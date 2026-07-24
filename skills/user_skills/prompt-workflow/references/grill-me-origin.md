# Grill Me 起源与 O→反馈环理论基础

## Grill Me 原始定义

来源：https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me

**SKILL.md（7 行）：**
```yaml
name: grill-me
description: A relentless interview to sharpen a plan or design.
disable-model-invocation: true
```

**agents/openai.yaml：**
```yaml
interface:
  display_name: "Grill Me"
  short_description: "Sharpen a plan through interview"
policy:
  allow_implicit_invocation: false
```

核心设计两个关键约束：
1. `disable-model-invocation: true` → 不让 AI 自动调用模型写代码
2. `allow_implicit_invocation: false` → 必须人类主动触发

翻译成人话：**写代码之前的魔鬼审讯官——不把需求说清楚，AI 不动手。**

## 与 O→反馈环的关系

本技能（prompt-workflow）的 Phase 0 Grill 直接对应以下闭环：

```
人类设 O ──→ AI 理解 why ──→ AI 反馈 ──→ 人类修订 O ──→ AI 执行
```

Grill Me 就是把「理解 why → 反馈」这个环节显式化、强制化、流程化了。

## 为什么这个洞察重要

大多数 prompt 优化工具只做文本层面的打磨（措辞改进、结构优化），
但没有先验证**方向是否正确**。Grill Me 的核心贡献不是技术层面的，而是流程层面的——

**技术问题：这个提示词写得好不好？**
**战略问题：我们要解决的是不是正确的问题？**

Phase 0 解决的是战略问题，Phase 1-3 解决的是技术问题。
跳过 Phase 0 = 把一条偏了的路铺得更好，但路还是偏的。

## 社区来源

这个分享来自 Hermes Agent 中文社区微信群 38 的讨论：
> 在使用Agent开发应用时，推荐首先使用"Grill Me"技能，引导Agent深入追问，
> 明确需求细节与架构设计，待方案清晰后再交由Agent编程，
> 这种工作流能有效减少返工，提高效率。
