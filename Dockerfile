# 多阶段构建Dockerfile

# 第一阶段：构建前端应用
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端项目文件
COPY server-info-frontend/package*.json ./
RUN npm ci

COPY server-info-frontend/ ./
RUN npm run build

# 第二阶段：构建后端应用
FROM python:3.12-alpine AS backend-builder

WORKDIR /app/backend

# 安装系统依赖
RUN apk add --no-cache gcc musl-dev linux-headers

# 复制后端项目文件
COPY server-info-api/pyproject.toml ./
RUN pip install --no-cache-dir -e .

COPY server-info-api/ ./

# 第三阶段：生产环境
FROM python:3.12-alpine

WORKDIR /app

# 安装运行时依赖
RUN apk add --no-cache \
    libstdc++ \
    && addgroup -S app && adduser -S app -G app

# 从构建阶段复制已安装的Python包
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=backend-builder /usr/local/bin/ /usr/local/bin/

# 复制后端应用代码
COPY server-info-api/ ./backend/

# 从前端构建阶段复制构建好的静态文件到后端静态文件夹
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 创建非root用户并设置权限
RUN chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 启动命令 - 同时服务前端静态文件和后端API
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]