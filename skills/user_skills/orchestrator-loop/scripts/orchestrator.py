"""
orchestrator.py -- Five-phase Task Orchestration Loop
=====================================================

基于 loop_engine.py，实现：
  Phase 1: UNDERSTAND  - approval model + Sequential Thinking -> /goal
  Phase 2: PLAN        - MOA 4 models + SeqThink -> 5 COT -> compare -> user selects
  Phase 3: PREPARE     - tavily search + info filter + tool matching
  Phase 4: EXECUTE     - Executor (v4-flash) + Auditor (v4-pro) dual Agent inner loop
  Phase 5: REVIEW      - matplotlib actual-path PNG + 7-dimension retrospective

Design:
  - Makers produce execution instructions to workspace directory
  - Hermes Agent executes instructions, then calls loop.advance()
  - Human-gate steps pause for user approval
  - Failed Phase 4 execution is raw material for Phase 5 retrospective
"""

import sys, os, json
from datetime import datetime

ENGINE_PATH = "C:/Users/Admin/AppData/Local/hermes/skills/loop-engine/scripts"
sys.path.insert(0, ENGINE_PATH)
from loop_engine import Loop, Step, StepResult


def ensure_workspace(state_path):
    ws = os.path.dirname(state_path)
    os.makedirs(ws, exist_ok=True)
    os.makedirs(os.path.join(ws, "cot"), exist_ok=True)
    os.makedirs(os.path.join(ws, "flowcharts"), exist_ok=True)
    os.makedirs(os.path.join(ws, "search"), exist_ok=True)
    os.makedirs(os.path.join(ws, "execution-log"), exist_ok=True)
    return ws


# ============================================================
# Phase 1: UNDERSTAND
# ============================================================

def maker_task_trigger(ctx):
    state = ctx["state"]
    workspace = ensure_workspace(ctx["loop"].state_path)
    task_input = state.get("task_input", "MISSING")

    template = """## Phase 1: UNDERSTAND

### Step 1: Prompt Engineering
Use the approval model (auxiliary.approval = custom:183399/deepseek-v4-pro)
to optimize the user's original instruction:
  - Eliminate ambiguity
  - Define /goal (measurable target)
  - Identify implicit constraints

### Step 2: Sequential Thinking
Call Sequential Thinking MCP service, output:
  - What information does this task need (gap prediction)
  - SMART validation questions (list each)
  - One independent COT path (as the 5th COT)

### Step 3: Generate Task Definition Document
Merge results of Step 1 and Step 2, write to {0}/task-definition.md

Format:
  /goal: <one-line measurable target>
  constraints: [c1, c2, ...]
  information_gaps:
    - need user supplement: <question>
    - need search: <search terms>
  smart_check:
    specific:   <score 1-5>
    measurable: <score 1-5>
    achievable: <score 1-5>
    relevant:   <score 1-5>
    time_bound: <score 1-5>
  cot_skeleton: <SeqThinking COT steps>

### Original User Instruction
{1}""".format(workspace, task_input)

    instruction_file = os.path.join(workspace, "phase1-instruction.md")
    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(template)

    return StepResult(status="blocked", data={
        "instruction": "Phase 1: approval model + Sequential Thinking -> /goal",
        "instruction_file": instruction_file,
        "output_file": os.path.join(workspace, "task-definition.md"),
    })


def checker_task_trigger(ctx, output):
    workspace = ensure_workspace(ctx["loop"].state_path)
    td_file = os.path.join(workspace, "task-definition.md")
    if not os.path.exists(td_file):
        return False
    with open(td_file, "r", encoding="utf-8") as f:
        c = f.read()
    return "/goal:" in c and "smart_check" in c and "information_gaps" in c


# ============================================================
# Phase 2: PLAN - MOA analysis + COT comparison
# ============================================================

