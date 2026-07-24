"""
loop_engine.py — Universal Loop Engine for Hermes Skills
"""
import os, json, time, traceback
from datetime import datetime

class StepResult:
    def __init__(self, status="completed", data=None, error=None, skip_reason=None):
        self.status = status
        self.data = data or {}
        self.error = error
        self.skip_reason = skip_reason

class Step:
    def __init__(self, name, maker, checker=None, max_retries=3,
                 human_gate=False, timeout=300, description=""):
        self.name = name
        self.maker = maker
        self.checker = checker
        self.max_retries = max_retries
        self.human_gate = human_gate
        self.timeout = timeout
        self.description = description

class Loop:
    ICONS = {"pending":"\u23f3","running":"\U0001f504","retrying":"\U0001f501",
             "completed":"\u2705","failed":"\u274c","blocked":"\U0001f534",
             "waiting_approval":"\U0001f7e1","skipped":"\u23ed\ufe0f",
             "needs_agent":"\U0001f916"}

    def __init__(self, name, state_path, steps, tools=None, context=None):
        self.name = name
        self.state_path = os.path.abspath(state_path)
        self.steps_map = {s.name: s for s in steps}
        self.step_order = [s.name for s in steps]
        self.tools = tools or {}
        self.extra_context = context or {}

    def _default_state(self):
        t = datetime.now().isoformat()
        return {"loop_name":self.name,"status":"running","current_step":self.step_order[0],
                "steps":{s:{"status":"pending","retries":0,"errors":[],"output_summary":""}
                         for s in self.step_order},
                "started_at":t,"completed_at":None,"updated_at":t,"summary":"","blocked_reason":""}

    def load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path,"r",encoding="utf-8") as f:
                return self._parse_md(f.read())
        return self._default_state()

    def _parse_md(self, content):
        state = self._default_state()
        cur = None
        step_statuses = {}
        for line in content.split("\n"):
            if line.startswith("# Loop:"):
                state["loop_name"] = line.split(":",1)[1].strip()
            elif line.startswith("Status:"):
                v = line.split(":",1)[1].strip().strip("**")
                if v in ("pending","running","retrying","completed","failed","blocked","waiting_approval"):
                    state["status"] = v
            elif line.startswith("## Phase:"):
                cur = line.split("## Phase:")[1].strip().split()[0]
                step_statuses[cur] = "pending"
            elif cur and line.strip().startswith("- Status:"):
                v = line.split(":",1)[1].strip().strip("**").split()[0]  # strip trailing gate flag
                if cur in state["steps"]:
                    state["steps"][cur]["status"] = v
                    step_statuses[cur] = v
            elif cur and line.strip().startswith("- Retries:"):
                v = line.split(":",1)[1].strip().split("/")[0]
                if cur in state["steps"]:
                    state["steps"][cur]["retries"] = int(v)
            elif cur and line.strip().startswith("- Error:"):
                if cur in state["steps"]:
                    state["steps"][cur]["errors"].append(line.split(":",1)[1].strip())
        # Fix: current_step = first non-completed/non-skipped step
        for sname in self.step_order:
            st = step_statuses.get(sname, "pending")
            if st not in ("completed", "skipped"):
                state["current_step"] = sname
                break
        return state

    def _render_md(self, state):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        gate_flag = " \u26a0\ufe0f \u9700\u5ba1\u6279"  # " ⚠️ 需审批"
        lines = [f"# Loop: {state['loop_name']}",
                 f"Status: **{state['status']}**",
                 f"Updated: {now}", ""]
        for sname in self.step_order:
            s = state["steps"].get(sname, {})
            step = self.steps_map.get(sname)
            st = s.get("status","pending")
            icon = self.ICONS.get(st, "\u23f3")
            retries = s.get("retries",0)
            max_r = step.max_retries if step else 3
            desc = step.description if step else ""
            human = gate_flag if (st == "waiting_approval") else ""
            lines.append(f"## Phase: {sname} {icon}")
            if desc:
                lines.append(f"> {desc}")
            lines.append(f"- Status: **{st}**{human}")
            lines.append(f"- Retries: {retries}/{max_r}")
            if s.get("output_summary"):
                lines.append(f"- Output: {s['output_summary']}")
            for e in s.get("errors",[])[-3:]:
                lines.append(f"  - Error: {e[:120]}")
            lines.append("")
        if state.get("blocked_reason"):
            lines.append("### Blocked")
            lines.append(state["blocked_reason"])
            lines.append("")
        if state.get("summary","").strip():
            lines.append("## Summary")
            lines.append(state["summary"].strip())
            lines.append("")
        return "\n".join(lines)

    def save_state(self, state):
        os.makedirs(os.path.dirname(self.state_path) or ".", exist_ok=True)
        with open(self.state_path,"w",encoding="utf-8") as f:
            f.write(self._render_md(state))

    def _next_step(self, cur):
        idx = self.step_order.index(cur)
        return self.step_order[idx+1] if idx+1 < len(self.step_order) else None

    def run(self, max_iter=100):
        state = self.load_state()
        it = 0
        while state["status"] == "running" and it < max_iter:
            it += 1
            sname = state["current_step"]
            step = self.steps_map.get(sname)
            if not step:
                state["status"] = "error"
                state["summary"] = f"Unknown step: {sname}"
                break
            ss = state["steps"][sname]
            if ss["status"] in ("completed","skipped","needs_agent"):
                n = self._next_step(sname)
                if n:
                    state["current_step"] = n
                else:
                    state["status"] = "completed"
                    state["completed_at"] = datetime.now().isoformat()
                self.save_state(state)
                continue
            if ss["status"] in ("blocked","failed"):
                state["status"] = "blocked"
                break
            if ss["status"] == "waiting_approval":
                state["status"] = "waiting_approval"
                break
            if ss["status"] == "needs_agent":
                state["status"] = "needs_agent"
                break

            ss["status"] = "running"
            self.save_state(state)
            try:
                ctx = {"state":state,"step":step,"tools":self.tools,
                       "loop":self,**self.extra_context}
                result = step.maker(ctx)
                if not isinstance(result, StepResult):
                    result = StepResult(status="completed" if result else "failed",
                                        data={"raw":result})
                if result.status == "completed":
                    check_ok = True
                    if step.checker:
                        check_ok = step.checker(ctx, result.data)
                    if check_ok:
                        ss["status"] = "completed"
                        ss["output_summary"] = json.dumps(result.data, ensure_ascii=False)[:200]
                        if step.human_gate:
                            state["status"] = "waiting_approval"
                            state["blocked_reason"] = f"Step '{sname}' needs approval."
                            ss["status"] = "waiting_approval"
                            break
                        n = self._next_step(sname)
                        if n:
                            state["current_step"] = n
                        else:
                            state["status"] = "completed"
                            state["completed_at"] = datetime.now().isoformat()
                    else:
                        raise Exception("Checker did not pass")
                elif result.status == "blocked":
                    ss["status"] = "blocked"
                    state["status"] = "blocked"
                    state["blocked_reason"] = result.error or "Unknown"
                    break
                elif result.status == "skipped":
                    ss["status"] = "skipped"
            except Exception as e:
                ss["retries"] += 1
                ss["errors"].append(f"[{datetime.now().strftime('%H:%M:%S')}] {e}")
                if ss["retries"] >= step.max_retries:
                    ss["status"] = "failed"
                    state["status"] = "blocked"
                    state["blocked_reason"] = f"Step '{sname}' failed after {step.max_retries} retries"
                else:
                    ss["status"] = "retrying"
                    # Full jitter: random(0, base*2^attempt) capped at max
                    from random import uniform
                    backoff = min(2**ss["retries"] * 5, 120)
                    jittered = uniform(0, backoff)
                    time.sleep(jittered)
            finally:
                state["updated_at"] = datetime.now().isoformat()
                self.save_state(state)
        return state

    def approve(self, state):
        # Find the step that is actually waiting for approval
        waiting_step = None
        for sname in self.step_order:
            if state["steps"].get(sname, {}).get("status") == "waiting_approval":
                waiting_step = sname
                break
        if not waiting_step:
            waiting_step = state["current_step"]
        ss = state["steps"].get(waiting_step, {})
        ss["status"] = "completed"
        state["status"] = "running"
        state["blocked_reason"] = ""
        n = self._next_step(waiting_step)
        if n:
            state["current_step"] = n
        else:
            state["status"] = "completed"
            state["completed_at"] = datetime.now().isoformat()
        self.save_state(state)
        return state

    def reject(self, state, reason=""):
        ss = state["steps"].get(state["current_step"], {})
        ss["status"] = "blocked"
        state["status"] = "blocked"
        state["blocked_reason"] = f"Rejected: {reason}" if reason else "Rejected by human"
        self.save_state(state)
        return state

    def advance(self, state):
        """After agent executes a blocked step, mark it completed and continue."""
        sname = state["current_step"]
        ss = state["steps"].get(sname, {})
        ss["status"] = "completed"
        state["status"] = "running"
        state["blocked_reason"] = ""
        n = self._next_step(sname)
        if n:
            state["current_step"] = n
        else:
            state["status"] = "completed"
            state["completed_at"] = datetime.now().isoformat()
        state["updated_at"] = datetime.now().isoformat()
        self.save_state(state)
        return state

def cron_tick(loop):
    state = loop.load_state()
    if state["status"] in ("completed","error"):
        new_state = loop._default_state()
        new_state["started_at"] = state["started_at"]
        return new_state
    if state["status"] in ("blocked","waiting_approval"):
        return state
    return loop.run()
