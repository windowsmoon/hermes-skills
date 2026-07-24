#!/usr/bin/env python3
"""
大码女装视频混剪路由器
根据用户选择的模式，准备对应的环境和配置
"""
import os, sys, json, subprocess

def get_jianying_draft_dir():
    """获取剪映草稿目录"""
    home = os.path.expanduser("~")
    possible_paths = [
        os.path.join(home, "AppData", "Local", "JianyingPro", "User Data", "Projects", "com.lveditor.draft"),
        os.path.join(home, "AppData", "Local", "JianyingPro", "Drafts"),
        os.path.join(home, "AppData", "Local", "JianyingPro", "User Data", "Projects", "com.lveditor.drafts"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return possible_paths[0]

def check_env(mode):
    """检查对应模式的工具是否就绪"""
    status = {}
    
    if mode in ["simple", "全面"]:
        # Check jianying-editor-skill
        skill_dir = os.path.expanduser("~/AppData/Local/hermes/skills/jianying-editor-skill")
        status["jianying-editor-skill"] = {
            "installed": os.path.exists(skill_dir),
            "path": skill_dir
        }
    
    if mode in ["full", "全面"]:
        # Check pyJianYingDraft
        try:
            import pyJianYingDraft
            status["pyJianYingDraft"] = {"installed": True, "version": "0.3.0"}
        except ImportError:
            status["pyJianYingDraft"] = {"installed": False}
    
    if mode == "paid":
        status["NemoVideo"] = {"installed": False, "note": "需要付费套餐"}
    
    return status

def main():
    print("===== 大码女装视频混剪路由器 =====")
    print()
    print("请选择模式:")
    print("  1. 简单混剪 - 快速出片 (jianying-editor-skill)")
    print("  2. 全面混剪 - 精细控制 (pyJianYingDraft)")  
    print("  3. 花费混剪 - NemoVideo (需付费)")
    print()
    
    mode = input("输入 1/2/3: ").strip()
    
    modes = {"1": "simple", "2": "full", "3": "paid"}
    mode_name = modes.get(mode, "simple")
    
    print(f"\n选中的模式: {mode_name}")
    print(f"剪映草稿目录: {get_jianying_draft_dir()}")
    
    env = check_env(mode_name)
    print(f"\n环境检查: {json.dumps(env, indent=2, ensure_ascii=False)}")
    
    print("\n✅ 准备就绪！请把素材放到一个文件夹，然后告诉我路径。")

if __name__ == "__main__":
    main()