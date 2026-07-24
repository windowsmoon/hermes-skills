#!/usr/bin/env python3
"""产品生命周期流水线 状态机 — 管理4阶段18步的状态流转"""

import json, os, sys, time
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.product-lifecycle-state.json")

PIPELINE = {
    "phase1_strategic_insight": {
        "name": "战略洞察期 (0→1)",
        "goal": "找方向、选战场、判生死",
        "steps": [
            {"id": "p1s1", "name": "产品愿景", "skill": "product-vision", "output": "Mission Statement"},
            {"id": "p1s2", "name": "SWOT分析", "skill": "swot-analysis", "output": "优劣势威胁矩阵"},
            {"id": "p1s3", "name": "市场细分", "skill": "market-segments", "output": "目标细分市场"},
            {"id": "p1s4", "name": "竞品分析", "skill": "competitor-analysis", "output": "竞品定位空白点"},
            {"id": "p1s5", "name": "用户调研", "skill": "analyze-feature-requests", "output": "未满足痛点清单"},
            {"id": "p1s6", "name": "用户画像", "skill": "user-personas", "output": "典型Persona"},
        ]
    },
    "phase2_definition": {
        "name": "定义聚焦期 (立项)",
        "goal": "确定唯一核心指标和差异化锚点",
        "steps": [
            {"id": "p2s1", "name": "战略画布", "skill": None, "output": "价值曲线图"},
            {"id": "p2s2", "name": "定位", "skill": "positioning-ideas", "output": "核心差异化口号"},
            {"id": "p2s3", "name": "北极星指标", "skill": "north-star-metric", "output": "长期健康指标"},
            {"id": "p2s4", "name": "机会树", "skill": "opportunity-solution-tree", "output": "可拆解指标+杠杆"},
            {"id": "p2s5", "name": "功能优先级", "skill": "prioritize-features", "output": "MVP Backlog"},
        ]
    },
    "phase3_execution": {
        "name": "落地执行期 (从需求到上线)",
        "goal": "拆解任务、保障质量、合规避险",
        "steps": [
            {"id": "p3s1", "name": "写PRD", "skill": "create-prd", "output": "8段式PRD文档"},
            {"id": "p3s2", "name": "用户故事", "skill": "user-stories", "output": "开发任务拆分"},
            {"id": "p3s3", "name": "Sprint规划", "skill": "sprint-plan", "output": "迭代计划"},
            {"id": "p3s4", "name": "测试场景", "skill": "test-scenarios", "output": "验收用例集"},
            {"id": "p3s5", "name": "NDA/隐私终审", "skill": "draft-nda", "output": "合规文件"},
        ],
        "delegate_to": ["engineering-director", "qa-director"]
    },
    "phase4_growth": {
        "name": "上市增长期 (上线后)",
        "goal": "把产品推出去，形成自增长闭环",
        "steps": [
            {"id": "p4s1", "name": "GTM策略", "skill": "gtm-strategy", "output": "定价/渠道/推广计划"},
            {"id": "p4s2", "name": "增长飞轮", "skill": "growth-loops", "output": "留存自传播正循环"},
        ]
    }
}

PHASE_ORDER = ["phase1_strategic_insight", "phase2_definition", "phase3_execution", "phase4_growth"]

def default_state():
    return {
        "product_name": "",
        "status": "not_started",
        "current_phase": 0,
        "current_step": 0,
        "completed_steps": [],
        "started_at": None,
        "updated_at": None,
        "outputs": {},
        "delegations": {}
    }

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return default_state()

def save_state(state):
    state["updated_at"] = time.time()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def cmd_start(product_name):
    state = load_state()
    if state["status"] == "running":
        print(f"已有进行中的产品: {state['product_name']}，请先完成或使用 reset")
        return
    state = default_state()
    state["product_name"] = product_name
    state["status"] = "running"
    state["started_at"] = time.time()
    save_state(state)
    phase = PHASE_ORDER[state["current_phase"]]
    step = PIPELINE[phase]["steps"][state["current_step"]]
    print(f"启动产品: {product_name}")
    print(f"当前位置: {PIPELINE[phase]['name']} → {step['name']}")
    print(f"产出目标: {step['output']}")
    if step["skill"]:
        print(f"参考技能: pm-skills/{step['skill']}")

def cmd_status():
    state = load_state()
    if state["status"] == "not_started":
        print("无进行中的产品。使用 start <产品名> 开始")
        return
    phase = PHASE_ORDER[state["current_phase"]]
    phase_data = PIPELINE[phase]
    step = phase_data["steps"][state["current_step"]]
    print(f"产品: {state['product_name']}")
    print(f"进度: {state['current_phase']+1}/4 阶段, {state['current_step']+1}/{len(phase_data['steps'])} 当前步")
    print(f"已完成: {len(state['completed_steps'])}/{sum(len(p['steps']) for p in PIPELINE.values())} 步")
    print(f"当前阶段: {phase_data['name']}")
    print(f"当前步骤: {step['name']} → {step['output']}")
    if state["outputs"]:
        print(f"已产出: {list(state['outputs'].keys())}")

