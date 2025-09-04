# server_info_pannel
展示服务器信息的面板页面，包括操作系统信息、CPU使用率、内存使用情况、磁盘空间、系统运行时间、每日一言等。

![](./image.png)

# Docker 部署指南

## 项目结构

这是一个包含前后端的服务器信息面板应用：
- 前端：Vue 3 + TypeScript + Vite
- 后端：Python Flask API

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 构建并启动容器
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker 直接运行

```bash
# 构建镜像
docker build -t server-info-app .

# 运行容器
docker run -d -p 8080:8080 \
  -v /:/host:ro \
  --name server-info-app \
  server-info-app
```

## 访问应用

应用启动后，可以通过以下地址访问：
- 前端界面：http://localhost:8080
- API接口：http://localhost:8080/api/server-info

## 功能特性

- ✅ 实时显示服务器操作系统信息
- ✅ CPU使用率监控
- ✅ 内存使用情况显示
- ✅ 磁盘空间监控
- ✅ 系统运行时间统计
- ✅ 每日一言功能（Hitokoto API）
- ✅ 跨域请求支持
- ✅ 响应式前端界面

## 配置说明

### 环境变量

- `FLASK_ENV`: 运行环境（production/development）
- `FLASK_APP`: Flask应用入口文件（默认为app.py）

### 挂载卷

容器需要挂载主机根目录（只读）来获取系统信息：
```yaml
volumes:
  - /:/host:ro
```

## 开发模式

如果需要开发模式，可以分别启动前后端：

### 前端开发
```bash
cd server-info-frontend
npm install
npm run dev
```

### 后端开发
```bash
cd server-info-api
uv venv
source .venv/bin/activate
pip install -e .
python app.py
```

## 生产部署建议

1. **使用反向代理**：建议使用 Nginx 作为反向代理
2. **配置SSL**：为生产环境启用 HTTPS
3. **监控日志**：设置日志轮转和监控
4. **资源限制**：为容器设置适当的资源限制
5. **备份策略**：定期备份重要数据

## 故障排除

### 权限问题
如果无法读取系统信息，可能需要调整容器权限：
```yaml
# 在docker-compose.yml中添加（仅限开发环境）
privileged: true
```

### 端口冲突
如果8080端口被占用，可以修改映射端口：
```yaml
ports:
  - "3000:8080"  # 主机端口:容器端口
```

### 构建失败
确保所有依赖文件存在：
- server-info-api/pyproject.toml
- server-info-frontend/package.json

## 技术支持

如有问题，请检查：
1. Docker 和 Docker Compose 版本
2. 系统资源是否充足
3. 网络连接是否正常