def maker_moa_analysis(ctx):
    workspace = ensure_workspace(ctx["loop"].state_path)
    td_file = os.path.join(workspace, "task-definition.md")
    td = "/goal: (not yet defined)"
    if os.path.exists(td_file):
        with open(td_file, "r", encoding="utf-8") as f:
            td = f.read()[:2000]

    cot_dir = os.path.join(workspace, "cot")
    flowchart_dir = os.path.join(workspace, "flowcharts")

    template = """## Phase 2: PLAN - MOA COT Analysis

### Step 1: Run MOA Mind-Daily
Enable MOA preset "Mind-Daily" (Qwen3.7-plus + DeepSeek-V4-Pro + GLM-5.2 + MiniMax-M3, aggregator GPT-5.5).
Use the following prompt for all 4 models:

> Based on the task definition below, produce a complete execution plan (COT):
> 1. OKR decomposition (Objective + 3 Key Results around /goal)
> 2. Task methodology (what approach to solve)
> 3. Success rate estimate (0-100% + rationale)
> 4. Failure risk prediction (at least 3 risks)
> 5. Estimated duration
> 6. Human intervention/approval points needed
>
> {1}

Save 4 COTs to:
  - {0}/cot-qwen.md
  - {0}/cot-deepseek.md
  - {0}/cot-glm.md
  - {0}/cot-minimax.md

### Step 2: Sequential Thinking as 5th COT
Independent COT (focus: information gaps + logic validation) -> {0}/cot-seqthink.md

### Step 3: COT Comparison
Default model (deepseek-v4-flash) compares all COTs on:
  - Contradiction points (conflicting conclusions)
  - Common risks (risks mentioned by all COTs)
  - Methodology soundness (scientific vs hacky)
  - Scoring: success_rate_score + speed_score + low_intervention_score = total, descending

Write to {0}/comparison.md

### Step 4: Generate Skeleton Flowchart
Use matplotlib to draw 6 subplots (one per COT + comparison).
Color: green=high success steps, yellow=risks, red=conflicts.
Save to {2}/cot-comparison.png""".format(cot_dir, td, flowchart_dir)

    instruction_file = os.path.join(workspace, "phase2-instruction.md")
    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(template)

    return StepResult(status="blocked", data={
        "instruction": "Phase 2: MOA + SeqThink -> 5 COT -> compare -> flowchart",
        "instruction_file": instruction_file,
        "cot_dir": cot_dir,
    })


def checker_moa_analysis(ctx, output):
    workspace = ensure_workspace(ctx["loop"].state_path)
    cot_dir = os.path.join(workspace, "cot")
    if not os.path.exists(cot_dir):
        return False
    return len([f for f in os.listdir(cot_dir) if f.endswith(".md")]) >= 1


# ============================================================
# Phase 2b: COT Selection (human_gate)
# ============================================================

def maker_cot_selection(ctx):
    workspace = ensure_workspace(ctx["loop"].state_path)
    comparison_file = os.path.join(workspace, "cot", "comparison.md")
    flowchart_file = os.path.join(workspace, "flowcharts", "cot-comparison.png")

    comparison = "comparison file not yet generated"
    if os.path.exists(comparison_file):
        with open(comparison_file, "r", encoding="utf-8") as f:
            comparison = f.read()[:500]

    return StepResult(status="blocked", data={
        "comparison": comparison,
        "comparison_file": comparison_file,
        "flowchart": flowchart_file,
        "question": "Select execution path: enter number (1-5) or 'discuss' for group chat debate",
        "options": [
            "1: Qwen approach", "2: DeepSeek approach", "3: GLM approach",
            "4: MiniMax approach", "5: Sequential Thinking approach",
        ],
    })


# ============================================================
# Phase 2c: COT Grilling (checker only)
# ============================================================

