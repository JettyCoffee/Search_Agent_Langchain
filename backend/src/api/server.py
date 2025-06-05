#!/usr/bin/env python3
"""
FastAPI服务器 - 提供搜索Agent的API接口
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 设置代理
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 添加项目根目录到Python路径
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入本地Agent
from backend.src.agent.graph import SearchAgent

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智能搜索Agent API",
    description="提供基于LangGraph的智能搜索服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体的来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局Agent实例
agent = None

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    max_iterations: Optional[int] = 3

class SearchResponse(BaseModel):
    """搜索响应模型"""
    success: bool
    query: str
    answer: Optional[str] = None
    error: Optional[str] = None
    search_results: Optional[Dict[str, Any]] = None
    iterations: Optional[int] = None
    timestamp: str = None

@app.on_event("startup")
async def startup_event():
    """启动时初始化Agent"""
    global agent
    try:
        agent = SearchAgent()
        logger.info("Search Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Search Agent: {e}")
        raise

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能搜索Agent API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "health": "/api/health",
            "websocket": "/ws"
        }
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": agent is not None
    }

@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """执行搜索"""
    if not agent:
        logger.error("Agent not initialized")
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"开始处理搜索请求: {request.query}")
        logger.debug(f"搜索参数: max_iterations={request.max_iterations}")
        
        # 运行Agent前的状态记录
        logger.debug("准备调用Agent搜索方法")
        
        # 运行Agent
        logger.debug("开始执行Agent.search()")
        result = agent.search(request.query, max_iterations=request.max_iterations)
        logger.debug(f"Agent.search()执行完成，返回结果长度: {len(str(result)) if result else 0}")
        
        # 构建响应
        response = SearchResponse(
            success=True,
            query=request.query,
            answer=result,
            iterations=request.max_iterations,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"搜索成功完成: {request.query}")
        logger.debug(f"完整响应对象: {response.dict()}")
        return response
        
    except Exception as e:
        logger.error(f"搜索过程发生错误: {str(e)}", exc_info=True)
        return SearchResponse(
            success=False,
            query=request.query,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，支持流式响应"""
    await websocket.accept()
    
    try:
        while True:
            # 接收查询
            data = await websocket.receive_json()
            query = data.get("query", "")
            max_iterations = data.get("max_iterations", 3)
            
            if not query:
                await websocket.send_json({
                    "type": "error",
                    "message": "Query is required"
                })
                continue
            
            # 发送开始信号
            await websocket.send_json({
                "type": "start",
                "query": query,
                "timestamp": datetime.now().isoformat()
            })
            
            try:
                # 执行搜索
                result = agent.search(query, max_iterations=max_iterations)
                
                # 发送结果
                await websocket.send_json({
                    "type": "result",
                    "data": {
                        "answer": result,
                        "success": True
                    }
                })
                
                # 发送完成信号
                await websocket.send_json({
                    "type": "complete",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn
    
    # 运行服务器
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 