# ChatPPT 已知问题与降级策略

## 已知限制

1. **主题文本必须 ≤ 200 字符** — 超长用 `import_file` 替代
2. **`--ai-picture` 是 boolean flag** — 不加 `true/false` 值，直接 `--ai-picture`
3. **免费额度有限** — 用完返回 code 11500「用户权益已用完」
4. **文件导入可绕过 200 字符限制** — 用 `chatppt ppt import_file --file-path <md文件>` 替代

## 降级链

当 ChatPPT 返回 code 11500 时，按以下顺序降级：

```
ChatPPT 额度用完
  ↓
① GordenPPTSkill（21套模板，离线本地，完全免费）
  ↓
② HTML 演示文稿（frontend-design + uiux-slides，零成本，自定风格）
```

## 充值（如需）

去 chat-ppt.com 充值续费即可恢复。