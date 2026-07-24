#!/usr/bin/env python3
"""提示词优化工具 - 调用 LLM API 优化提示词"""

import json, os, sys, urllib.request

API_KEY = "sk-1a1bda2f842562ad7361cc24b2e24d16852577771da119592d93587018946d44"
API_BASE = "https://api.183399.xyz/v1"
MODEL = "deepseek-v4-flash"

def call_llm(messages, temperature=0.3):
    """调用 LLM API"""
    data = json.dumps({
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096
    }).encode()
    
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
        return result["choices"][0]["message"]["content"]

def optimize_user_prompt(prompt, context=""):
    """优化用户提示词"""
    system_prompt = """你是一个专业的提示词优化专家。你的任务是：
1. 分析用户原始提示词的目标和意图
2. 优化提示词的结构：增加清晰的指令、上下文、输出格式要求
3. 添加示例（few-shot）来引导更好的输出
4. 确保提示词完整、无歧义、可执行
5. 保留原始意图，不改变核心需求

输出格式：
## 优化后的提示词
[优化后的完整提示词]

## 优化说明
- 改进了什么
- 为什么这样改
- 预期效果
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"需要优化的原始提示词：\n\n{prompt}\n\n上下文信息：{context}" if context else f"需要优化的原始提示词：\n\n{prompt}"}
    ]
    return call_llm(messages)

def optimize_system_prompt(prompt):
    """优化系统提示词"""
    system_prompt = """你是一个系统提示词优化专家。你的任务是优化系统级提示词（System Prompt），使其：
1. 角色定义更清晰
2. 指令更精确、无歧义
3. 行为约束更明确
4. 输出格式更规范
5. 保留原始核心能力

输出格式：
## 优化后的系统提示词
[优化后的完整提示词]

## 优化说明
- 改进了什么
- 为什么这样改
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"需要优化的系统提示词：\n\n{prompt}"}
    ]
    return call_llm(messages)

def iterate_prompt(prompt, feedback):
    """根据反馈迭代优化提示词"""
    system_prompt = """你是一个提示词迭代优化专家。用户会提供：
1. 当前的提示词版本
2. 对现有效果的反馈或需要改进的方向

请基于反馈迭代优化提示词。"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"当前提示词：\n\n{prompt}\n\n反馈/改进需求：\n\n{feedback}"}
    ]
    return call_llm(messages)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: prompt_optimizer.py <mode> <prompt>")
        print("模式: user | system | iterate")
        print("示例: prompt_optimizer.py user '写一篇关于AI的文章'")
        sys.exit(1)
    
    mode = sys.argv[1]
    prompt_text = " ".join(sys.argv[2:])
    
    if mode == "user":
        result = optimize_user_prompt(prompt_text)
    elif mode == "system":
        result = optimize_system_prompt(prompt_text)
    elif mode == "iterate":
        result = iterate_prompt(prompt_text, sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        print(f"未知模式: {mode}")
        sys.exit(1)
    
    print(result)
