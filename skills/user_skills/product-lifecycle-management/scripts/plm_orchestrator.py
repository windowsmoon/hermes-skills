#!/usr/bin/env python3
"""产品生命周期 状态机 — 4阶段18步状态管理"""
import json, os, sys, time
STATE_FILE = os.path.expanduser("~/.product-lifecycle-state.json")
PIPELINE = {
    "phase1_strategic_insight": {"name": "战略洞察期 (0→1)", "goal": "找方向、选战场、判生死", "steps": [
        {"id":"p1s1","name":"产品愿景","skill":"product-vision","output":"Mission Statement"},
        {"id":"p1s2","name":"SWOT分析","skill":"swot-analysis","output":"优劣势威胁矩阵"},
        {"id":"p1s3","name":"市场细分","skill":"market-segments","output":"目标细分市场"},
        {"id":"p1s4","name":"竞品分析","skill":"competitor-analysis","output":"竞品定位空白点"},
        {"id":"p1s5","name":"用户调研","skill":"analyze-feature-requests","output":"未满足痛点清单"},
        {"id":"p1s6","name":"用户画像","skill":"user-personas","output":"典型Persona"}]},
    "phase2_definition": {"name":"定义聚焦期 (立项)","goal":"确定唯一核心指标和差异化锚点","steps":[
        {"id":"p2s1","name":"战略画布","skill":None,"output":"价值曲线图"},
        {"id":"p2s2","name":"定位","skill":"positioning-ideas","output":"核心差异化口号"},
        {"id":"p2s3","name":"北极星指标","skill":"north-star-metric","output":"长期健康指标"},
        {"id":"p2s4","name":"机会树","skill":"opportunity-solution-tree","output":"可拆解指标+杠杆"},
        {"id":"p2s5","name":"功能优先级","skill":"prioritize-features","output":"MVP Backlog"}]},
    "phase3_execution":{"name":"落地执行期","goal":"拆解任务、保障质量、合规避险","steps":[
        {"id":"p3s1","name":"写PRD","skill":"create-prd","output":"8段式PRD文档"},
        {"id":"p3s2","name":"用户故事","skill":"user-stories","output":"开发任务拆分"},
        {"id":"p3s3","name":"Sprint规划","skill":"sprint-plan","output":"迭代计划"},
        {"id":"p3s4","name":"测试场景","skill":"test-scenarios","output":"验收用例集"},
        {"id":"p3s5","name":"NDA/隐私终审","skill":"draft-nda","output":"合规文件"}],"delegate_to":["engineering-director","qa-director"]},
    "phase4_growth":{"name":"上市增长期","goal":"把产品推出去，形成自增长闭环","steps":[
        {"id":"p4s1","name":"GTM策略","skill":"gtm-strategy","output":"定价/渠道/推广计划"},
        {"id":"p4s2","name":"增长飞轮","skill":"growth-loops","output":"留存自传播正循环"}]}}
PHASE_ORDER = ["phase1_strategic_insight","phase2_definition","phase3_execution","phase4_growth"]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"status":"not_started","current_phase":0,"current_step":0,"completed_steps":[],"outputs":{}}

def save_state(s):
    s["updated_at"]=time.time()
    with open(STATE_FILE,'w') as f:
        json.dump(s,f,indent=2,ensure_ascii=False)

def cmd_start(name):
    s={"status":"running","product_name":name,"current_phase":0,"current_step":0,"completed_steps":[],"started_at":time.time(),"outputs":{}}
    save_state(s)
    p=PHASE_ORDER[0]; step=PIPELINE[p]["steps"][0]
    print(f"✅ 启动: {name}\\n📌 {PIPELINE[p]['name']} → {step['name']}\\n💡 产出: {step['output']}\\n📖 技能: pm-skills/{step['skill']}" if step['skill'] else f"💡 通用方法论")

