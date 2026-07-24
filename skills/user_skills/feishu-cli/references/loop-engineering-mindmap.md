# Loop Engineering 思维导图 Mermaid 代码

## 推荐样式（带颜色分组）

```mermaid
mindmap
  root((Loop Engineering<br/>循环工程))
    基础概念
      以前写prompt让AI回答一次
      现在设计自动循环让AI自主干活
      核心从应答机升级为自动工人
    提出背景
      Peter Steinberg OpenCode创始人
      Boris Claude Code负责人
      Andy 谷歌工程师
    技术演进
      脚本期2025年5月
        while循环加管道符
        粗糙但能用
      Hook期
        StopHook拦截机制
        模型既是运动员又是裁判
      标准命令期
        Go命令统一驱动
        大模型干活小模型检查
    六大核心组件
      自动化让loop持续运转
      技能记忆不让AI重复理解规则
      MCP连接连接GitHub飞书数据库
      子代理分工一个干活一个检查
      环境隔离每个AI独立工作间
      状态记忆跨轮次不丢失上下文
    现实挑战
      不是消除复杂性是迁移复杂性
      token消耗大成本高
      安全边界尚未定义完善
```

## 渲染方式

### 在线渲染（mermaid.ink）
```python
import base64, requests

mermaid_code = '...'  # 上面完整代码
encoded = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
url = f"https://mermaid.ink/img/{encoded}"

resp = requests.get(url, timeout=30)
with open("output.png", "wb") as f:
    f.write(resp.content)
```

### 本地渲染（mmdc）
```bash
"C:\Users\Admin\AppData\Roaming\npm\mmdc.cmd" -i loop.mmd -o loop.png -b white -w 1920 -H 1080
```

## 注意事项
- `mermaid.ink` 可用，`kroki.io` 全部 404
- 图片插入飞书文档需用 user token 或让用户手动复制粘贴