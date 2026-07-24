# 美团跑腿 Skill 安装与授权记录

## 安装方式

```bash
# 从 ClawHub 下载 zip 包后解压到本地
# 解压到: ~/Developer/mt-paotui-skill/
# 复制到: ~/AppData/Local/hermes/skills/mt-paotui/
```

## 执行方式

```bash
# 使用 Node.js 直接运行（Windows 不支持 sh）
node dist/paotui.js <command> [args...]
```

## 授权流程

```
1. node dist/paotui.js login           → 获取 AUTH_LINK + 生成 QR 码
2. 用户打开链接 → 美团 App 扫码授权
3. node dist/paotui.js confirm_auth    → 完成授权
```

## 授权状态

✅ 已授权（2026-07-21）
Token 存储在 `~/.xiaomei-workspace/mt_passport_auth.json`

## 可用命令

| 命令 | 用途 |
|------|------|
| `login` | 检查登录/获取授权链接 |
| `login --force` | 强制刷新 Token |
| `confirm_auth` | 轮询确认授权 |
| `search_poi` | 搜索地址（POI） |
| `get_address_list` | 获取地址簿 |
| `preview_and_submit` | 预览费用 + 提交订单 |

## 注意事项

- 依赖 `cliguard.js` 混淆保护，不可直接查看源码
- 订单提交后需用户在美团 App 内支付（15分钟内）
- 费用 > 100 元需额外确认
- Token 过期时接口返回 `code: 10000`，需执行 `login --force` 刷新