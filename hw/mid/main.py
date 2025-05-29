from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
import motor.motor_asyncio
from contextlib import asynccontextmanager

# 導入你現有的代碼
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from langmem.short_term import SummarizationNode
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.messages.utils import count_tokens_approximately
from typing import Any

load_dotenv()

# 環境變數
api_key = os.getenv("GOOGLE_API_KEY")
Mongo_url = os.getenv("MONGO_URI")
Database_Name = os.getenv("Database_Name")
Collection_Name = os.getenv("Collection_Name")

# 全局變量
tools = None
agent = None
checkpointer = None
checkpointer_cm = None

# 資料模型
class ChatMessage(BaseModel):
    message: str
    session_id: str

class ChatHistory(BaseModel):
    session_id: str
    messages: List[dict]
    created_at: datetime
    updated_at: datetime

class ChatSession(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    last_message: Optional[str] = None

# MongoDB 連接管理
class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.chat_collection = None
        self.history_collection = None
    
    async def connect(self):
        """建立 MongoDB 連接"""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(Mongo_url)
        self.db = self.client[Database_Name]
        self.chat_collection = self.db["chat_sessions"]
        self.history_collection = self.db["chat_history"]
        
        # 測試連接
        try:
            await self.client.admin.command('ping')
            print("MongoDB 連接成功!")
        except Exception as e:
            print(f"MongoDB 連接失敗: {e}")
            raise
    
    async def close(self):
        """關閉 MongoDB 連接"""
        if self.client:
            self.client.close()

# 創建全局數據庫管理器
db_manager = DatabaseManager()

# 初始化 MCP 客戶端和模型
async def init_mcp_client():
    client = MultiServerMCPClient({
        "eveng": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:4200/my-custom-path/"
        }
    })
    tools = await client.get_tools()
    return tools

# 初始化 LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    temperature=1.0,
    max_retries=2,
    google_api_key=api_key,
)

# 應用生命週期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理應用生命週期"""
    global tools, agent, checkpointer, checkpointer_cm
    
    try:
        # 連接數據庫
        await db_manager.connect()
        
        # 初始化 MCP 工具
        tools = await init_mcp_client()
        model = llm.bind_tools(tools)
        
        # 正確創建 checkpointer
        checkpointer_cm = AsyncMongoDBSaver.from_conn_string(Mongo_url)
        checkpointer = await checkpointer_cm.__aenter__()
        
        # 創建摘要節點
        summarization_node = SummarizationNode(
            token_counter=count_tokens_approximately,
            model=model,
            max_tokens=1000000,
            max_summary_tokens=2048,
            max_tokens_before_summary=80000,
            output_messages_key="llm_input_messages",
        )
        
        # 定義狀態模式
        class State(AgentState):
            context: dict[str, Any]
        
        # 創建代理
        agent = create_react_agent(
            model=model,
            tools=tools,
            checkpointer=checkpointer,
            pre_model_hook=summarization_node,
            state_schema=State,
            prompt="""當用戶請你幫忙解析影片時，請使用download(MCP tool)下載影片，
                    當影片超過300秒(5分鐘)時使用audio_cut(MCP tool)依每5分鐘的長度分割成多個片段，
                    再使用whisper_tool(MCP tool)產生字幕檔並根據回傳的文字進行影片內容解析，請用繁體中文回答，
                    切記在使用MCP工具時一定要先詢問我並告知你預計傳入的參數"""
        )
        
        print("應用初始化成功")
        
        # 讓應用運行
        yield
        
    except Exception as e:
        print(f"初始化失敗: {e}")
        raise
    
    finally:
        # 清理資源
        try:
            # 關閉數據庫連接
            await db_manager.close()
            
            # 正確關閉 checkpointer
            if checkpointer_cm:
                await checkpointer_cm.__aexit__(None, None, None)
                
            print("應用清理完成")
        except Exception as e:
            print(f"清理過程發生錯誤: {e}")

# 創建 FastAPI 應用
app = FastAPI(
    title="聊天助手", 
    description="基於 LangGraph 的聊天助手 Web 介面",
    lifespan=lifespan
)

# CORS 設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態文件服務
app.mount("/static", StaticFiles(directory="static"), name="static")