def cmd_status():
    s=load_state()
    if s["status"]=="not_started": print("📭 无进行中产品。使用 start <产品名>"); return
    p=PHASE_ORDER[s["current_phase"]]; pd=PIPELINE[p]; step=pd["steps"][s["current_step"]]
    total=sum(len(ph["steps"]) for ph in PIPELINE.values())
    print(f"📊 {s['product_name']}\\n  阶段 {s['current_phase']+1}/4 • 步骤 {s['current_step']+1}/{len(pd['steps'])}\\n  已完成 {len(s['completed_steps'])}/{total} 步\\n  当前: {pd['name']} → {step['name']}\\n  产出: {step['output']}")
    if s["outputs"]: print(f"  已产出: {list(s['outputs'].keys())}")

def cmd_next():
    s=load_state()
    if s["status"]!="running": print("❌ 无进行中产品"); return
    p=PHASE_ORDER[s["current_phase"]]; pd=PIPELINE[p]; cs=pd["steps"][s["current_step"]]
    s["completed_steps"].append(cs["id"])
    if s["current_step"]+1<len(pd["steps"]):
        s["current_step"]+=1; save_state(s); ns=pd["steps"][s["current_step"]]
        print(f"✅ 完成 {cs['name']}\\n🚀 下一步: {ns['name']}\\n💡 产出: {ns['output']}"+(f"\\n📖 技能: pm-skills/{ns['skill']}" if ns["skill"] else ""))
    else:
        s["current_step"]=0; s["current_phase"]+=1
        if s["current_phase"]>=len(PHASE_ORDER): s["status"]="completed"; save_state(s); print(f"🎉 {s['product_name']} 全生命周期完成！")
        else:
            save_state(s); np=PIPELINE[PHASE_ORDER[s["current_phase"]]]
            print(f"✅ 阶段完成: {pd['name']}\\n🚀 进入: {np['name']}\\n🎯 {np['goal']}\\n📌 第一步: {np['steps'][0]['name']}")
            if np.get("delegate_to"): print(f"🤝 委托: {', '.join(np['delegate_to'])}")

def cmd_rollback():
    s=load_state()
    if s["status"]!="running": print("❌ 无进行中产品"); return
    p=PHASE_ORDER[s["current_phase"]]; pd=PIPELINE[p]
    if s["current_step"]>0:
        sid=pd["steps"][s["current_step"]-1]["id"]
        if sid in s["completed_steps"]: s["completed_steps"].remove(sid)
        s["current_step"]-=1; save_state(s)
        print(f"🔙 回退到: {pd['steps'][s['current_step']]['name']}")
    elif s["current_phase"]>0:
        s["current_phase"]-=1; pp=PIPELINE[PHASE_ORDER[s["current_phase"]]]
        s["current_step"]=len(pp["steps"])-1; save_state(s)
        print(f"🔙 回退到上阶段: {pp['steps'][-1]['name']}")
    else: print("❌ 已在第一步")

def cmd_list():
    for pk in PHASE_ORDER:
        pd=PIPELINE[pk]; print(f"\\n📁 {pd['name']}\\n   🎯 {pd['goal']}")
        for st in pd["steps"]:
            sk=f" [技能: {st['skill']}]" if st["skill"] else ""
            print(f"   {st['id']}: {st['name']} → {st['output']}{sk}")
        if pd.get("delegate_to"): print(f"   🤝 委托: {', '.join(pd['delegate_to'])}")

def cmd_set_output(k,v):
    s=load_state(); s["outputs"][k]=v; save_state(s); print(f"📝 已记录: {k}")

def cmd_reset():
    if os.path.exists(STATE_FILE): os.remove(STATE_FILE)
    print("🔄 已重置")

if __name__=="__main__":
    if len(sys.argv)<2: print("用法: plm_orchestrator.py <命令> [参数...]\\n命令: start|status|next|rollback|step|list|reset|set-output"); sys.exit(1)
    c=sys.argv[1]
    {"start":lambda:cmd_start(" ".join(sys.argv[2:])),"status":cmd_status,"next":cmd_next,"rollback":cmd_rollback,"step":lambda:cmd_step(sys.argv[2])if len(sys.argv)>2 else None,"list":cmd_list,"reset":cmd_reset,"set-output":lambda:cmd_set_output(sys.argv[2]," ".join(sys.argv[3:]))if len(sys.argv)>3 else None}.get(c,lambda:print(f"未知: {c}"))()