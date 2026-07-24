# 自动化节点复用模式

## 问题：垃圾节点堆积

每次运行用 uuid 后缀创建新节点：
```python
node_name = f"图片-{task_key}-{uuid.uuid4().hex[:8]}"  # ❌ 每次新建，旧节点废弃
```

**后果**：画布上堆满同名节点，用户在网页版看到的是旧节点，脚本写回飞书的却是新节点 URL——两张完全不同的图。

---

## 原则：固定节点名 + 同名复用

```python
node_name = f"图片-{task_key}-{record_id[:8]}"  # ✅ record_id 前8位固定，同记录复用同名节点
```

**LibTV 行为**：`node create` 同名已存在时**报错** `已存在显示名为「xxx」的节点`。捕获后走默认子命令复用到已有节点：

```python
# Step 1: 新建
rc, stdout, _ = libtv(["node", "create", node_name, "-t", "image",
                         "--prompt", prompt, "-s", f"model={model}", "-s", f"modeType={modeType}",
                         "--left", "参考图1", "-p", LIBTV_PROJ])
if rc != 0 and "已存在" in stderr:
    # Step 2: 复用（覆盖参数 + --run）
    rc, stdout, _ = libtv(["node", node_name, "-p", LIBTV_PROJ,
                             "--prompt", prompt, "-s", f"model={model}", "-s", f"modeType={modeType}",
                             "--left", "参考图1", "--run"])
else:
    # 首次：触发生成
    node_key = json.loads(stdout.strip())["newNodeKey"]
    rc, stdout, _ = libtv(["node", node_key, "-p", LIBTV_PROJ, "--run"])

# 解析结果 URL
compact = ''.join(stdout.split())
data = json.loads(compact)
url = (data.get("data") or data.get("node", {}) or {}).get("data", {}).get("url")
if isinstance(url, list): url = url[0]
```

## 效果对比

| | 旧策略（uuid） | 新策略（record_id） |
|---|---|---|
| 重复运行节点数 | +1 个/次 | 0（始终复用1个） |
| 用户网页版看到 | 旧节点结果 | 最新节点结果 ✅ |
| 飞书写回 URL | 新节点 URL | 最新节点 URL ✅ |