def cmd_next():
    state = load_state()
    if state["status"] != "running":
        print("没有进行中的产品")
        return
    phase = PHASE_ORDER[state["current_phase"]]
    phase_data = PIPELINE[phase]
    current_step = phase_data["steps"][state["current_step"]]
    step_id = current_step["id"]
    if step_id not in state["completed_steps"]:
        state["completed_steps"].append(step_id)
    if state["current_step"] + 1 < len(phase_data["steps"]):
        state["current_step"] += 1
        save_state(state)
        next_step = phase_data["steps"][state["current_step"]]
        print(f"完成: {current_step['name']}")
        print(f"下一步: {next_step['name']} → {next_step['output']}")
        if next_step["skill"]:
            print(f"技能: pm-skills/{next_step['skill']}")
    else:
        state["current_step"] = 0
        state["current_phase"] += 1
        if state["current_phase"] >= len(PHASE_ORDER):
            state["status"] = "completed"
            save_state(state)
            print(f"全生命周期完成: {state['product_name']}")
        else:
            save_state(state)
            next_phase = PIPELINE[PHASE_ORDER[state["current_phase"]]]
            print(f"阶段完成: {phase_data['name']}")
            print(f"进入下阶段: {next_phase['name']}")
            print(f"第一步: {next_phase['steps'][0]['name']}")
            if next_phase.get("delegate_to"):
                print(f"委托: {', '.join(next_phase['delegate_to'])}")

def cmd_step(step_id):
    for phase_key in PHASE_ORDER:
        phase = PIPELINE[phase_key]
        for i, step in enumerate(phase["steps"]):
            if step["id"] == step_id:
                state = load_state()
                state["current_phase"] = PHASE_ORDER.index(phase_key)
                state["current_step"] = i
                save_state(state)
                print(f"跳到: {phase['name']} → {step['name']}")
                if step["skill"]:
                    print(f"技能: pm-skills/{step['skill']}")
                return
    print(f"未找到步骤: {step_id}")

def cmd_reset():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("状态已重置")

def cmd_set_output(key, value):
    state = load_state()
    state["outputs"][key] = value
    save_state(state)
    print(f"已记录: {key} = {value[:50]}...")

def cmd_rollback():
    state = load_state()
    if state["status"] != "running":
        print("没有进行中的产品")
        return
    if state["current_step"] > 0:
        state["current_step"] -= 1
        phase = PHASE_ORDER[state["current_phase"]]
        step_to_remove = PIPELINE[phase]["steps"][state["current_step"]]["id"]
        if step_to_remove in state["completed_steps"]:
            state["completed_steps"].remove(step_to_remove)
        save_state(state)
        print(f"回退到: {PIPELINE[phase]['steps'][state['current_step']]['name']}")
    elif state["current_phase"] > 0:
        state["current_phase"] -= 1
        prev_phase = PIPELINE[PHASE_ORDER[state["current_phase"]]]
        state["current_step"] = len(prev_phase["steps"]) - 1
        save_state(state)
        print(f"回退到上阶段: {prev_phase['steps'][-1]['name']}")
    else:
        print("已在第一步")

def cmd_list():
    for phase_key in PHASE_ORDER:
        phase = PIPELINE[phase_key]
        print(f"\n{phase['name']} [{phase['goal']}]")
        for step in phase["steps"]:
            s = f"  [{step['id']}] {step['name']} → {step['output']}"
            if step["skill"]:
                s += f" (技能: pm-skills/{step['skill']})"
            print(s)
        if phase.get("delegate_to"):
            print(f"  委托: {', '.join(phase['delegate_to'])}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: orchestrator.py <command> [args...]")
        print("命令: start <name> | status | next | step <id> | rollback | reset | list | set-output <k> <v>")
        sys.exit(1)
    cmd = sys.argv[1]
    {"start": lambda: cmd_start(" ".join(sys.argv[2:])),
     "status": cmd_status,
     "next": cmd_next,
     "step": lambda: cmd_step(sys.argv[2]) if len(sys.argv) > 2 else None,
     "rollback": cmd_rollback,
     "reset": cmd_reset,
     "list": cmd_list,
     "set-output": lambda: cmd_set_output(sys.argv[2], " ".join(sys.argv[3:])) if len(sys.argv) > 3 else None,
     "help": lambda: print("Commands: start, status, next, step, rollback, reset, list, set-output")
    }.get(cmd, lambda: print(f"未知命令: {cmd}"))()
