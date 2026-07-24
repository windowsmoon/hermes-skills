# Apify MCP 服务器 — 安装 & 数据能力

## 安装

```yaml
# 在 Hermes config.yaml 的 mcp_servers 段添加：
apify-mcp:
    command: npx
    args:
      - "-y"
      - "@apify/actors-mcp-server"
    env:
      APIFY_TOKEN: apify_api_xxxxxxxxxxxxx
    enabled: true
```

### 关键陷阱

- **环境变量名是 `APIFY_TOKEN`，不是 `APIFY_API_TOKEN`**。写错了会报 "APIFY_TOKEN is required"。
- 推荐先 `npm install -g @apify/actors-mcp-server` 预安装，避免每次启动时 npx 下载 261 个依赖。
- 测试连接：`hermes mcp test apify-mcp`（预期：✓ Connected + 11 tools discovered）

### 可用的 MCP 工具（共 11 个）

| 工具 | 作用 |
|------|------|
| `search-actors` | 搜索 Apify Store，找爬取器 |
| `call-actor` | 运行任意 Actor（执行爬取任务） |
| `fetch-actor-details` | 查 Actor 详情/定价/输入参数 |
| `get-actor-run` | 查看运行状态 |
| `get-dataset-items` | 获取采集结果数据 |
| `abort-actor-run` | 中断运行中的任务 |
| `search-apify-docs` | 搜 Apify 文档 |
| `fetch-apify-docs` | 获取完整文档内容 |
| `get-key-value-store-record` | 读取 KV 存储 |
| `apify--rag-web-browser` | RAG 网页浏览器 |
| `report-problem` | 报告问题 |

## 国内电商数据覆盖

### ✅ 有现成 Actor 的平台

| 平台 | Actor | 核心数据 | 定价 |
|------|-------|---------|------|
| **淘宝/天猫** | `sian.agency/taobao-tmall-product-scraper` | 90+字段：价格/SKU/评论/店铺/优惠券后价/销量 | $10/1000条 |
| **1688 批发** | `zen-studio/1688-wholesale-scraper` | 50+字段：阶梯价/供应商认证/工厂数据/一件代发 | 按计算单元 |
| **京东 JD.com** | `sian.agency/jd-com-product-scraper` | 关键词搜索+详情+评论+店铺目录 | 按结果计费 |
| **京东 JD.com** | `zen-studio/jd-com-search-scraper` | 价格/图片/店铺/属性/评论 | 按结果计费 |
| **抖音电商** | `zen-studio/douyin-product-search-scraper` | 月销量/30天趋势/好评率/店铺分/佣金 | 按结果计费 |
| **抖音视频** | `zen-studio/douyin-search-scraper` | 60+字段+MP4下载 | 免费10次 |
| **闲鱼** | `zen-studio/goofish-xianyu-search-scraper` | 150+字段：芝麻信用/规格/图片/运费 | 按结果计费 |
| **微店** | `notdemna/weidian-products` | 标题/价格/SKU/图片/标签 | 按结果计费 |

### ❌ 没有的
- **拼多多 Pinduoduo** — Apify Store 里没有任何 PDD 爬取器

## 定价模型

```
总成本 = Apify 平台订阅费 + 每次运行 Actor 的费用

平台: Free $0/月（送$5额度）
       Starter $29/月（送$29额度）
       Scale $199/月（送$199额度）

Actor 费用: 按结果数量计费（pay-per-result）
           淘宝搜索 ≈ $10/1000条
```

### maxPages 参数详解（以淘宝爬取器为例）

| 属性 | 值 |
|------|-----|
| 范围 | 1 ~ **50** |
| 默认 | 5 |
| 免费版单次 | 最多 5 条 |
| 关键词搜索 (maxPages:50) | ~500 条商品 |
| 店铺目录 (maxPages:50) | ~3000+ 条商品（60条/页） |

**计费**：按实际采集到的结果条数收费，空页不收费。

### 成本估算示例

```
场景：监控淘宝"无线耳机"TOP100价格
每次：keywordSearch, maxPages=10, ~100条
费用：~$1/次
频率：每周一次 → ~$4/月 + 平台费 $0(免费版)
```

## 使用示例（通过 MCP）

```
search-actors("taobao") → 找到 sian.agency/taobao-tmall-product-scraper
call-actor("sian.agency/taobao-tmall-product-scraper", {
  operation: "keywordSearch",
  keyword: "无线耳机",
  maxPages: 5,
  sort: "_sale"
}) → 获取数据
get-dataset-items(runId) → 读取采集结果
```
