# HTML 演示风格预设速查

## 配色预设

| 预设名 | 主色 primary | 辅色 secondary | 强调 accent | 背景 bg | 卡片 card |
|--------|-------------|---------------|------------|---------|----------|
| 🔵 科技蓝 | #2D6FF2 | #00D4AA | #7C5CFC | #0A0E27 | #151B3D |
| 🟣 赛博朋克 | #FF3366 | #00FFFF | #FFD700 | #0D0D2B | #1A1A3E |
| ⚪ 极简白 | #1A1A2E | #E94560 | #0F3460 | #FFFFFF | #F5F5F5 |
| 🟠 暖色调 | #FF6B35 | #F7C59F | #004E89 | #1A1A2E | #2D2D44 |
| 🌈 渐变风 | #667EEA | #764BA2 | #F093FB | #0F0C29 | #1A1543 |

## 字体配对

| 风格 | 标题字体 | 正文字体 |
|------|---------|---------|
| 📰 默认 | 'Space Grotesk' | 'Inter' |
| ✍️ 手写感 | 'Caveat' | 'Nunito' |
| 🏛️ 宋体 | 'Noto Serif SC' | 'Noto Sans SC' |
| 💻 无衬线 | 'Montserrat' | 'Open Sans' |

加载 Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
```

## 布局模式

| 模式 | CSS | 说明 |
|------|-----|------|
| 功能网格 | `grid-template-columns: 1fr 1fr 1fr` | 3列卡片 |
| 指标看板 | `.big-number` + 卡片 | 大数字+说明 |
| 双栏对比 | `grid-template-columns: 1fr 1fr` | 文字+图表并排 |
| 时间线 | 纵向 flex | 流程/演进 |
| 案例展示 | 带图片 card | 成果展示 |

## 动画参数

| 类型 | CSS transition | 说明 |
|------|---------------|------|
| 淡入淡出 | `opacity 0.5s` | 默认 |
| 左滑 | `transform: translateX()` | 配合 opacity |
| 上滑 | `transform: translateY()` | 配合 opacity |
| 无 | `none` | 瞬间切换 |

## Chart.js 图表类型

| 图表 | type 值 | 适用 |
|------|---------|------|
| 柱状图 | `'bar'` | 对比数据 |
| 环形图 | `'doughnut'` | 占比分布 |
| 折线图 | `'line'` | 趋势变化 |
| 雷达图 | `'radar'` | 多维对比 |