def maker_cot_grill(ctx):
    """Write grilling instruction. Agent executes to grill the selected COT."""
    workspace = ensure_workspace(ctx["loop"].state_path)
    cot_dir = os.path.join(workspace, "cot")
    report_file = os.path.join(cot_dir, "grill-report.md")

    # If report already has ALL_RESOLVED, skip
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            if "ALL_RESOLVED" in f.read():
                return StepResult(data={"grill_report": report_file,
                                        "status": "already_passed"})

    instruction = """## COT Grilling (adversarial review)

### Role
deepseek-v4-pro acts as adversarial reviewer. Grill the user-selected COT path.

### Grilling Rules (max 3 rounds)
For each COT step, ask:

(1) Assumption check: Why does this step hold?
(2) Boundary check: Does it still work in a different scenario/input?
(3) Alternative check: Is there a simpler way?
(4) Gap check: What have you missed?

### Process
Round 1: griller asks all questions about the COT
Round 2: COT author responds to each question, may adjust the plan
Round 3: griller asks follow-up questions on unresolved items
       -> If none: report PASS, write ALL_RESOLVED at end of report
       -> If any: report FAIL, list remaining issues

### Output
Save final report to """ + report_file + """
End the report with line: ## VERDICT: ALL_RESOLVED (if passed) or: ## VERDICT: UNRESOLVED (if issues remain)"""

    instruction_file = os.path.join(workspace, "phase2c-grill-instruction.md")
    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(instruction)

    return StepResult(status="blocked", data={
        "instruction": "Phase 2c: Grill selected COT with adversarial review",
        "instruction_file": instruction_file,
        "grill_report": report_file,
    })


def checker_cot_grill(ctx, output):
    """Return True when grilling passes (ALL_RESOLVED), False to trigger re-grill."""
    workspace = ensure_workspace(ctx["loop"].state_path)
    report_file = os.path.join(workspace, "cot", "grill-report.md")
    if not os.path.exists(report_file):
        return False
    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read()
    # Only pass if ALL_RESOLVED
    if "ALL_RESOLVED" in content:
        return True
    # UNRESOLVED or no verdict -> re-run maker (re-grill)
    return False


# ============================================================
# Phase 3: PREPARE - info collection + tool matching
# ============================================================

def maker_prep_info(ctx):
    """Phase 3: Parallel info collection via Kanban workers."""
    workspace = ensure_workspace(ctx["loop"].state_path)
    td_file = os.path.join(workspace, "task-definition.md")
    td = "N/A"
    if os.path.exists(td_file):
        with open(td_file, "r", encoding="utf-8") as f:
            td = f.read()[:1000]

    search_dir = os.path.join(workspace, "search")
    flowchart_dir = os.path.join(workspace, "flowcharts")

    # Generate Kanban tasks for parallel search
    kanban_tasks = []
    for i, gap_line in enumerate(td.split("\n")):
        if gap_line.strip().startswith("- need:") or gap_line.strip().startswith("- need search:"):
            query = gap_line.split(":", 1)[1].strip()
            kanban_tasks.append({
                "id": f"search-{i}",
                "title": query,
                "lane": "research",
                "tool": "tavily" if "api" not in query.lower() else "firecrawl",
                "priority": "high" if "critical" in query.lower() else "normal",
            })

    # If no gaps parsed, generate a default search task
    if not kanban_tasks:
        kanban_tasks = [
            {"id": "search-0", "title": "Search for key information related to /goal", "lane": "research", "tool": "tavily", "priority": "high"},
            {"id": "search-1", "title": "Find tech docs / API references for tool stack", "lane": "research", "tool": "exa", "priority": "normal"},
        ]

    tasks_yaml = "\n".join(
        f"  - id: {t['id']}\n    title: {t['title']}\n    lane: {t['lane']}\n    tool: {t['tool']}\n    priority: {t['priority']}\n    status: todo"
        for t in kanban_tasks
    )

    template = """## Phase 3: PREPARE - Parallel Info Collection via Kanban

### Kanban Board Setup
Create a Kanban board with lane "research" and populate with these tasks:

{0}

### Worker Configuration
Launch 3+ workers (deepseek-v4-flash) assigned to the "research" lane.
Each worker:
  - Claims a "todo" task from the board
  - Uses the tool specified in the task (tavily/Exa/Firecrawl)
  - Writes results to {1}/{{task_id}}.md
  - Moves task to "done" column
  - Repeats until no more "todo" tasks

### Filtering (after all searches done)
Default model (deepseek-v4-flash) filters search results:
  - Relevant to /goal -> keep, inject into flowchart nodes
  - Irrelevant -> mark EXCLUDED, archive but don't inject

### Flowchart Update
Based on original COT skeleton + injected data, generate enhanced flowchart:
  {2}/prepared-plan.png

### Task Definition Context:
{3}""".format(tasks_yaml, search_dir, flowchart_dir, td)

    instruction_file = os.path.join(workspace, "phase3-info-instruction.md")
    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(template)

    return StepResult(status="blocked", data={
        "instruction": "Phase 3: tavily search -> filter -> flowchart update",
        "instruction_file": instruction_file,
    })


