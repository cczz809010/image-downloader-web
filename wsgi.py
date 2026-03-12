"""
WSGI 入口文件 - 适配 Vercel
"""

from app import app as application

if __name__ == '__main__':
    application.run()
