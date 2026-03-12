#!/usr/bin/env python3
"""
网站图片下载器 - Vercel Serverless版本
"""

import os
import re
import time
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for

app = Flask(__name__, template_folder='../templates')

# 配置
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/downloads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 下载历史（使用临时存储，生产环境建议使用数据库）
DOWNLOAD_HISTORY = []


class ImageDownloader:
    @staticmethod
    def _get_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    @staticmethod
    def _is_valid_image(url):
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
        parsed_url = urlparse(url)

        for ext in image_extensions:
            if parsed_url.path.lower().endswith(ext):
                return True

        if any(keyword in parsed_url.path.lower() for keyword in ['image', 'img', 'photo', 'picture', 'pic']):
            return True

        return False

    @staticmethod
    def download_images(url, folder_name):
        """下载网站所有图片"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # 创建输出文件夹
            output_folder = os.path.join(UPLOAD_FOLDER, folder_name)
            os.makedirs(output_folder, exist_ok=True)

            # 获取网页内容
            response = requests.get(url, headers=ImageDownloader._get_headers(), timeout=15)
            response.raise_for_status()

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取图片URL
            image_urls = set()

            # 查找所有图片标签
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-original')
                if src:
                    if ImageDownloader._is_valid_image(src):
                        image_urls.add(src)

            # 查找背景图片
            for element in soup.find_all(style=True):
                style = element.get('style', '')
                matches = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', style)
                for match in matches:
                    if ImageDownloader._is_valid_image(match):
                        image_urls.add(match)

            # 下载图片（限制最多下载50张，避免超时）
            results = []
            downloaded = 0
            failed = 0
            max_images = 50

            for index, img_url in enumerate(list(image_urls)[:max_images], 1):
                try:
                    if not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)

                    img_response = requests.get(img_url, headers=ImageDownloader._get_headers(), timeout=10)
                    img_response.raise_for_status()

                    # 获取扩展名
                    content_type = img_response.headers.get('content-type', '')
                    ext_map = {
                        'image/jpeg': '.jpg',
                        'image/png': '.png',
                        'image/gif': '.gif',
                        'image/bmp': '.bmp',
                        'image/webp': '.webp',
                        'image/svg+xml': '.svg',
                        'image/x-icon': '.ico'
                    }
                    ext = ext_map.get(content_type, os.path.splitext(urlparse(img_url).path)[1] or '.jpg')

                    # 保存图片
                    filename = f"image_{index:04d}{ext}"
                    filepath = os.path.join(output_folder, filename)

                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)

                    results.append({
                        'index': index,
                        'filename': filename,
                        'size': len(img_response.content),
                        'url': img_url,
                        'status': 'success'
                    })
                    downloaded += 1

                except Exception as e:
                    results.append({
                        'index': index,
                        'filename': '',
                        'size': 0,
                        'url': img_url,
                        'status': 'failed',
                        'error': str(e)
                    })
                    failed += 1

                time.sleep(0.05)

            return {
                'success': True,
                'folder_name': folder_name,
                'downloaded': downloaded,
                'failed': failed,
                'total': min(len(image_urls), max_images),
                'results': results
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


@app.route('/')
def index():
    return render_template('index.html', history=DOWNLOAD_HISTORY)


@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'success': False, 'error': 'URL不能为空'})

    # 生成文件夹名
    domain = urlparse(url).netloc.replace('www.', '') if url.startswith('http') else url
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = f"images_{domain}_{timestamp}"

    # 开始下载
    result = ImageDownloader.download_images(url, folder_name)

    if result['success']:
        # 添加到历史记录
        history_item = {
            'url': url,
            'folder_name': folder_name,
            'downloaded': result['downloaded'],
            'failed': result['failed'],
            'total': result['total'],
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        DOWNLOAD_HISTORY.insert(0, history_item)

        # 只保留最近5条记录
        if len(DOWNLOAD_HISTORY) > 5:
            DOWNLOAD_HISTORY.pop()

    return jsonify(result)


@app.route('/api/history')
def get_history():
    return jsonify(DOWNLOAD_HISTORY)


@app.route('/api/folders')
def get_folders():
    folders = []
    try:
        for item in os.listdir(UPLOAD_FOLDER):
            folder_path = os.path.join(UPLOAD_FOLDER, item)
            if os.path.isdir(folder_path):
                files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                folders.append({
                    'name': item,
                    'file_count': len(files)
                })
        folders.sort(key=lambda x: x['name'], reverse=True)
    except Exception as e:
        pass
    return jsonify(folders)


@app.route('/api/folder/<folder_name>')
def get_folder_files(folder_name):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        return jsonify({'success': False, 'error': '文件夹不存在'})

    files = []
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'url': url_for('download_file', folder_name=folder_name, filename=filename)
            })
    return jsonify({'success': True, 'files': files})


@app.route('/downloads/<folder_name>/<filename>')
def download_file(folder_name, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder_name), filename)