def checker_prep_info(ctx, output):
    workspace = ensure_workspace(ctx["loop"].state_path)
    flowchart = os.path.join(workspace, "flowcharts", "prepared-plan.png")
    return os.path.exists(flowchart) or os.path.exists(os.path.join(workspace, "search"))


# ============================================================
# Phase 3b: Tool Matching Confirmation (human_gate)
# ============================================================

def maker_prep_tools(ctx):
    workspace = ensure_workspace(ctx["loop"].state_path)

    tool_text = """## Tool Matching Table

Based on enhanced flowchart nodes, map required tools:

| Node | Info Need | Recommended Tool | Alternative | Call Method |
|:-----|:----------|:-----------------|:------------|:------------|
| TODO | populated from Phase 3 search results |     |     |     |

Full details: {0}/tool-match.md

Please confirm tool selections or suggest modifications.""".format(workspace)

    tool_file = os.path.join(workspace, "tool-match.md")
    with open(tool_file, "w", encoding="utf-8") as f:
        f.write(tool_text)

    return StepResult(data={
        "tool_table": tool_text,
        "tool_file": tool_file,
        "question": "Confirm tool matching table, or enter modifications",
    })


# ============================================================
# Phase 4: EXECUTE - Executor + Auditor dual Agent
# ============================================================

