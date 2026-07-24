# Tabbit Browser MCP 命令速查

## 页面导航
| 命令 | 用途 | 关键参数 |
|------|------|---------|
| tabbit_navigate | 导航到URL | url, waitForLoad(ms), humanBrowse, humanBrowseDuration |
| tabbit_antidetect | 注入反检测 | — |

## 页面交互
| 命令 | 用途 | 关键参数 |
|------|------|---------|
| tabbit_input(scroll) | 滚动页面 | direction="up"/"down" |
| tabbit_input(click) | 点击坐标 | x, y |
| tabbit_input(key) | 按键 | key="Enter"/"Escape"等 |
| tabbit_input(hotkey) | 快捷键 | hotkey="ctrl+c" |
| tabbit_element(click) | 智能点击（文本定位） | locator={text/selector} |
| tabbit_element(type) | 智能输入 | locator, text, clear |
| tabbit_element(wait) | 等待元素 | locator, timeout=10000 |
| tabbit_element(scroll-into-view) | 滚动到元素 | locator |

## 数据提取
| 命令 | 用途 | 输出 |
|------|------|------|
| tabbit_extract(type="text") | 提取全文文本 | 纯文本（已验证可行） |
| tabbit_extract(type="goods") | 提取商品 | 结构化商品数据 |
| tabbit_extract(type="links") | 提取链接 | 链接列表 |
| tabbit_readability | 智能正文提取 | Markdown |
| tabbit_screenshot | 截图 | 图片路径 |

## 其他
| 命令 | 用途 |
|------|------|
| tabbit_cookies(action="save"/"load") | 保存/恢复登录态 |
| tabbit_launch(killExisting=true) | 启动浏览器 |
| tabbit_status() | 检查连接 |
| tabbit_tabs(action="list") | 列出标签页 |
| tabbit_tabs(action="close") | 关闭标签页 |
| tabbit_new() | 打开新标签页 |
