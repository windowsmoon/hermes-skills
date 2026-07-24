---
name: buyin-harvester
description: >
  当用户需要采集巨量百应（buyin.jinritemai.com）的爆款视频数据时使用。
  通过Tabbit Browser控制浏览器自动翻页采集，解析视频标题、播放量、销售额等。
  不要用于：非巨量百应的电商平台、抖音App内数据采集、数据分析报告。
  触发词：巨量百应、爆款视频、采集抖音数据、buyin、电商数据采集
triggers:
  - 采集巨量百应
  - 巨量百应采集
  - buyin harvest
  - 爆款视频采集
  - 帮我从巨量百应拿数据
  - 收割巨量百应
version: 1
tags:
  - buyin-harvester
  - buyin

---

# Buyin Harvester — 巨量百应爆款视频采集

## 能力边界

- **浏览器控制**：Tabbit Browser MCP（控制用户本地Edge，含反检测）
- **视觉理解**：vision_analyze 分析截图，判断页面状态（有无数据、是否到底、异常检测）
- **数据提取**：tabbit_extract(type="text") + Python解析（已验证可行）
- **飞书写入**：Feishu Open API tenant_access_token 模式，batch_create批量写入
- **目标数据**：博主名称 / 发布时间 / 视频时长 / 视频摘要(商品名) / 总播放量 / 新增播放量 / 已选类目结算金额 / 总点赞量
- **目标量**：默认50条，可通过参数调整

## 架构概览

```
你登录浏览器 ──→ Tabbit Browser 控制Edge ──→ 我(Agent) 编排循环
                                                      │
                          ┌─────────────────────────────┤
                          ▼                             ▼
                   tabbit_screenshot              tabbit_extract(text)
                          ↓                             ↓
                   vision_analyze                 Python parser.py
                   (判断状态)                       (解析结构化记录)
                          │                             │
                          └───────── 循环直到50条 ───────┘
                                          ↓
                                    feishu_writer.py
                                    (批量写入飞书)
```

## 工具依赖

| 工具 | 用途 | 命令示例 |
|------|------|---------|
| tabbit_navigate | 导航到URL | tabbit_navigate(url, waitForLoad=5000, humanBrowse=true) |
| tabbit_antidetect | 注入反检测脚本 | tabbit_antidetect() |
| tabbit_screenshot | 截图 → vision分析 | tabbit_screenshot() |
| tabbit_input | 滚动、键盘操作 | tabbit_input(action="scroll", direction="down") |
| tabbit_extract | 提取页面文本 | tabbit_extract(type="text") |
| tabbit_element | 等待元素、智能点击 | tabbit_element(action="wait", locator={selector: "..."}) |
| tabbit_readability | 备用数据提取 | tabbit_readability(maxLength=20000) |
| vision_analyze | 截图视觉分析 | vision_analyze(image_url, question="页面状态？") |

## 六阶段执行流程

### Phase 0: 前置准备（用户一次性操作）
1. 打开 Edge 浏览器，登录巨量百应
2. 导航到爆款视频页：https://buyin.jinritemai.com/dashboard/inspiration-center/hot-video
3. 设置筛选条件（如果不需要默认值）
4. 通知 Agent "已就绪"

### Phase 1: Agent 初始化
1. Tabbit 启动/连上：tabbit_launch / 检查已有页面
2. 注入反检测：tabbit_antidetect()
3. 导航到目标页面：tabbit_navigate(url, waitForLoad=5000, humanBrowse=true)
4. 确认页面加载成功（检查页面标题/元素）
5. 加载飞书Token（获取 tenant_access_token）
6. 创建多维表格（如果不存在）
7. 初始化采集状态（start_time, count=0, records=[], scroll_count=0, empty_rounds=0）