def maker_execute(ctx):
    """Phase 4: Kanban role pipeline + Auditor (v4-pro) judges progress."""
    workspace = ensure_workspace(ctx["loop"].state_path)

    td_file = os.path.join(workspace, "task-definition.md")
    td_hint = "/goal: (not defined)"
    if os.path.exists(td_file):
        with open(td_file, "r", encoding="utf-8") as f:
            td_hint = f.read()[:500]

    template = """## Phase 4: EXECUTE - Kanban Role Pipeline + Auditor

### Architecture
```
+-----------------------+
|   Kanban Board        |
|                       |
| Lane "research":      |     +----------------------+
|   search tasks    ----|---->| research workers      |
|                       |     | (v4-flash / tavily)   |
| Lane "execute":       |     +----------------------+
|   coding tasks    ----|---->| dev workers           |
|                       |     | (v4-flash)            |
| Lane "review":        |     +----------------------+
|   verify tasks    ----|---->| review workers        |
|                       |     | (v4-pro)              |
+-----------+----------+     +----------------------+
            |
     execution-state.md
            |
   +--------+-----------+
   |     Auditor        |
   |   (v4-pro)         |
   |                    |
   | triggered every 3  |
   | completed nodes:   |
   | (1) /goal achieved?|
   | (2) executable left?|
   | (3) dead end?      |
   | (4) budget exceeded?|
   |                    |
   | verdict: continue  |
   |        / stop      |
   |        / done      |
   +--------+-----------+
            |
     execution-result.json
```

### Kanban Role Pipeline
- Board: {0}/kanban-execution.db
- State file: {0}/execution-state.md

Lane 1 "research": search tasks (tavily/Exa/Firecrawl workers)
  - Each search task = one card
  - Multiple workers claim in parallel (no dependency between search tasks)

Lane 2 "execute": coding tasks (deepseek-v4-flash workers)
  - Each flowchart execution node = one card
  - Tasks that have upstream dependencies: blocked until dependency done
  - Worker unblocks downstream tasks upon completion

Lane 3 "review": verify tasks (deepseek-v4-pro workers)
  - Review tasks created for critical execution nodes
  - Maker/Checker: execution worker writes, review worker verifies
  - Failed review -> card moved back to "execute" lane with comments

Tasks that CANNOT be parallelized (sequential by nature):
  - keep them in the same lane with block dependency links

### Auditor (v4-pro, strong model, writes NO code)
- Trigger: every 3 completed nodes
- 5 verdict criteria:

  (1) /goal achieved?
     -> Compare with quantified targets in task definition
     -> {1}
     -> Achieved -> verdict: done

  (2) Executable nodes remaining?
     -> Scan execution-state.md for nodes with status != completed/skipped
     -> None -> verdict: done

  (3) Dead end?
     -> All remaining nodes blocked, no bypass paths
     -> verdict: stop, record specific blockage reason

  (4) Budget exceeded?
     -> Token/time exceeds 120% of Phase 3 estimate
     -> verdict: stop

  (5) Otherwise -> continue

### Execution Flow
1. Populate Kanban board from prepared plan flowchart nodes
2. Launch workers assigned to each lane (research/execute/review)
3. Workers claim todo tasks, execute, move to done
4. Dependencies: blocked task auto-unblocks when dependency done
5. Every 3 completed nodes across all lanes:
   -> Pause workers, call Auditor for audit
   -> Auditor reads execution-state.md + task-definition.md
   -> Output audit-{{timestamp}}.md to {0}/execution-log/
   -> If verdict is stop/done -> halt workers, break loop
   -> If verdict is continue -> resume workers

### Final Output (whether done or stop)
{0}/execution-result.json:
  status: "completed" | "partially_completed" | "blocked"
  total_nodes, completed_nodes, failed_nodes, skipped_nodes
  auditor_decisions: [...]
  final_reason: "..."
  total_time, total_tokens, errors: [...]

Please construct and launch the Phase 4 dual-Agent execution Loop.
""".format(workspace, td_hint)

    instruction_file = os.path.join(workspace, "phase4-instruction.md")
    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(template)

    return StepResult(status="blocked", data={
        "instruction": "Phase 4: Executor(v4-flash) + Auditor(v4-pro) dual Agent Loop",
        "instruction_file": instruction_file,
        "exec_state": os.path.join(workspace, "execution-state.md"),
    })


def checker_execute(ctx, output):
    workspace = ensure_workspace(ctx["loop"].state_path)
    return os.path.exists(os.path.join(workspace, "execution-result.json"))


# ============================================================
# Phase 5: REVIEW - flowchart + 7-dimension retrospective
# ============================================================

def maker_report(ctx):
    workspace = ensure_workspace(ctx["loop"].state_path)
    result_file = os.path.join(workspace, "execution-result.json")

    template = """## Phase 5a: Execution Flowchart

Generate a matplotlib PNG (200dpi) showing the actual execution path.

### Color Coding
- Green: start/end
- Blue: successfully executed steps (annotated with actual time + tool calls)
- Yellow diamond: decision points
- Red dashed: failed/rollback paths (annotated with failure reason)

### Data Source
Execution result: {0}/execution-result.json
Node details: {0}/execution-log/

### Output
{0}/flowcharts/actual-execution.png""".format(workspace)

    instruction_file = os.path.join(workspace, "phase5a-instruction.md")
    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(template)

    return StepResult(status="blocked", data={
        "instruction": "Phase 5a: matplotlib actual execution path PNG",
        "instruction_file": instruction_file,
        "output": os.path.join(workspace, "flowcharts", "actual-execution.png"),
    })


def checker_report(ctx, output):
    workspace = ensure_workspace(ctx["loop"].state_path)
    return os.path.exists(os.path.join(workspace, "flowcharts", "actual-execution.png"))


