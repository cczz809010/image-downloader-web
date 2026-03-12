import os
import sys

# 将当前目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify

# 创建 Flask 应用
app = Flask(__name__)

# 导入主应用的路由
try:
    from main import *
except:
    # 如果 main.py 不存在，创建一个简单的响应
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': 'Image Downloader API is running',
            'endpoints': {
                '/': 'Root',
                '/': 'This endpoint'
            }
        })

# Vercel 需要的入口函数
def handler(event, context):
    return app(event, context)

# 本地开发
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
