# ChatPPT CLI (@yooai/cli v1.2.4) 参考

## 安装位置
```
C:\Users\Admin\AppData\Roaming\npm\node_modules\@yooai\cli\bin\chatppt.exe
```

## 登录状态
- 用户: windowsm（手机 13450377820）
- Token 保存: ~/.chatppt/credentials.json
- 登录命令: `chatppt auth login`（设备码 OAuth 流程）

## 常用命令

### 模板查询
```bash
chatppt ppt template --page 1 --limit 50 -o json
```
79 个模板，支持按风格筛选（商务风/科技风/卡通风/现代风等）

### 生成 PPT
```bash
chatppt ppt generate "<主题>" \
  --custom-template-id <ID> \
  --language zh-CN \
  --custom-page-count 10 \
  --ai-picture true \
  --font-name "微软雅黑" \
  --image-style "商务" \
  --poll
```

### 文件导入
```bash
chatppt ppt import_file \
  --file-path ./report.docx \
  --custom-template-id <ID> \
  --language zh-CN \
  --poll
```
支持: .doc/.docx/.pdf/.md/.txt（最大 100MB）

## 参数速查

| 参数 | 类型 | 说明 |
|------|------|------|
| `--custom-template-id` | string | 模板ID（从 template 命令获取） |
| `--language` | string | zh-CN / en-US |
| `--ai-picture` | bool | AI配图（默认 true） |
| `--custom-page-count` | int | 页数 |
| `--font-name` | string | 字体 |
| `--image-style` | string | 图片风格 |
| `--complex` | int | 复杂度 |
| `--poll` | bool | 启用轮询等待 |
| `--file-path` | string | 文件导入路径 |
| `-o` | string | json/pretty/table |
