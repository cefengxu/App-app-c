# CrawlerSaaS 网站

这是一个基于 Flask 的网络爬虫 SaaS 服务网站。

## 功能特点

- 清爽简约的界面设计
- 基于邮箱验证码的登录系统
- 用户仪表盘
- API 密钥管理
- 使用统计
- 响应式设计

## 技术栈

- Python 3.8+
- Flask 3.0.0
- HTML5
- CSS3
- JavaScript (原生)

## 安装步骤

1. 克隆项目：
```bash
git clone [项目地址]
cd crawler-saas
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行项目：
```bash
python app.py
```

访问 http://localhost:5000 查看网站。

## 项目结构

```
.
├── app.py              # Flask 应用主文件
├── requirements.txt    # 项目依赖
├── static/            # 静态文件
│   ├── css/          # CSS 文件
│   ├── js/           # JavaScript 文件
│   └── images/       # 图片文件
└── templates/         # HTML 模板
    ├── base.html     # 基础模板
    ├── index.html    # 首页
    ├── login.html    # 登录页
    ├── dashboard.html # 仪表盘
    └── ...           # 其他页面
```

## 开发说明

- 主色调采用薄荷绿，营造清新的视觉效果
- 采用响应式设计，适配各种设备
- 使用 Flask 作为后端框架，确保轻量级和高性能
- 前端采用原生 JavaScript，避免框架依赖

## 待开发功能

- [ ] API 文档页面
- [ ] 博客系统
- [ ] 关于页面
- [ ] 多语言支持
- [ ] 更多的仪表盘功能 