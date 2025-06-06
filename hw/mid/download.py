from pytubefix import YouTube
import asyncio

async def download_youtube_video(url):
    yt = YouTube(url)
    video_length_seconds = yt.length
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(filename="test.mp3")
    print(f"下載完成: {yt.title} 長度: {video_length_seconds}")
    return f"影片長度為: {video_length_seconds}秒"

if __name__ == "__main__":
    video_url = input()
    asyncio.run(download_youtube_video(video_url))
