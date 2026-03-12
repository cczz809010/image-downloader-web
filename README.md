# 🖼️ 网站图片下载器 - Web版

一个美观易用的Web界面网站图片批量下载工具。

## 功能特点

- ✅ 美观的渐变色UI设计
- ✅ 一键下载网站所有图片
- ✅ 实时显示下载进度
- ✅ 下载历史记录
- ✅ 文件夹管理
- ✅ 在线预览下载的图片
- ✅ 响应式设计，支持移动端

## 安装依赖

```bash
cd web_downloader
pip install -r requirements.txt
```

## 运行

```bash
python3 app.py
```

启动后访问：`http://localhost:5000`

## 使用方法

1. 在浏览器中打开 `http://localhost:5000`
2. 在输入框中输入网站URL
3. 点击"开始下载"按钮
4. 等待下载完成
5. 点击文件夹卡片查看下载的图片
6. 可以点击图片在新标签页打开或下载

## 目录结构

```
web_downloader/
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖
├── templates/
│   └── index.html        # 网页模板
└── downloads/            # 下载的图片保存目录
```

## API接口

- `GET /` - 主页面
- `POST /api/download` - 下载图片
- `GET /api/history` - 获取下载历史
- `GET /api/folders` - 获取文件夹列表
- `GET /api/folder/<folder_name>` - 获取文件夹中的文件
- `GET /downloads/<folder_name>/<filename>` - 下载单个文件

## 技术栈

- 后端：Flask
- 前端：原生 HTML + CSS + JavaScript
- HTML解析：BeautifulSoup4
- HTTP请求：requests

## 截图预览

- 渐变色背景，现代化UI
- 实时进度条显示
- 卡片式布局
- 图片网格预览

## 注意事项

- 请遵守目标网站的robots.txt规则
- 请勿用于非法用途
- 建议适当控制下载频率

## License

MIT
