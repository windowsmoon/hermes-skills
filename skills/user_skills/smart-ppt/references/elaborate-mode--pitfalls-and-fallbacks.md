# Smart PPT — 精装模式工作流与已知问题

## 精装模式完整流程

```
文多多生成大纲（SSE 流式）
  ↓
问用户：简单还是精装？
  ├─ 简单 → 文多多走完6步 → PPT下载链接
  └─ 精装 →
       ├─ 用 `import_file` 传入大纲MD文件到ChatPPT
       │   （不要用 `generate` 传长文本：主题字段 ≤200字限制）
       │   ├─ 成功 → 文件上传→轮询→下载PPT
       │   └─ code=11500(额度用完) → 自动降级
       │
       └─ 降级链路（按优先级）：
            1. GordenPPTSkill（~Developer/GordenPPTSkill/）
            2. HTML 演示（frontend-design + uiux-slides）
```

## 已知问题 & 应对

### 1. ChatPPT `generate` 主题文本 ≤200 字限制
- **现象**：`字段[text]: text长度必须在1-200字符之间`
- **原因**：`chatppt ppt generate` 的主题字段硬性限制 200 字符
- **应对**：涉及长文本/大纲 → 用 `import_file` 替代 `generate`
  ```bash
  chatppt ppt import_file --file-path outline.md --custom-template-id xxx --poll
  ```

### 2. ChatPPT `--ai-picture` 是 boolean flag，不传值
- **正确用法**：`--ai-picture`（不加 true/false）
- **错误**：`--ai-picture true` → 报错 `unknown command "true"`

### 3. GordenPPTSkill edits.json 正确格式
```json
{
  "template_slug": "architecture-deck",
  "selected_slides": [1, 2, 5, 10, 15, 20],
  "edits": [
    {"slide": 1, "slot_id": "s1_sh8_p0r0", "new_text": "新标题"}
  ]
}
```
- ⚠️ 不是 `"slides"` 数组，是 `"selected_slides"` + `"edits"` 
- 每个 edit 的 `"slide"` 是 1-indexed
- 用 `--detail detail.json` 查看全部可用的 slot_id

### 4. AiPPT / 文多多 SSE 流式输出
- 生成大纲和内容的 API 使用 SSE (Server-Sent Events)，不是标准 JSON
- 需要逐行读取 `data:` 前缀的行，拼装成完整文本
- 示例解析逻辑（Python）：
  ```python
  resp = urllib.request.urlopen(req)
  text = ""
  while True:
      line = resp.readline()
      if not line: break
      if line.startswith(b"data:"):
          d = json.loads(line[5:])
          if "text" in d: text += d["text"]
  ```

### 5. HTML 演示（零成本模式）参数轮询
当走 HTML 演示模式时，按顺序问用户 8 个选择题：
1. 配色风格（科技蓝/赛博朋克/极简白/暖色调/渐变风/自定义）
2. 字体（默认/手写感/宋体/无衬线/自定义）
3. 页数（5-6/8-10/12-15/自定义）
4. 布局模式（数据看板/功能网格/双栏对比/时间线/案例展示）
5. 动画效果（流畅/滑动/干脆/炫酷）
6. 图表类型（柱状图/环形图/折线图/雷达图/不需要）
7. 文案风格（专业严谨/轻松易懂/激情感染力/数据驱动）
8. 结尾（联系方式/下一步计划/Q&A/感谢/试用邀请）

每项都给 4-6 个选项 + 默认值，用户选数字或说"默认"跳过。
