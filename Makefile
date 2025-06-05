# Makefile for Search Agent

.PHONY: install install-backend install-frontend dev backend frontend clean

# 安装所有依赖
install: install-backend install-frontend

# 安装后端依赖
install-backend:
	cd backend && pip install -r requirements.txt

# 安装前端依赖
install-frontend:
	cd frontend && npm install

# 同时运行前后端开发服务器
dev:
	@echo "Starting backend and frontend development servers..."
	@start cmd /k "cd backend\src\api && python server.py"
	@start cmd /k "cd frontend && npm run dev"

# 只运行后端
backend:
	cd backend/src/api && python server.py

# 只运行前端
frontend:
	cd frontend && npm run dev

# 构建前端
build-frontend:
	cd frontend && npm run build

# 清理
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/node_modules
	rm -rf frontend/dist 