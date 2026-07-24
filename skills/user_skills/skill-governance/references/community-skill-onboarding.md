# 社区 Skill 接入规范（Onboarding Checklist）

## 背景

从 skills.sh / ClawHub / 其他市场安装的社区 skill 往往针对 Claude Code / Cursor / Codex 等 Agent 设计，它们的 YAML frontmatter 标准与 Hermes 不完全一致。安装后需要做一轮"接入检查"才能让 Hermes 正确发现、匹配、触发该 skill。

## 接入流程

### 第一步：安装

```bash
# 从 skills.sh 安装（-y 跳过交互式 agent 选择菜单）
npx skills add https://github.com/<owner>/<repo> --skill <name> -y
```

安装后 skill 位于 `D:\hermes-data\.agents\skills\<name>\`（或 `~/.agents/skills/`）。

### 第二步：复制到 Hermes 技能目录

```bash
# 从 .agents 复制到 Hermes skills 目录
cp -r ~/.agents/skills/<name> ~/AppData/Local/hermes/skills/<name>
```

### 第三步：检查 YAML frontmatter 完整性

**必须检查的 4 个字段：**

| 字段 | 常见问题 | 修复方式 |
|------|---------|---------|
| `tags` | ❌ 空数组 `[]` | 补标签，如 `[video, storyboard, director, film]`，确保中英文标签都有 |
| `related_skills` | ❌ 空数组 `[]` | 补关联 skill 名，如 `[shanyin-screenwriting-master]` |
| `description` | ⚠️ 可能没写边界 | 末尾加一行：`不适用于：XXX、YYY、ZZZ等场景` |
| 依赖声明 | ❌ 可能没写工具依赖 | 检查是否有"生成文件/调用API/执行代码"等步骤，如有则补依赖说明 |

**自测标准：** 只看 description 能不能判断"什么时候该用、什么时候不该用"。

### 第四步：检查入口治理（description 边界）

社区 skill 的 description 通常只写"这个 skill 多厉害"，不写"不适合什么"。需要补：

```
原 description：
  将剧本转化为可执行的视听方案...

补边界（末尾追加）：
  不适用于：剧本创作/编剧（那是编剧大师的领域）、后期剪辑/调色/配音、
  纯视频生成（如文生视频/图生视频）、询问什么是分镜等概念解释。
```

### 第五步：检查工具依赖

社区 skill 可能假定 Agent 环境有某些能力（如 Python 库、网络 API、文件系统操作），但 Hermes 环境需要明确声明。

**常见依赖声明格式：**
```
**依赖：** 生成 xlsx 需要 Python openpyxl 库。
在 Hermes Agent 中通过 execute_code 调用 openpyxl 生成。
```

### 第六步：验证完整性

检查清单：
- [ ] SKILL.md 文件存在且完整
- [ ] YAML frontmatter 有 name、description、tags、related_skills
- [ ] description 有边界（不适用场景）
- [ ] 依赖已声明（如有）
- [ ] references/ 目录存在（如有需要）
- [ ] 核心流程/步骤未被截断或损坏
- [ ] 更新 Profile能力矩阵.md

### 第七步：更新能力矩阵

```
D:/Obsidian/Note/Profile能力矩阵.md  →  追加新 skill 条目
D:/Obsidian/Note/能力矩阵新增_<Skill名>.md  →  创建详细文档
```

## 常见陷阱

### 1. Windows 编码问题

`npx skills add` 在 git-bash/MSYS 下输出乱码（二进制数据），exit_code=1 但实际成功。
**解决：** 用 Python subprocess 调用 `npx.cmd` 并捕获 stdout，或用 `-y` 参数避免交互菜单。

### 2. 安装位置不对

npx 默认装到 `D:\hermes-data\.agents\skills\` 或 `~/.agents/skills/`，**不自动装到 Hermes 目录**。
**解决：** 手动复制到 `~/AppData/Local/hermes/skills/<name>/`。

### 3. Symlink 在 Windows 上可能失效

npx 输出的 "symlink → Hermes Agent" 在 Windows 上可能不工作。
**解决：** 直接复制目录，不依赖 symlink。

### 4. 社区 skill 的 YAML 可能不完整

skills.sh 上的 skill 设计时面向的是 Claude Code / Cursor 等 Agent，它们的 YAML 标准可能只要求 name + description。Hermes 需要 tags + related_skills + description 边界。
**解决：** 按第三步的检查清单逐项补。

## 参考案例

### Director-Master（山音超级导演大师）

**安装命令：**
```bash
npx skills add https://github.com/shanyin-ai/shanyin-director-master --skill director-master -y
```

**修复内容：**
| 字段 | 修复前 | 修复后 |
|------|--------|--------|
| tags | `[]` | `[video, storyboard, director, film, 分镜, 导演, 视频制作]` |
| related_skills | `[]` | `[shanyin-screenwriting-master]` |
| description | 无边界 | 加"不适用于：剧本创作/编剧、后期剪辑/调色/配音、纯视频生成、概念解释" |
| xlsx 依赖 | 未声明 | 加"需要 Python openpyxl 库，通过 execute_code 调用" |