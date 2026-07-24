# Windows 文件操作编码问题 workaround

## 问题

在 Windows git-bash/MSYS 环境下，`terminal` 工具和 `write_file` 工具可能因编码问题失败：
- `terminal` 输出显示为 `�` 乱码
- `write_file` 返回 `Failed to write file` 错误
- `read_file` 对某些路径也可能失败

## Workaround：使用 Hermes Studio API

当本地文件工具失败时，使用 Web UI API 作为替代：

### 读取文件
```bash
GET /api/hermes/files/read?path=C:\Users\Admin\AppData\Local\hermes\memories\MEMORY.md
```

### 写入文件
```bash
PUT /api/hermes/files/write
Content-Type: application/json

{
  "path": "C:\\Users\\Admin\\AppData\\Local\\hermes\\memories\\MEMORY.md",
  "content": "文件内容..."
}
```

### 列出目录
```bash
GET /api/hermes/files/list?path=C:\Users\Admin\AppData\Local\hermes\memories
```

### 获取文件状态
```bash
GET /api/hermes/files/stat?path=C:\Users\Admin\AppData\Local\hermes\memories\MEMORY.md
```

## 注意事项

- API 路径使用 Windows 反斜杠 `\`，需要对 `\` 进行转义（`\\`）
- 大文件（33KB+）通过 API 传输没问题
- API 返回的 content 字段包含完整文件内容
- 写入时 content 字段需要是转义后的字符串

## 适用场景

- `write_file` 工具因编码问题失败
- `terminal` 工具输出乱码无法解析
- 需要读写 `AppData/Local/hermes/` 下的配置文件
- 批量文件操作（API 调用可并行）
