import subprocess
import time

print("啟動 mcp-server")
mcp_proc = subprocess.Popen(["uv", "run", "mcp-server.py"])
time.sleep(10)

print("啟動網頁")
main_proc = subprocess.Popen(["uv", "run", "main.py"])

# 保持主程式運行
try:
    mcp_proc.wait()
    main_proc.wait()
except KeyboardInterrupt:
    print("接收到中斷指令，結束進程")
    mcp_proc.terminate()
    main_proc.terminate()
