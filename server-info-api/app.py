from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import psutil
import platform
import time
import requests
import os

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

@app.route('/api/server-info', methods=['GET'])
def get_server_info():
    # 获取操作系统信息
    # os_name = platform.system()
    # if os_name == "Linux":
    #     # 尝试获取更详细的Linux发行版信息
    #     try:
    #         with open('/etc/os-release', 'r') as f:
    #             for line in f:
    #                 if line.startswith('NAME='):
    #                     os_name = line.split('=')[1].strip().strip('"')
    #                     break
    #     except:
    #         pass
    os_name = "NixOS"
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
    
    # 获取系统启动时间
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
        response = requests.get('https://v1.hitokoto.cn', timeout=3)
        if response.status_code == 200:
            hitokoto_data = response.json()
            word_data = {
                "content": hitokoto_data.get('hitokoto', 'Talk is cheap, show me your code'),
                "author": hitokoto_data.get('from_who') or hitokoto_data.get('from', 'Linus Torvalds')
            }
    except:
        pass
    
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