# API 端點
@app.get("/", response_class=HTMLResponse)
async def get_chat_page():
    """返回聊天介面 HTML 頁面"""
    with open("static/chat.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/sessions")
async def get_chat_sessions():
    """獲取所有聊天會話"""
    try:
        sessions = await db_manager.chat_collection.find().sort("created_at", -1).to_list(100)
        for session in sessions:
            session["_id"] = str(session["_id"])
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """獲取特定會話的聊天歷史"""
    try:
        history = await db_manager.history_collection.find_one({"session_id": session_id})
        if history:
            history["_id"] = str(history["_id"])
            return history
        return {"session_id": session_id, "messages": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions")
async def create_session():
    """創建新的聊天會話"""
    try:
        import uuid
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session_data = {
            "session_id": session_id,
            "title": "新對話",
            "created_at": now,
            "last_message": None
        }
        
        await db_manager.chat_collection.insert_one(session_data)
        session_data["_id"] = str(session_data["_id"])
        
        return {"session": session_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """刪除聊天會話"""
    try:
        await db_manager.chat_collection.delete_one({"session_id": session_id})
        await db_manager.history_collection.delete_one({"session_id": session_id})
        return {"message": "會話已刪除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket 連接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 聊天端點"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # 接收用戶消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message.strip():
                continue
                
            # 保存用戶消息
            await save_message(session_id, "user", user_message)
            
            # 更新會話信息
            await update_session_last_message(session_id, user_message)
            
            # 發送用戶消息確認
            await manager.send_message(json.dumps({
                "type": "user_message",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            }), session_id)
            
            # 獲取 AI 回應
            if agent:
                try:
                    # 發送正在輸入指示器
                    await manager.send_message(json.dumps({
                        "type": "typing",
                        "content": "AI 正在思考..."
                    }), session_id)
                    
                    config = {
                        "configurable": {
                            "thread_id": session_id
                        }
                    }
                    
                    # 調用 agent
                    events = agent.astream(
                        {"messages": user_message},
                        config,
                        stream_mode="values",
                    )
                    
                    ai_response = ""
                    async for event in events:
                        if event.get("messages"):
                            last_message = event["messages"][-1]
                            if hasattr(last_message, 'content'):
                                ai_response = last_message.content
                    
                    # 保存 AI 回應
                    await save_message(session_id, "assistant", ai_response)
                    
                    # 發送 AI 回應
                    await manager.send_message(json.dumps({
                        "type": "ai_message", 
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    }), session_id)
                    
                except Exception as e:
                    error_msg = f"處理消息時發生錯誤: {str(e)}"
                    print(f"Agent 錯誤詳情: {e}")
                    await manager.send_message(json.dumps({
                        "type": "error",
                        "content": error_msg
                    }), session_id)
            else:
                await manager.send_message(json.dumps({
                    "type": "error",
                    "content": "AI 代理未初始化"
                }), session_id)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket 錯誤: {e}")
        manager.disconnect(session_id)

async def save_message(session_id: str, role: str, content: str):
    """保存消息到數據庫"""
    try:
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        }
        
        # 查找現有歷史記錄
        history = await db_manager.history_collection.find_one({"session_id": session_id})
        
        if history:
            # 更新現有記錄
            await db_manager.history_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.now()}
                }
            )
        else:
            # 創建新記錄
            new_history = {
                "session_id": session_id,
                "messages": [message],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            await db_manager.history_collection.insert_one(new_history)
    except Exception as e:
        print(f"保存消息錯誤: {e}")

async def update_session_last_message(session_id: str, message: str):
    """更新會話的最後消息"""
    try:
        # 截斷過長的消息作為預覽
        preview = message[:50] + "..." if len(message) > 50 else message
        
        await db_manager.chat_collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "last_message": preview,
                    "updated_at": datetime.now()
                }
            }
        )
        
        # 如果是第一條消息，更新會話標題
        session = await db_manager.chat_collection.find_one({"session_id": session_id})
        if session and session.get("title") == "新對話":
            title = message[:30] + "..." if len(message) > 30 else message
            await db_manager.chat_collection.update_one(
                {"session_id": session_id},
                {"$set": {"title": title}}
            )
    except Exception as e:
        print(f"更新會話錯誤: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
