#!/usr/bin/env python3
"""三Agent编排助手：Hermes 调 OpenCode 和 Coze 的统一入口

用法：
  python agent_bridge.py opencode "<任务描述>"          # 调 OpenCode 写代码
  python agent_bridge.py coze code <projectId> "<消息>"  # 调 Coze 执行
  python agent_bridge.py coze deploy <projectId>         # 调 Coze 部署
  python agent_bridge.py status                          # 查看任务状态
  python agent_bridge.py acp-start                       # 启动 OpenCode ACP 服务
"""
import subprocess, json, os, sys, time, tempfile
from pathlib import Path

OPENCODE = "C:\\Users\\Admin\\AppData\\Roaming\\npm\\opencode.cmd"
COZE     = "C:\\Users\\Admin\\AppData\\Roaming\\npm\\coze.cmd"
WORKSPACE = "C:\\Users\\Admin\\AppData\\Local\\hermes\\workspace"

def run_opencode(task: str, timeout: int = 120):
    """调 OpenCode 执行编程任务"""
    print(f"[Bridge] 调 OpenCode: {task[:60]}...")
    
    # 写一个 prompt 文件，OpenCode 可以通过文件读取
    prompt_file = os.path.join(tempfile.gettempdir(), "hermes_prompt.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(task)
    
    # OpenCode 当前不支持直接传 prompt 做非交互式调用
    # 所以这里用 ACP 方式（启动临时 ACP 服务 + 发请求）
    # 或者直接启动 opencode TUI 在 pty 模式
    # 这里返回如何调用的提示给 Hermes
    print(f"[Bridge] 请使用: terminal('{OPENCODE} \"{task}\"', pty=True)")
    print(f"[Bridge] 或启动 ACP 服务后用 HTTP 发送任务")
    
    return {"status": "prompt", "message": f"请在 terminal(pty=true) 中运行: {OPENCODE} \"{task}\""}

def run_coze_command(action: str, project_id: str, message: str = "", timeout: int = 120):
    """调 Coze 执行操作"""
    if action == "send" and message:
        cmd = [COZE, "code", "message", "send", message, "-p", project_id]
    elif action == "deploy":
        cmd = [COZE, "code", "deploy", project_id]
    elif action == "list":
        cmd = [COZE, "code", "project", "list"]
    elif action == "create":
        cmd = [COZE, "code", "project", "create", "--message", message, "--type", "web"]
    elif action == "agent-send":
        cmd = [COZE, "agent", "message", "send", "--project-id", project_id, "--message", message] if message else []
    elif action == "file-upload":
        # coze agent file upload --project-id <id> --local-file-path <path> --project-dir <dir>
        parts = message.split("|")
        if len(parts) >= 2:
            cmd = [COZE, "agent", "file", "upload", "--project-id", project_id,
                   "--local-file-path", parts[0], "--project-dir", parts[1]]
        else:
            return {"status": "error", "message": "file-upload 格式: <本地路径>|<远端目录>"}
    else:
        return {"status": "error", "message": f"未知操作: {action}"}
    
    print(f"[Bridge] 调 Coze: {' '.join(cmd[:4])}...")
    start = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
    elapsed = time.time() - start
    print(f"[Bridge] Coze 返回 (耗时 {elapsed:.1f}s, rc={r.returncode})")
    
    return {
        "status": "ok" if r.returncode == 0 else "error",
        "stdout": r.stdout[:2000],
        "stderr": r.stderr[:500],
        "exit_code": r.returncode,
        "elapsed": round(elapsed, 1)
    }

def start_acp_server(port: int = 3100):
    """启动 OpenCode ACP 服务 (后台进程)"""
    cmd = f'start "OpenCode ACP" "{OPENCODE}" acp --port {port}'
    subprocess.run(cmd, shell=True)
    return {"status": "ok", "message": f"OpenCode ACP 服务已启动在 :{port}"}

def show_status():
    """查看当前配置状态"""
    print("=== 三Agent 状态 ===")
    
    # OpenCode
    r = subprocess.run([OPENCODE, "--version"], capture_output=True, text=True, timeout=10, shell=True)
    oc_ver = r.stdout.strip() or r.stderr.strip()
    
    # Coze
    r2 = subprocess.run([COZE, "--version"], capture_output=True, text=True, timeout=10, shell=True)
    cz_ver = r2.stdout.strip() or r2.stderr.strip()
    
    # Coze auth
    r3 = subprocess.run([COZE, "auth", "status"], capture_output=True, text=True, timeout=10, shell=True)
    
    print(f"  OpenCode: {oc_ver}")
    print(f"  Coze:     {cz_ver}")
    print(f"  Coze 登录: {'✅' if 'logged_in true' in r3.stdout else '❌'}")
    print(f"  Workspace: {WORKSPACE}")
    
    import re
    auth_ok = bool(re.search(r'logged_in\s+true', r3.stdout))
    return {"opencode": oc_ver, "coze": cz_ver, "auth_ok": auth_ok}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "opencode":
        if len(sys.argv) < 3:
            print("用法: agent_bridge.py opencode \"<任务描述>\"")
            sys.exit(1)
        result = run_opencode(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "coze":
        if len(sys.argv) < 3:
            print("用法: agent_bridge.py coze <action> [projectId] [message]")
            sys.exit(1)
        action = sys.argv[2]
        project_id = sys.argv[3] if len(sys.argv) > 3 else ""
        message = sys.argv[4] if len(sys.argv) > 4 else ""
        result = run_coze_command(action, project_id, message)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "acp-start":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 3100
        result = start_acp_server(port)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "status":
        show_status()
    
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)