def maker_retrospective(ctx):
    workspace = ensure_workspace(ctx["loop"].state_path)
    result_file = os.path.join(workspace, "execution-result.json")

    template = """## Phase 5b: 7-Dimension Retrospective

Score each dimension (1-10) with detailed explanation:

(1) Goal Completion (30% weight)
    - Compare /goal quantified targets with actual achievement rate

(2) Tool Performance (15% weight)
    - Tool call success rate, failure causes

(3) COT Logic Correctness (20% weight)
    - Were decision points reasonable? Any better paths?

(4) Resource Efficiency (10% weight)
    - Time consumed, Token consumed (from execution-result.json)

(5) User Satisfaction (15% weight)
    - Based on user feedback score

(6) Information Value Effectiveness (5% weight)
    - Was search-collected info accurate and sufficient?

(7) Improvement Points (5% weight)
    - Process-level: optimization suggestions for this Loop design
    - Execution-level: specific step improvements

### Root Cause Analysis
Mark root cause nodes on flowchart (reference node_id from execution-result.json)

### Experience Injection
If you were to do this task again, how would you optimize:
  - COT selection
  - Data adoption from searches
  - Tool selection
  - Key decisions

Output to: {0}/retrospective.md""".format(workspace)

    instruction_file = os.path.join(workspace, "phase5b-instruction.md")
    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(template)

    return StepResult(status="blocked", data={
        "instruction": "Phase 5b: 7-dimension retrospective report",
        "instruction_file": instruction_file,
        "output": os.path.join(workspace, "retrospective.md"),
    })


# ============================================================
# CONSTRUCT THE LOOP
# ============================================================

def create_orchestrator(task_input, workspace_dir=None):
    if workspace_dir is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        workspace_dir = "D:/hermes-data/orchestrator/" + ts

    os.makedirs(workspace_dir, exist_ok=True)
    state_path = os.path.join(workspace_dir, "orchestrator-state.md")

    task_file = os.path.join(workspace_dir, "raw-task.md")
    with open(task_file, "w", encoding="utf-8") as f:
        f.write("# Task Input\n\n" + task_input + "\n")

    return Loop(
        name="Orchestrator - " + task_input[:50],
        state_path=state_path,
        steps=[
            Step("task-trigger", maker_task_trigger, checker_task_trigger,
                 description="approval model + Sequential Thinking -> /goal"),

            Step("moa-analysis", maker_moa_analysis, checker_moa_analysis,
                 description="MOA(4 models) + SeqThink -> 5 COT -> compare"),

            Step("cot-selection", maker_cot_selection,
                 description="User selects COT path (or 'discuss' for group chat)"),

            Step("cot-grill", maker_cot_grill, checker_cot_grill,
                 max_retries=3,
                 description="Adversarial review: grill the selected COT until all issues resolved"),

            Step("prep-info", maker_prep_info, checker_prep_info,
                 description="tavily search + data filter + flowchart update"),

            Step("prep-tools", maker_prep_tools, human_gate=True,
                 description="Tool matching table -> you confirm"),

            Step("execute", maker_execute, checker_execute,
                 description="Phase 4 Executor(v4-flash) + Auditor(v4-pro) inner Loop"),

            Step("report", maker_report, checker_report,
                 description="matplotlib actual execution path flowchart"),

            Step("retrospective", maker_retrospective,
                 description="7-dimension retrospective + root cause + experience injection"),
        ],
        context={"task_input": task_input, "workspace_dir": workspace_dir},
    )


if __name__ == "__main__":
    task_file = "D:/hermes-data/orchestrator/pending-task.md"
    if os.path.exists(task_file):
        with open(task_file, "r", encoding="utf-8") as f:
            task_input = f.read()
        loop = create_orchestrator(task_input)
        state = loop.run()
        print("Loop completed with status: " + state["status"])
        os.rename(task_file, task_file + ".done")
    else:
        print("No pending task found.")
