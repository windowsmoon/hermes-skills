# 飞书 docx 图片插入根因分析（2026-07-20 完整版）

## 背景

将图片插入飞书文档需要两步：
1. 上传图片 → 拿到 `file_token`
2. 用 `file_token` 在 docx 文档中创建 image block

曾经尝试直接 REST API（失败），最终用 lark-cli 成功。

---

## ❌ 直接 REST API：全部失败

### 上传成功
- `drive/v1/medias/upload_all` ✅ 成功，返回 `file_token`
- 参数：`parent_type=docx_image`, `parent_node=doc_id`

### 插入失败（所有格式）
| 格式 | 结果 |
|------|------|
| `{block_type:17, image:{token, width, height}}` | 1770001 invalid param |
| `{block_type:17, image:{token}}` | 1770001 |
| `{block_type:31, file:{token, name:"xxx.png"}}` | 1770001 |
| 插入到 block 子节点而非 document root | 1770001 |
| 先插空文本块再插入 image block | 1770001 |

**所有格式不受影响，全部返回 1770001。**

核心结论：**飞书 docx 直接 REST API 不支持 block_type 17（图片）和 block_type 31（文件）的创建。** 
这与 block_type 3/4/5（标题）的行为一致——某些 block type 在直接 API 下不可创建，必须通过 lark-cli 或飞书 SDK。

---

## ✅ lark-cli docs +media-insert：成功（有坑）

`lark-cli` 的 `+media-insert` 命令是**正确的图片插入方式**。它内部执行了 4 步编排：
1. 在文档末尾创建空 block
2. 上传图片到飞书
3. 绑定 file_token 到 block
4. 回填图片尺寸和格式

### 命令格式

```bash
lark-cli docs +media-insert \
  --doc <doc_id> \
  --file <相对路径图片文件> \
  --align center \
  --width 800 \
  --caption "标题说明" \
  --as <bot|user>
```

### ⚠️ 关键限制

1. **`--file` 必须是相对路径**（在当前工作目录下），绝对路径会报 `unsafe file path`。正确做法：
   ```python
   import shutil
   shutil.copy2("原始路径/图片.png", "相对路径/图片.png")  # 复制到 cwd
   # 然后 --file "图片.png"
   ```

2. **`--as bot` vs `--as user` 取决于文档主人**
   - 如果文档是用 `tenant_access_token`（bot 身份）创建的 → 用 `--as bot`
   - 如果文档是用 `user_access_token`（用户身份）创建的 → 用 `--as user`
   - 用错身份返回 `1770032 forBidden`（无权操作）

3. **需要对应身份已授权**
   - `--as bot` → bot identity ready（自动，无需扫码）
   - `--as user` → 需要 `user_access_token`（需 OAuth 扫码）

4. **🔴 `--as bot` + `--selection-with-ellipsis` = invalid token（已验证 v1.0.48 & v1.0.73，更新未修复）**
   - **现象：** 文本定位阶段返回 `code=-32602, message="invalid token"`。去掉 selection 直接 append 就成功。
   - **根因：** bot 身份做文本定位时走了不同的内部认证通道，该通道 token 格式不被接受。append 模式不走定位通道。
   - **最终结论：放末尾即可。**
     `--as bot` + `--selection-with-ellipsis` 报 invalid token（无法定位插入）。
     流程统一为：建文档 -> 写文字 -> `lark-cli --as bot` append图片到末尾

### 场景对照表

| 文档创建方式 | 插入图片用 | 说明 |
|-------------|-----------|------|
| tenant_access_token（bot） | `--as bot` | 可自动执行，无需扫码 |
| lark-cli（user） | `--as user` | 需要 OAuth 扫码授权 |

**默认走 bot 身份即可**，只要文档是 bot 创建的。bot 身份始终可用（`auth/status --verify` 显示 bot.available=true）。

---

## 对比：为什么不要用直接 REST API

| 方式 | 图片插入 | 文本写入 | 需要 |
|------|---------|---------|------|
| 直接 REST API | ❌ block_type=17 全部失败 | ✅ block_type=2 正常 | tenant_access_token |
| lark-cli +media-insert（append末尾） | ✅ bot/user 皆可 | ✅ 支持 | bot 或 user token |
| lark-cli +media-insert（定位插入） | ⚠️ **仅 user**，bot报invalid token | ✅ 支持 | user token |

**推荐组合：**
- **文本写入** → 直接 REST API（fast，无依赖）
- **图片插入** → lark-cli `+media-insert --as bot` 追加到末尾
- **图片放顶部** → 先 `--as bot` append 图片，再写文字（文字在图片下方）
