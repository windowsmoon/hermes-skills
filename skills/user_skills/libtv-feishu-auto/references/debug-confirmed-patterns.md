# LibTV × 飞书自动化 — 调试确认记录

> 本次会话中发现的真实 Bug 及修复，已固化进 scripts/generate.py。

---

## 已确认工作的完整链路

### 生图任务（生成角色卡，image2image）
```
读取飞书记录 → 上传图片附件为资源节点 → libtv node create（无--run）
→ libtv node newNodeKey --run → 解析 url → 写回 图片URL + 状态=完成
```
总耗时：~90 秒（含模型推理）

### 生视频任务（生成视频片段，mixed2video）
```
读取飞书记录 → 上传图片+音频附件为资源节点 → libtv node create（无--run）
→ libtv node newNodeKey --run → 解析 url（数组，取[0]）→ 写回 视频URL + 状态=完成
```
总耗时：~225 秒（含模型推理）

---

## 关键 Bug 修复清单（时间线）

| # | 发现日期 | 问题现象 | 根本原因 | 修复 |
|---|---|---|---|---|
| 1 | 2026-07-07 | 状态=待处理的记录也被跳过 | STATUS 常量写反了（optuWxL8aA=完成，实际=待处理） | STATUS 值改为中文文本：待处理/完成/失败 |
| 2 | 2026-07-07 | 节点名固定（视频-001），重复执行冲突 | 节点名无后缀，重复运行报错 | 加 uuid 后缀 |
| 3 | 2026-07-07 | libtv upload 成功但 nodeKey 解析为 None | stdout 是多行格式化 JSON，按行 split 后 json.loads 失败 | 改为整体 json.loads(stdout.strip()) |
| 4 | 2026-07-07 | node create --run 立即返回，不等生成完成 | 文档说的行为与实际不符 | 拆成两步：先 node create（无--run），再 node newNodeKey --run |
| 5 | 2026-07-07 | 第二步 --run 的 stdout 解析失败 | stdout 是多行格式化 JSON，按行 split 后每行都是不完整的 JSON | 改为 compact = join(stdout.split()) 后整体解析 |
| 6 | 2026-07-07 | 飞书 download URL 返回 400 | 直接 urlretrieve 不带认证 | 用 urllib.request.Request(url, headers={Authorization: Bearer token}) |
| 7 | 2026-07-07 | 写视频URL 报 URLFieldConvFail | 用了纯字符串 | 必须 {"link": url, "text": url} |
| 8 | 2026-07-07 | 写视频附件字段报 AttachFieldConvFail | 附件字段需要 file_token，LibTV 生成结果没有 | 去掉附件写回，只写视频URL 字段 |
| 9 | 2026-07-07 | 画布上多个同名节点，用户网页版看到旧图，飞书写回的却是新节点 URL | 每次加 uuid 后缀，同记录重复运行创建多个节点 | 节点名改为图片-{task_key}-{record_id[:8]}（固定前缀）；同名节点已存在时先删除再重建 |
| 10 | 2026-07-08 | 新节点用了错误的参考图，生成结果完全不对（内容与飞书附件不符） | 资源节点用显示名 `素材-图-001-1`，`--left "素材-图-001-1"` 匹配到了旧的空同名节点（nodeKey=None）而不是刚上传的有图节点；同名资源节点重复上传时 display name 查询行为不稳定 | ① 资源节点名改为 REF-{record_id[:8]}-{task_key}-{i+1} ② 连线必须用 lefts = resource_node_keys（传 nodeKey UUID），不能用 lefts = resource_nodes（传显示名） |
| 11 | 2026-07-08 | 第二次运行，图片节点的参考图变成了旧节点 | `--left` 传显示名时，LibTV 对同名多节点取第一个（可能不是刚上传的那个） | 必须用 nodeKey UUID 连线，参考图 url hash 与飞书附件 hash 一致 |
| 12 | 2026-07-08 | 旧 `素材-图-001-X` 节点里的图不是飞书附件，而是旧的测试图（hash 不同） | 之前某次运行的资源节点也叫 `素材-图-001-1`，内容是另一张图 | 资源节点不再重复使用历史命名，每次用新的 record_id 前缀区分 |

---

## 飞书 API 字段类型与写回格式

| 字段类型 | UI Type | 写回格式 |
|---|---|---|
| 单行文本 | Text | 字符串 "value" |
| URL 链接 | Url | {"link": "url", "text": "显示文本"} |
| 附件 | Attachment | 无法通过 URL 写入，需要 file_token（LibTV 生成结果无 file_token） |
| 单选 | SingleSelect | 直接字符串，如 "完成"（多维表格已删 option_id） |

---

## LibTV CLI 行为实测确认

| 操作 | 实际行为 |
|---|---|
| libtv node create --run | 不等待生成，立即返回 newNodeKey |
| libtv node name --run | 阻塞等待生成完成，stdout 输出终态 JSON |
| libtv upload stdout | 多行格式化 JSON，不要按行 split |
| libtv node create stdout | 多行格式化 JSON，整体 json.loads |
| libtv node --run stdout | 多行格式化 JSON，去掉换行后 json.loads |
| 生成结果 url（视频） | data["data"]["url"] 是数组 |
| 生成结果 url（图片） | data["data"]["url"] 是字符串 |
| --left 传 nodeKey UUID | 可以正确连接节点 |
| --left 传显示名（同名多个节点） | 不稳定，可能匹配到错误的节点 |
| libtv node 查询 display name（同名多个） | 可能返回 nodeKey=None（空节点） |