import os, time, asyncio
from faster_whisper import WhisperModel
from opencc import OpenCC

async def whisper_video(video_path:str):
    """
    產生影片字幕檔
    """
    os.environ['KMP_DUPLICATE_LIB_OK']='True'

    file_name = video_path 

    os.environ["PATH"] += os.environ["PATH"] \
        +  ";" +  r".\.venv\Lib\site-packages\nvidia\cublas\bin" \
        +  ";" +  r".\.venv\Lib\site-packages\nvidia\cudnn\bin"

    start_time = time.time()

    model_size = "large-v3"

    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    print(f"Model load: {time.time()-start_time} s")

    start_time = time.time()
    segments, info = model.transcribe(file_name, beam_size=5,vad_filter=True,word_timestamps=True)

    subtitles=[]
    for segment in segments:
        text = OpenCC('s2twp').convert(segment.text)
        subtitles.append((float(format(segment.start,'.2f')), float(format(segment.end,'.2f')),text))
        print((float(format(segment.start,'.2f')), float(format(segment.end,'.2f')),text))

    def format_time(milliseconds):
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    srt_content = ""
    count = 1
    for subtitle in subtitles:
        start_time = int(subtitle[0] * 1000)
        end_time = int(subtitle[1] * 1000)
        srt_content += f"{count}\n"
        srt_content += f"{format_time(start_time)} --> {format_time(end_time)}\n"
        srt_content += f"{subtitle[2]}\n\n"
        count += 1

    cnt=1
    while 1:
        output_file = f"{file_name}{cnt}.srt"
        if not os.path.exists(output_file):
            with open(f"{file_name}.srt" if cnt == 1 else f"{file_name}{cnt}.srt", "w", encoding="utf-8") as file:
                file.write(srt_content)
            break
        cnt+=1

    return video_path