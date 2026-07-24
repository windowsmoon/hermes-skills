# 中国云平台 AI 模型定价调研技术

## 场景

调研中国大模型厂商的 AI 模型定价和规格信息，对比不同模型的性价比和适用场景。常见于：选型决策、内容创作（如 AI 工具对比评测）、采购评估。

## 目标厂商与官方定价页

| 厂商 | 平台 | 官方定价页 |
|------|------|-----------|
| 字节跳动/火山引擎 | 火山方舟 | https://docs.volcengine.com/docs/82379/1544106 |
| 阿里云 | 百炼 Model Studio | https://help.aliyun.com/zh/model-studio/models |
| 百度 | 千帆 | https://cloud.baidu.com/doc/WENXINWORKSHOP/s/hgk91m0r6 |
| 腾讯 | 混元大模型 | https://cloud.tencent.com/product/hunyuan/pricing |
| 月之暗面/Kimi | 开放平台 | https://platform.moonshot.cn/console/pricing |
| DeepSeek | 开放平台 | https://platform.deepseek.com/api-docs/zh/pricing |

## 火山引擎（Doubao）定价调研

### URL
`https://docs.volcengine.com/docs/82379/1544106` 或访问文档首页 → 火山方舟 → 入门 → 模型价格

### 页面结构
- 页面内容在静态 HTML 中，但 DOM 树很深（大量嵌套 generic/list/listitem）
- 定价表在 "大语言模型" 部分下，按模型名分组，每行包含：模型名、条件（输入长度区间）、输入价格、缓存价格、输出价格
- 计费单位：**元/百万 token**（不是千 token！很多第三方文章写错）
- 注意分段计费：部分模型（如 doubao-seed-1.6-vision）按输入长度分段：
  - [0, 32K] tokens → 基础价
  - (32K, 128K] → 1.5x
  - (128K, 256K] → 3x

### 提取技术
用 browser_console + JS InnerText 提取整页表格数据：

```js
// 获取所有可见文本
document.body.innerText.substring(0, 50000)
// 或定位到 main 区域
document.querySelector('main')?.innerText
```

输出的文本是 tab 分隔的表格数据，直接按模型名 grep 即可定位价格。

### 关键模型名映射

| 文档名 | 含义 | 类型 |
|--------|------|------|
| doubao-seed-1.6-vision | 视觉理解专用模型 | 视觉 |
| doubao-seed-2.1-pro | 最新旗舰（多模态） | 统一多模态 |
| doubao-seed-2.1-turbo | 最新性价比款（多模态） | 统一多模态 |
| doubao-1.5-vision-pro | 上一代视觉模型（已过时） | 视觉 |
| doubao-seed-2.0-pro | 前代旗舰（纯文本） | 文本 |
| doubao-seed-1.6 | 前代标准（纯文本） | 文本 |

### 注意
- `doubao-seed-2.1` 系列虽然有多模态能力，但其定价页可能在"大语言模型"分类下而非"视觉"分类
- 视觉模型的视频理解按**输入 token 数**计费（视频帧被转为视觉 token），不是按时长计费

## 阿里云百炼（Qwen）定价调研

### URL
`https://help.aliyun.com/zh/model-studio/models` → 找到对应模型名称的锚点跳转

### 页面结构陷阱
- 该页面是 **动态渲染** 的 React SPA，browser_snapshot 只能看到侧边栏导航，主要内容在 JS 渲染后的 DOM 里
- 需要用 browser_console + JS 提取实际内容
- 锚点格式：`#qwen-vl-plus`、`#qwen-max` 等

### 提取技术

```js
// 在页面完全加载后，获取整个页面的可见文本
var allText = document.body.textContent;

// 或搜索特定模型
var idx = allText.toLowerCase().indexOf('qwen-vl-plus');
allText.substring(Math.max(0, idx - 200), idx + 1500);
```

### 计费单位
阿里云百炼使用 **元/千 token**（旧版文档）或 **元/百万 token**（新版文档），需要针对同一篇文章统一换算基准。换算公式：
- 1 千 token = 0.001 百万 token
- 1 元/千 token = 1000 元/百万 token

### 关键模型名

| 模型名 | 类型 | 上下文 |
|--------|------|--------|
| qwen3-vl-plus | 视觉理解（旗舰） | 262K |
| qwen3-vl-max | 视觉理解（超旗舰） | 未公开 |
| qwen2.5-vl-plus | 前代视觉（已过时） | 131K |
| qwen2.5-vl-max | 前代视觉旗舰 | 131K |

### 注意
- GitHub 和某些聚合网站（如 qianwenai.com、302.ai 等第三方平台）可能会比官方页更容易访问，但价格可能加价（第三方转售）
- 官方价格以 help.aliyun.com 为准
- 模型名后缀中的日期（如 `-2025-09-23`）表示模型版本快照，不影响价格

## 常见失败场景与降级

| 失败场景 | 表现 | 降级策略 |
|---------|------|---------|
| 官方页加载慢/504 | 浏览器超时 | 用 Bing 搜索"模型名 价格 百万token"找第三方总结 |
| GitHub 连接重置 | ERR_CONNECTION_RESET | 改用 Gitee 镜像或直接跳摘要 |
| SPA 页面只显示侧边栏 | snapshot 无主要内容 | 用 browser_console + JS textContent 提取 |
| 第三方平台 500 | 服务器错误 | 换另一家聚合站（302.ai / hoton.ai / ninefire） |
| 定价单位不统一 | 有的用千token有的用百万token | 统一换算为 元/百万token 再比较 |

## 第三方定价聚合站（快速参考，但可能有加价）

| 站点 | URL | 特点 |
|------|-----|------|
| 302.AI | https://302.ai | 多模型价格展示，含测评论坛 |
| HotON.AI | https://hoton.ai | 国际定价（美元），带性价比评分 |
| 九焱算力 | https://ninefireai.cn | 国产模型转售，价格略高于官方 |
| 阿里云API Explorer | https://bailian-api-explorer.vercel.app | 参数速查但偶尔不可用 |

## 完整调研实例

参考 `references/model-comparison-doubao-vs-qwen-20260718.md` 获取完整的 Doubao-Seed-Vision vs Qwen3-VL-Plus 对比过程，包括：
- 各模型价格从官方页面提取的完整记录
- 网络声浪和评测数据汇总
- 价格换算表

## 价格换算速查

| 原单位 | 换算到 元/百万token | 示例 |
|--------|-------------------|------|
| X 元/千token | X × 1000 元/百万token | 0.0015元/千token = 1.5元/百万token |
| X 元/百万token | 不变 | 0.80元/百万token = 0.80元/百万token |
| $X / 1M token | X × 7.2 元/百万token（按汇率7.2） | $0.20 = 1.44元/百万token |