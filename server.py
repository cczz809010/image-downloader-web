#!/usr/bin/env python3
"""
简单的 HTTP 服务器 - 用于测试和本地运行
"""

from app import app

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🌐 网站图片下载器 - 本地服务器")
    print("=" * 60)
    print("  访问地址: http://localhost:8888")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=8888, debug=True)