### Phase 2: 视觉评估
1. tabbit_screenshot() → 得到截图路径
2. vision_analyze(image_url, question="分析页面状态：1)是否有视频数据卡片？2)页面底部是否有加载中/加载完毕的提示？3)是否有异常弹窗或验证码？4)滚动条在什么位置？")
3. 根据视觉结果决策：
   - ✅ 正常有数据 → 进入 Phase 3
   - 🟡 加载中 → 等待 2-3 秒，重新截图
   - 🚫 到底（无更多内容）→ 连续2次判断到底 → 进入 Phase 4
   - ❌ 异常弹窗/验证码 → PAUSE，通知用户手动处理

### Phase 3: 数据提取 + 滚动
1. tabbit_extract(type="text") 或 tabbit_readability(maxLength=30000) 提取全页文本
2. 调用 parser.py 解析文本为结构化记录
3. 调用 state.py 去重 + 累计
4. 打印当前进度：`已采集 X/50 条，新增 N 条`
5. 如果 reached_target() → Phase 4
6. 如果连续3次新增=0 → 判定到底 → Phase 4
7. 否则：
   a. vision_analyze 再看一眼状态（快速检查）
   b. vtabbit_input(action="scroll", direction="down") 或 tabbit_element(action="scroll-into-view")
   c. 等待 2-3 秒新数据加载
   d. 回到 Phase 2

### Phase 4: 飞书写入
1. 调用 feishu_writer.py 批量创建/追加记录
2. 打印多维表格链接和采集统计

### Phase 5: 复盘报告
- 采集总数 / 耗时
- 字段列表
- 飞书表格链接
- 异常记录（如果有）

## 状态管理

脚本 `state.py` 管理 `collect_state.json`，包含：
```json
{
  "records": [...],
  "seen_keys": {"博主名|时间|摘要hash": true},
  "scroll_count": 0,
  "empty_rounds": 0,
  "total_fetched": 0,
  "target": 50,
  "status": "collecting|done|pause",
  "start_time": "..."
}
```

## 去重策略

唯一键 = `md5(博主名称 + 发布时间 + 视频摘要[:30])`
- 同一轮采集不重复写入
- 跨轮次采集通过飞书表格已有记录去重（可选）

## 异常处理

| 异常 | 处理方式 |
|------|---------|
| Tabbit断开 | 重试3次，每次等待3秒，仍不行则通知用户 |
| 页面加载超时 | waitForLoad增加到8000，重试2次 |
| 数据解析失败 | 原样记录到 error_log，继续下一轮 |
| 飞书API限流 | 退避重试（指数退避） |
| 验证码/异常弹窗 | PAUSE → 通知用户手动处理后继续 |
| 无限滚动卡住 | 尝试tabbit_input滚动+随机偏移，避免被检测为机器人 |

## 数据字段对照

| 中文字段 | 英文标识 | 类型 | 来源 |
|---------|---------|------|------|
| 视频标题与标签 | title_tags | 文本 | 视频描述行 |
| 博主名称 | author_name | 文本 | 作者行 |
| 发布时间 | publish_time | 文本 | 时间行 |
| 视频时长 | duration | 文本 | 时长行 |
| 视频摘要 | product_summary | 文本 | 商品描述行 |
| 总播放量 | total_views | 文本 | 解析 "总播放量" 后的数字 |
| 新增播放量 | added_views | 文本 | 第二个播放量数字 |
| 已选类目结算金额 | settlement_amount | 文本 | 金额行 |
| 总点赞量 | total_likes | 文本 | 点赞数字 |

## 完整命令示例

```bash
# 启动Tabbit浏览器
tabbit_launch(killExisting=true)

# 导航到巨量百应爆款视频页
tabbit_navigate(url="https://buyin.jinritemai.com/dashboard/inspiration-center/hot-video", waitForLoad=5000, humanBrowse=true)

# 注入反检测
tabbit_antidetect()

# 截图检查页面
tabbit_screenshot()

# 提取文本
tabbit_extract(type="text")

# 滚动
tabbit_input(action="scroll", direction="down")

# 备用：Readability提取
tabbit_readability(maxLength=30000)
```
