# HTML 演示文稿参考 — 智能客服风格笔记

## 已验证的基础模板结构

- 6 页，含 2 个 Chart.js 图表（柱状图 + 环形图）
- 键盘左右键 / 空格翻页
- 响应式布局（桌面/平板/手机）
- 8KB 大小，零外部依赖（除 Chart.js CDN）

## 常用自定义

### 增加图表
```html
<div class="chart-container"><canvas id="chartX"></canvas></div>
<script>
new Chart(document.getElementById('chartX'), {
    type: 'bar', // bar | doughnut | line | pie | radar
    data: { labels: [...], datasets: [...] },
    options: { responsive: true, maintainAspectRatio: false }
});
</script>
```

### 卡片布局
```html
<div class="grid-3"> <!-- 或 grid-2 -->
    <div class="card">
        <div class="big-number">85%</div>
        <h3>标题</h3>
        <p>描述文字</p>
    </div>
</div>
```

### 标签徽章
```html
<span class="badge badge-blue">文本</span> <!-- blue/green/purple -->
```

## 验证通过的 CDN
- Chart.js: `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js`
