# server.py
# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP, Context
import sys
from pydantic import BaseModel
from typing import List
import traceback
import logging
import asyncio
import uvicorn
from faster_whisper import WhisperModel
from opencc import OpenCC
import os, time

# 設定基本記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create an MCP server
mcp = FastMCP(name="Demo")

# 檢查導入是否正常
try:
    from download import download_youtube_video
    from Whisper import whisper_video
    from movie_cut import split_video_by_duration
    logging.info("Successfully imported EvengTool modules.")
except ImportError as e:
    logging.error(f"ERROR: Failed to import EvengTool modules: {e}")
    logging.error("Please ensure MCP-Server.py is in the correct directory relative to EvengTool or adjust sys.path.")
except Exception as e:
    logging.error(f"An unexpected error occurred during import: {e}")

@mcp.tool()
async def download(video_url) -> str:
    """
    下載 YouTube 影片的音頻

    Args:
        video_url (str): YouTube 影片的網址

    return:
        str: 影片長度的描述字串，格式為 "影片長度為: XXX秒"
    """
    logging.info("Starting download execution.")
    try:
        result = await download_youtube_video(video_url)
        return result
    except Exception as e:
        logging.error(f"Failed to initialize lab: {e}", exc_info=True)
        return None
    
@mcp.tool()
async def audio_cut() -> list[str]:
    """
    將超過300秒(5分鐘)的音頻檔案依每5分鐘的長度分割成多個片段

    回傳:
        list[str]: 分割後的音頻片段檔案名稱清單，格式為 ["test_part_1.mp3", "test_part_2.mp3", ...]
    """
    logging.info("Attempting to initialize lab...")
    try:
        result = await split_video_by_duration()
        logging.info("Lab instance created successfully.")
        return result
    except Exception as e:
        logging.error(f"Failed to initialize lab: {e}", exc_info=True)
        return None
    
@mcp.tool()
async def whisper_tool(audio_paths: list[str] ,ctx:Context):
    """
    將傳入需要進行Whisper模型產生字幕的音頻，讀取並回傳所有音頻內容

    Args:
        - audio_paths: 待處理的音頻檔案路徑清單，格式為["test_part_1.mp3", "test_part_2.mp3", ...]
        - ctx: 上下文物件，用於回報處理進度
    Return:
        list[str]: 將所有讀取到的字幕回傳
    """
    logging.info("Starting whisper_tool execution.")
    try:
        result = []
        counter = 1
        for audio_path in audio_paths:
            await whisper_video(audio_path)
            result.append(await Reading_analyzing_content(audio_path))
            time.sleep(0.5)
            await ctx.report_progress(progress=counter, total=len(audio_paths))
            counter += 1
        return result
    except Exception as e:
        logging.error(f"Failed to initialize lab: {e}", exc_info=True)
        return None
    
async def Reading_analyzing_content(file_name: str):
    # 逐行讀取
    result = []
    with open(f"{file_name}.srt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        count = 1
        for line in lines:
            if count%4 == 1 :
                count += 1
                continue
            if line == "\n":
                count += 1
                continue
            if "-->" in line:
                count += 1
                continue

            result.append(line.strip())
            print(line.strip())
            count += 1
    return result

@mcp.tool()
async def Reading_analyzing_content_tool():
    """
    讀取並回傳影片字幕檔
    """
    try:
        result = await Reading_analyzing_content()
        return result
    except Exception as e:
        logging.error(f"Failed to initialize lab: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=4200,
        path="/my-custom-path",
        log_level="debug",
    )
