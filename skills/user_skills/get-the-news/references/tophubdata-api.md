# 今日热榜（榜眼数据）API 参考

## 基本信息

- **平台**: 榜眼数据 — 今日热榜官方数据开放平台
- **文档**: https://www.tophubdata.com/documentation
- **认证**: Header `Authorization: <API Key>`（直接传 Key 字符串，无需 Bearer 前缀）

## 全网热点内容搜索（正确版本）

### 请求
```
GET https://api.tophubdata.com/search?q=<关键词>&hashid=&p=1
```

### 参数

| 参数 | 必选 | 类型 | 说明 | 示例 |
|------|:----:|:----:|------|------|
| `q` | 是 | String | 搜索关键词（**不是 keyword**） | "AI视频生成" |
| `hashid` | 否 | String | 限定到指定榜单节点 | "mproPpoq6O"（知乎） |
| `p` | 否 | Int | 页码，每页最多50条 | 1 |

### 返回格式
```json
{
  "data": {
    "p": 1,
    "pagesize": 50,
    "totalpage": 76,
    "totalsize": 3751,
    "items": [
      {
        "title": "文章标题",
        "description": "文章描述（⚠️经常为空）",
        "thumbnail": "缩略图URL",
        "url": "原文链接",
        "extra": "热度/来源信息",
        "time": 1784283939
      }
    ]
  }
}
```

### 字段说明

| 字段 | 说明 | 注意 |
|------|------|------|
| `title` | 标题 | ✅ 基本都有 |
| `description` | 描述 | ⚠️ **经常为空**，不是抓取问题，是 API 本身数据不全 |
| `url` | 原文链接 | ✅ 可点击 |
| `extra` | 额外信息 | 有时是来源（"赚客大家谈"），有时是观看数（"24.5万"） |
| `time` | 时间戳 | Unix 秒级时间戳，需 `datetime.fromtimestamp(ts)` 转换 |
| `thumbnail` | 缩略图 | 一般没有 |

### 热度衡量

API 没有返回显式的"热度"数值。判断热度的方式：
1. **返回顺序** — 越靠前热度越高
2. **extra 字段** — 有时包含观看数（如 "24.5万"），可作热度参考
3. **time 字段** — 越新的内容可能热度越高

## 其他端点

### 全部榜单列表

```
GET https://api.tophubdata.com/nodes
```

返回所有可用的榜单（知乎热榜、微博热搜、微信24h热文等），含 `hashid`、`name`、`domain`。

## 限额

API 未返回显式的 rate-limit 头或 credit 消耗。搜索结果50条左右，通过 p 参数翻页。

## 已知问题

- **连接不稳定** — API 偶发 HTTPS 超时（`Read timed out`），需重试机制（至少3次）
- **中文编码** — 抓取页面内容时设置 `r.encoding = r.apparent_encoding` 防乱码
