# 逐行讀取
import asyncio

async def Reading_analyzing_content():
    # 逐行讀取
    result = []
    with open("test.srt", "r", encoding="utf-8") as file:
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