# 網頁使用 Claude產生 
* [main.py](https://github.com/liu99002/_ml/blob/main/hw/fin/main.py)
> fastapi、WebSocket由Claude產生
>[與AI對話連結](https://www.perplexity.ai/search/zhe-shi-wo-kai-fa-de-yi-ge-ji-PNdI35jdTeSgrDWppyL_GA)
> Agent搭建如下列所示

# Agent、MCP參考網路上資料後為自行完成
* [Langgraph_Agent.ipynb](https://github.com/liu99002/_ml/blob/main/hw/fin/Langgraph_Agent.ipynb)
    > Agent 主程式
    > 參考資料: 
    > 1. [AsyncMongoDBSaver](https://langchain-mongodb.readthedocs.io/en/latest/langgraph_checkpoint_mongodb/aio/langgraph.checkpoint.mongodb.aio.AsyncMongoDBSaver.html#langgraph.checkpoint.mongodb.aio.AsyncMongoDBSaver)
    > 2. [create_react_agent](https://langchain-ai.github.io/langgraph/agents/agents/#1-install-dependencies)
    > 3. [Day 18: langchain 由入門到熟練(建立 Agent-使用Open AI -API)](https://ithelp.ithome.com.tw/articles/10345369)

* [mcp-server.py](https://github.com/liu99002/_ml/blob/main/hw/fin/mcp-server.py)
    > MCP Server 主程式
    > 集成下列工具給Agent
    > 參考資料: 
    > 1. [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
    > 2. [FastMCP v2](https://github.com/jlowin/fastmcp)
    > 3. [FastMCP 文檔](https://gofastmcp.com/getting-started/welcome)


* [download.py](https://github.com/liu99002/_ml/blob/main/hw/fin/download.py)
    >下載影片

* [movie_cut.py](https://github.com/liu99002/_ml/blob/main/hw/fin/movie_cut.py)
    > 音檔剪輯
    > 參考資料: [使用 moviepy 取出影片聲音，儲存為 mp3](https://steam.oxxostudio.tw/category/python/example/video-audio.html)

* [Whisper.py](https://github.com/liu99002/_ml/blob/main/hw/fin/Whisper.py)
    > 產生字幕檔
    > 參考資料: [Faster-Whisper 免费开源的高性能语音识别模型](https://techdiylife.github.io/blog/blog.html?category1=c02&blogid=0021)、范揚玄同學協助

# 使用方法
'python app.py'
