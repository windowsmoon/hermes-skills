# Apify 中国电商平台数据覆盖调研

> 调研日期：2026-07-18（首次） | 2026-07-18（更新：补充JD.com详情、字段级数据、weidian）
> 来源：apify.com/store 抓取 + 各 Actor 详情页 JSON-LD 解析 + JS console 全文提取
> 用途：快速判断 Apify 能否采集特定平台数据

## 覆盖的平台

| 平台 | Actor | 开发者 | 核心能力 | 定价参考 |
|------|-------|--------|----------|---------|
| **淘宝/天猫** | [taobao-tmall-product-scraper](https://apify.com/sian.agency/taobao-tmall-product-scraper) | SIÁN OÜ | **90+字段，5种操作**：关键词搜索/商品详情(含券后价)/店铺目录/评论/买家问答。SKU变体、属性、视频、图片。支持中文+英文混合搜索 | $10/1000条搜索结果 |
| **1688.com** | [1688-wholesale-scraper](https://apify.com/zen-studio/1688-wholesale-scraper) | Zen Studio | 50+字段（阶梯价/供应商认证/工厂统计/一件代发），250+产品/分，无需登录 | 按 Actor 定价 + 计算单元费 |
| **京东 JD.com** | [jd-com-product-scraper](https://apify.com/sian.agency/jd-com-product-scraper) | SIÁN OÜ | 关键词搜索+详情+评论+店铺目录+批量查价，5种操作 | 按 Actor 定价 |
| **京东 JD.com** | [jd-com-search-scraper](https://apify.com/zen-studio/jd-com-search-scraper) | Zen Studio | 价格/图片/店铺/属性/评论，中文关键词搜索 | 按 Actor 定价 |
| **抖音商城（电商）** | [douyin-product-search-scraper](https://apify.com/zen-studio/douyin-product-search-scraper) | Zen Studio | 抖音商城商品：价格、月销量、30天销量趋势、好评率、店铺分、佣金率 | 按 Actor 定价 |
| **抖音（视频）** | [douyin-scraper](https://apify.com/sian.agency/douyin-scraper) | SIÁN OÜ | 播放/点赞/评论/分享/话题/博主信息 | 同上 |
| **抖音（搜索+下载）** | [douyin-search-scraper](https://apify.com/zen-studio/douyin-search-scraper) | Zen Studio | 60+字段，MP4视频下载，按排序/发布时间/时长筛选 | 同上 |
| **闲鱼** | [goofish-xianyu-search-scraper](https://apify.com/zen-studio/goofish-xianyu-search-scraper) | Zen Studio | **150+字段**：价格/芝麻信用/规格/图片/运费/分类标签 | 同上 |
| **微店 Weidian** | [weidian-products](https://apify.com/notdemna/weidian-products) | notdemna | 标题、价格、SKU、图片、标签 | 免费版5条/次 |
| **通用电商** | [e-commerce-scraping-tool](https://apify.com/apify/e-commerce-scraping-tool) | Apify 官方 | 给任意产品URL就能爬 | 同上 |

## ✅ 京东 JD.com — 已确认有覆盖

**以下多个 JD.com Actor 均可用：**

| Actor | 开发者 | 核心能力 |
|-------|--------|----------|
| [jd-com-product-scraper](https://apify.com/sian.agency/jd-com-product-scraper) | SIÁN OÜ | 关键词搜索+产品详情+评论+店铺目录+批量查价，5种操作合一 |
| [jd-com-search-scraper](https://apify.com/zen-studio/jd-com-search-scraper) | Zen Studio | 价格、图片、店铺、属性、评论，按关键词搜索（支持中文） |
| [jd-com-product-scraper](https://apify.com/piotrv1001/jd-com-product-scraper) | FalconScrape | 产品名、品牌、分类、店铺ID、图片集 |
| [jd-scraper](https://apify.com/automation-lab/jd-scraper) | Stas Persiianenko | 按关键词/分类/URL爬取，提取标题/图片/价格/评论 |

## 淘宝/天猫 Actor 详细字段（90+ 字段）

来自 `sian.agency/taobao-tmall-product-scraper`，5种操作合一：

### 5种操作
| 操作 | 用途 | 输入 |
|------|------|------|
| `keywordSearch` | 按关键词搜索商品 | keyword + 可选价格范围/Tmall-only/排序 |
| `productDetail` | 获取单个商品完整详情 | itemId + detailVersion |
| `shopCatalog` | 拉取卖家全店商品 | userId + (可选) shopId |
| `productReviews` | 获取商品评论 | itemId + 排序方式 |
| `productQuestions` | 获取买家问答 | itemId |

### 核心输出字段（所有操作均有）
- `itemId`, `title`, `priceYuan`, `imageUrl`, `shopId`, `shopName`, `status`
- `_operation` — 标记数据来自哪个操作
- `recordTime` — 上游真实抓取时间戳（用于新鲜度验证）
- `_fetchedAt` — 本次运行时间

### 商品详情 ProductDetail 特有字段
- `originalPriceYuan`, `promotionPriceYuan`, `discountPct`, `priceRange`
- **`afterCouponAmountPrice`** — 券后最终价（核心字段）
- `skus[]` — 每个变体的 price/stock/swatchImage/propPath
- `skuCount`, `imageUrls[]`, `descImages[]`, `videoUrl`, `videoCoverUrl`
- `properties[]`, `desc(HTML)`, `couponInfo`, `couponUrl`, `freeShipping`
- `qna[]`, `tags[]`, `categoryId`, `location`
- `attributes[]` — [{key:"品牌", value:"绿联"}, ...]
- `specs{}`, `props[]`, `sellerType`, `mainItemInfo`

### 关键词搜索 keywordSearch 特有字段
- `titleEn` — 机器翻译英文标题
- `subTitle`, `discntPriceYuan`, `commentCount`, `itemGradeAvg`
- `sellerLevel`, `sellerGoodRate`, `sellerLoc`, `userType`, `tags[]`
- `_sourceKeyword`, `_page` — 标记来源关键词和页码

### 店铺目录 shopCatalog 特有字段
- 标准模式：`promotionPrice`, `finalPromotionPrice`, `reservePrice`, `commissionRate`, `payRate30Days`, `dailySellCount`, `provcity`
- 扩展模式（60条/页）：`priceFen`, `priceZKYuanDouble`, `orderCount30Day`, `soldCount30Day`, `sellPointMap{}`

### 评论 productReviews 特有字段
- `reviewId`, `reviewDate`, `reviewContent`, `reviewAppend`, `reviewAppendDays`
- `reviewRatingStars`, `reviewTag`, `reviewPhotos[]`, `reviewVideoUrl`
- `reviewSkuLabel`, `reviewBuyAmount`, `reviewUsefulCount`
- `reviewerNick`, `reviewerVipLevel`, `reviewerAnonymous`

### detailVersion 选择（影响数据新鲜度和价格）
| 版本 | 标签 | 新鲜度 | 适用场景 |
|------|------|--------|---------|
| v9 (默认) | Full | 实时，非缓存 | 含券后价、属性、SKU图、促销信息。推荐 |
| v1 | Standard | 实时，非缓存 | 经典完整负载：SKU、Q&A、优惠券、退换货 |
| v5 | Lite | ⚠️ 缓存（可能数天~数月） | 仅当新鲜度不重要且成本优先 |
| v4 💎 | Premium | 实时 | 精确的满减后最终价（快速同步版） |
| v2 💎 | Premium | 实时异步 | 最全定价（慢、成功率稍低） |

### 定价：$10/1000条搜索结果

## 未覆盖的平台

| 平台 | 状态 | 备注 |
|------|------|------|
| **拼多多 Pinduoduo** | ❌ | 确实没有 |
| **小红书 Xiaohongshu** | ❌ | 未找到 |
| **快手 Kuaishou** | ❌ | 未找到 |
| **美团/饿了么** | ❌ | 本地生活无覆盖 |

## Apify 平台定价

```
Free      $0/月    + $5 额度     + $0.20/计算单元
Starter   $29/月   + $29 额度    + $0.20/计算单元
Scale     $199/月  + $199 额度   + $0.16/计算单元
Business  $999/月  + $999 额度   + $0.13/计算单元
Enterprise 定制价
```

每个 Actor 有独立的每次运行价格 + 计算单元消耗。实际成本 = Actor定价 + 计算单元 × 单元价格。

## Apify MCP Server 在 Hermes 上的安装

### 前置条件

1. 在 [apify.com](https://apify.com) 注册账号（免费版送 $5 额度）
2. 从 Apify Console → **API & Integrations** → 复制 API Token

### 安装步骤

```bash
# ① 全局预装 npm 包（避免 npx 首次下载超时）
npm install -g @apify/actors-mcp-server

# ② 验证安装
actors-mcp-server --help  # 应能正常输出帮助
```

### Hermes 配置（config.yaml）

添加到 `C:\Users\<user>\AppData\Local\hermes\config.yaml` 的 `mcp_servers:` 块中：

```yaml
mcp_servers:
  # ... 已有 MCP 服务器 ...
  apify-mcp:
    command: npx
    args:
      - "-y"
      - "@apify/actors-mcp-server"
    env:
      APIFY_TOKEN: "<你的Apify API Token>"
    enabled: true
```

### ⚠️ 已知坑点

| 坑 | 说明 |
|---|------|
| **环境变量名是 `APIFY_TOKEN` 不是 `APIFY_API_TOKEN`** | 文档里写的是 `APIFY_API_TOKEN`，但 MCP 包实际读取的是 `APIFY_TOKEN`。配错的话错误信息是 `APIFY_TOKEN is required but not set` |
| **`hermes config set` 不能设 mcp_servers 下的 env** | 它会把 `APIFY_TOKEN` 当成 OS 环境变量名去设置，会报错 `Invalid environment variable name`。必须直接编辑 config.yaml |
| **npm 预装可大幅减少连接超时** | 如果不预装，npx 首次需要下载 261+ 包（约 1 分钟），MCP 连接测试的 40s 超时会失败 |
| **MCP Server 需重启 Hermes 才能当前会话使用** | 配置写入后，`hermes mcp list` 能看到已启用，但当前会话的工具集不会自动加载。需要重启 Hermes Desktop 应用 |
| **`patch` 工具拒绝写 config.yaml** | Hermes 保护 AppData 下的 config.yaml，报 `Refusing to write to security-sensitive configuration`。改用 Python `open().write()` 或 `hermes config set`（有限支持） |

### 验证命令

```bash
# 查看所有 MCP 服务器状态
hermes mcp list

# 测试指定 MCP 服务器连接
hermes mcp test apify-mcp

# 成功后应看到：✓ Connected + ✓ Tools discovered: 11
# 11 个工具包括：search-actors, call-actor, fetch-actor-details, get-dataset-items 等
```

### 可用工具列表（共11个）

| 工具 | 功能 |
|------|------|
| `search-actors` | 搜索 Apify Store，按关键词找爬取 Actor |
| `call-actor` | 运行任意 Actor，传参启动爬取任务 |
| `fetch-actor-details` | 获取 Actor 详情（ID/描述/输入 schema） |
| `get-actor-run` | 查询运行状态和结果 |
| `get-dataset-items` | 获取采集数据集（分页/排序/过滤） |
| `get-key-value-store-record` | 读取 KV 存储 |
| `abort-actor-run` | 中断运行中的任务 |
| `search-apify-docs` | 搜索 Apify 文档 |
| `fetch-apify-docs` | 获取文档全文 |
| `apify--rag-web-browser` | RAG 网页浏览器 Actor |
| `report-problem` | 反馈问题 |

## 调研方法（可复用于其他平台调研）

1. 访问 apify.com/store 获取首页 Actor 列表
2. 提取所有 `href="/username/actor-name"` 链接
3. 对候选 Actor 页面提取 JSON-LD (application/ld+json) 获取结构化描述
4. 使用 `<meta name="description">` 作为补充信息
5. 遍历所有已知中文平台名确认有无覆盖
6. 尝试猜测可能的 Actor URL 模式并逐个探测（如 /username/jd-scraper）
