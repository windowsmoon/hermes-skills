# ChatPPT CLI 已知问题与规避

## 1. 主题文本 200 字符限制

`chatppt ppt generate` 的 `text` 参数限制 1-200 字符。
超长会返回：`字段[text]: text长度必须在1-200字符之间`

**解决：** 用 `import_file` 替代，把长文本或大纲存为 .md 文件传入。

## 2. Boolean flag 不加值

`--ai-picture` 是 boolean flag，不是 string flag：
```bash
# ❌ 错误
chatppt ppt import_file --ai-picture true

# ✅ 正确
chatppt ppt import_file --ai-picture
```

## 3. 免费额度用完

返回 `code=11500, "用户权益已用完"`。
此时无法继续使用 ChatPPT，需降级到 GordenPPTSkill。

## 4. JSON 输出混杂在 log 中

`-o json` 的 JSON 输出前面有多行 log 前缀：
```
[配置] 使用嵌入的配置文件
正在获取PPT模板列表...
{ "code": 200, "data": {...} }
```

**解决：** 逐行扫描，取第一行以 `{` 开头的行做 json.loads。

## 5. 二进制包结构

`@yooai/cli` 的 chatppt 命令是一个 Go 二进制文件：
- 入口：`script/run.js` 查找 `bin/chatppt.exe`
- 如果 postinstall 被跳过（npm 配置了 `ignore-scripts`），二进制不会下载
- **解决：** 手动运行 `node script/install.js` 或 `npm approve-scripts @yooai/cli`

## 6. --font-name 需系统已安装

指定 `--font-name` 时，字体必须在系统中已安装。
如果字体不存在，ChatPPT 会使用默认字体，不会报错但可能不符合预期。
