#!/usr/bin/env python3
"""
便捷运行脚本
"""

import os
import sys
import subprocess
import platform

def run_backend():
    """运行后端服务器"""
    print("Starting backend server...")
    # 使用项目根目录
    subprocess.run([sys.executable, "backend/src/api/server.py"])

def run_frontend():
    """运行前端开发服务器"""
    print("Starting frontend development server...")
    os.chdir("frontend")
    subprocess.run(["npm", "run", "dev"], shell=True)

def run_dev():
    """同时运行前后端"""
    print("Starting development servers...")
    
    if platform.system() == "Windows":
        # Windows系统
        subprocess.Popen(["start", "cmd", "/k", "cd backend\\src\\api && python server.py"], shell=True)
        subprocess.Popen(["start", "cmd", "/k", "cd frontend && npm run dev"], shell=True)
    else:
        # Unix系统
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", "cd backend/src/api && python server.py; exec bash"])
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", "cd frontend && npm run dev; exec bash"])

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行搜索Agent应用")
    parser.add_argument("--backend", action="store_true", help="只运行后端")
    parser.add_argument("--frontend", action="store_true", help="只运行前端")
    
    args = parser.parse_args()
    
    if args.backend:
        run_backend()
    elif args.frontend:
        run_frontend()
    else:
        run_dev()
        print("\n✨ 开发服务器已启动!")
        print("🔗 前端: http://localhost:5173")
        print("🔗 后端: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("\n按 Ctrl+C 停止服务器") 