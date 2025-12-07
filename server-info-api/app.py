from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import psutil
import platform
import time
import requests
import os
from datetime import datetime

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

@app.route('/api/server-info', methods=['GET'])
def get_server_info():
    # 获取操作系统信息
    os_name = platform.system()
    # 尝试获取更详细的Linux发行版信息
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('NAME='):
                    os_name = line.split('=')[1].strip().strip('"')
                    break
    except:
        pass

    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # 获取内存使用信息（单位：MB）
    memory = psutil.virtual_memory()
    memory_usage = {
        "total": round(memory.total / (1024 * 1024), 2),
        "used": round(memory.used / (1024 * 1024), 2)
    }
    
    # 获取所有磁盘分区的整体使用信息（单位：GB）
    disk_usage = {"total": 0, "used": 0}
    try:
        total_size = 0
        total_used = 0
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_size += usage.total
                total_used += usage.used
            except:
                continue
        
        disk_usage = {
            "total": round(total_size / (1024 * 1024 * 1024), 2),
            "used": round(total_used / (1024 * 1024 * 1024), 2)
        }
    except:
        # 如果获取所有分区失败，使用根目录作为备选
        disk = psutil.disk_usage('/')
        disk_usage = {
            "total": round(disk.total / (1024 * 1024 * 1024), 2),
            "used": round(disk.used / (1024 * 1024 * 1024), 2)
        }
    
    # 获取系统启动时间（优先使用环境变量 BOOT_TIME）
    boot_time = None
    boot_time_env = os.getenv('BOOT_TIME')
    
    # 去除首尾的引号和空白字符
    if boot_time_env:
        boot_time_env = boot_time_env.strip().strip('"').strip("'")
    
    if boot_time_env:
        try:
            # 尝试解析为 Unix 时间戳（支持整数和浮点数）
            boot_time = float(boot_time_env)
            app.logger.info(f"从环境变量 BOOT_TIME 读取到时间戳: {boot_time}")
        except ValueError:
            # 如果不是数字，尝试解析为时间字符串
            try:
                # 尝试解析 ISO 格式时间字符串
                boot_time_dt = datetime.fromisoformat(boot_time_env.replace('Z', '+00:00'))
                boot_time = boot_time_dt.timestamp()
                app.logger.info(f"从环境变量 BOOT_TIME 解析时间字符串: {boot_time_env} -> {boot_time}")
            except Exception as e:
                app.logger.warning(f"无法解析环境变量 BOOT_TIME 的值 '{boot_time_env}': {e}，将使用系统启动时间")
                boot_time = psutil.boot_time()
    else:
        # 如果没有设置环境变量，使用系统启动时间
        boot_time = psutil.boot_time()
    
    uptime_seconds = time.time() - boot_time
    
    # 计算天、小时、分钟、秒
    days = int(uptime_seconds // (24 * 3600))
    uptime_seconds %= (24 * 3600)
    hours = int(uptime_seconds // 3600)
    uptime_seconds %= 3600
    minutes = int(uptime_seconds // 60)
    seconds = int(uptime_seconds % 60)
    
    uptime = {
        "day": days,
        "hour": hours,
        "minute": minutes,
        "second": seconds
    }
    
    # 获取hitokoto名言
    word_data = {"content": "Talk is cheap, show me your code", "author": "Linus Torvalds"}
    try:
        app.logger.info("正在请求 hitokoto API...")
        response = requests.get('https://v1.hitokoto.cn', timeout=3)
        app.logger.info(f"收到响应，状态码: {response.status_code}")
        if response.status_code == 200:
            try:
                hitokoto_data = response.json()
                app.logger.info(f"成功解析 JSON，数据: {hitokoto_data}")
                word_data = {
                    "content": hitokoto_data.get('hitokoto', 'Talk is cheap, show me your code'),
                    "author": hitokoto_data.get('from_who') or hitokoto_data.get('from', 'Linus Torvalds')
                }
                app.logger.info(f"更新后的 word_data: {word_data}")
            except Exception as e:
                app.logger.error(f"解析 hitokoto API 响应 JSON 时出错: {e}")
                app.logger.error(f"响应内容: {response.text[:200]}")
        else:
            app.logger.warning(f"获取 hitokoto 名言失败，HTTP 状态码: {response.status_code}")
            app.logger.warning(f"响应内容: {response.text[:200]}")
    except requests.exceptions.Timeout:
        app.logger.error("获取 hitokoto 名言超时（超过 3 秒）")
    except requests.exceptions.ConnectionError as e:
        app.logger.error(f"获取 hitokoto 名言连接错误: {e}")
    except Exception as e:
        app.logger.error(f"获取 hitokoto 名言时出错: {type(e).__name__}: {e}")
    
    # 构建响应数据
    response_data = {
        "operating_system": os_name,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "uptime": uptime,
        "word": word_data
    }
    
    return jsonify(response_data)

# 添加前端静态文件服务路由
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)