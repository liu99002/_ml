from moviepy import AudioFileClip
import math
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def split_video_by_duration(video_path="test.mp3", segment_duration=300):  # 300秒 = 5分鐘
    # 載入影片
    clip = AudioFileClip(video_path)
    total_duration = clip.duration
    clip.close()
    
    # 計算需要分割的片段數量
    num_segments = math.ceil(total_duration / segment_duration)
    
    def process_segment(i):
        start_time = i * segment_duration
        end_time = min((i + 1) * segment_duration, total_duration)
        output_filename = f"test_part_{i+1}.mp3"
        
        clip = AudioFileClip(video_path)
        subclip = clip.subclipped(start_time, end_time)
        subclip.write_audiofile(output_filename)
        clip.close()
        subclip.close()
        
        return output_filename

    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor(max_workers=num_segments) as executor:
        tasks = [
            loop.run_in_executor(executor, process_segment, i)
            for i in range(num_segments)
        ]
        
        results = await asyncio.gather(*tasks)
        
    print("所有片段處理完成:", results)
    return results
    
    
if __name__ == "__main__":
    # 使用範例
    asyncio.run(split_video_by_duration("test.mp3", 300))  # 5分鐘 = 300秒
