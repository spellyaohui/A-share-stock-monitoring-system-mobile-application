# 📈 A股股票监测系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org)
[![uni-app](https://img.shields.io/badge/uni--app-Vue3-blue.svg)](https://uniapp.dcloud.io)

一个完整的 A 股股票买卖监控解决方案，支持 PC 端、移动端（H5/Android/iOS）独立访问，统一后端服务。

## ✨ 功能特性

| 功能模块 | 说明 |
|---------|------|
| 🔍 股票搜索 | 支持代码精确搜索、名称模糊搜索 |
| 💰 价格监测 | 最低价、最高价预警通知 |
| 📊 涨跌幅监测 | 日涨跌幅超阈值预警 |
| ⚡ 实时行情 | WebSocket 实时推送股票数据 |
| 📈 K线图表 | 日K、周K、月K，支持 MA 均线指标 |
| 🔔 通知对接 | Webhook API 通知接口 |
| 🌙 深色模式 | 支持跟随系统自动切换深色/浅色主题 |
| 🔄 热更新 | 集成 uni-upgrade-center 支持 APP 热更新 |

## 🖼️ 系统截图

<!-- 可以添加截图 -->
```
PC端：专业的股票监测管理界面
移动端：简洁的移动端操作体验
```

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        Nginx 反向代理                              │
│                      domain.com:80/443                           │
└──────┬───────────────────────┬───────────────────────┬───────────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   PC端      │         │   移动端    │         │   后端API   │
│   Vue3      │         │   uni-app   │         │   FastAPI   │
│  端口 3001  │         │  端口 3002  │         │  端口 8000  │
└─────────────┘         └─────────────┘         └──────┬──────┘
                                                      │
                                      ┌───────────────┼───────────────┐
                                      ▼               ▼               ▼
                              ┌───────────┐   ┌───────────┐   ┌───────────┐
                              │   MySQL   │   │ WebSocket │   │  AkShare  │
                              │ 端口 3306 │   │ 实时推送  │   │  数据源   │
                              └───────────┘   └───────────┘   └───────────┘
```

## 🛠️ 技术栈

### 后端 (stock-monitor-backend)
- **框架**：FastAPI + Uvicorn
- **数据库**：MySQL 8.0+ (异步驱动 aiomysql)
- **ORM**：SQLAlchemy 2.0 (异步模式)
- **认证**：JWT (python-jose + passlib)
- **数据源**：AkShare (A股免费数据)
- **定时任务**：APScheduler

### PC 前端 (stock-monitor-pc)
- **框架**：Vue 3 + TypeScript
- **构建**：Vite 5
- **UI 库**：Element Plus
- **图表**：ECharts
- **状态管理**：Pinia

### 移动端 (stock-monitor-mobile)
- **框架**：uni-app + Vue 3 + TypeScript
- **构建**：Vite 5 + @dcloudio/vite-plugin-uni
- **状态管理**：Pinia
- **升级中心**：uni-upgrade-center

## 📦 项目结构

```
├── stock-monitor-backend/    # Python 后端
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic 模式
│   │   ├── services/         # 业务逻辑
│   │   └── core/             # 核心模块
│   └── requirements.txt
├── stock-monitor-pc/         # Vue 3 PC 前端
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 通用组件
│   │   ├── store/            # Pinia 状态
│   │   └── api/              # API 封装
│   └── package.json
├── stock-monitor-mobile/     # uni-app 移动端
│   ├── pages/                # 页面
│   ├── components/           # 组件
│   ├── store/                # 状态管理
│   └── uni_modules/          # uni-app 插件
├── init_mysql.sql            # 数据库初始化脚本
└── README.md
```

## 🚀 快速开始

### 部署方式

- [本地开发环境部署](#本地开发环境)
- [宝塔面板部署](docs/宝塔面板部署指南.md)（推荐新手）

### 环境要求

| 组件 | 版本要求 |
|-----|---------|
| Python | 3.11+ |
| Node.js | 18.0+ |
| MySQL | 8.0+ |
| HBuilderX | 最新版（移动端打包需要） |

### 本地开发环境

### 1. 克隆项目

```bash
git clone https://github.com/spellyaohui/A-share-stock-monitoring-system-mobile-application.git
cd A-share-stock-monitoring-system-mobile-application
```

### 2. 数据库初始化

```bash
mysql -u root -p < init_mysql.sql
```

**默认账号**: `admin` / `admin`

> ⚠️ 首次登录后请立即修改密码！

### 3. 后端部署

```bash
cd stock-monitor-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 启动服务
python run.py
```

### 4. PC 端部署

```bash
cd stock-monitor-pc

npm install
npm run dev      # 开发模式，访问 http://localhost:3001
npm run build    # 生产构建
```

### 5. 移动端部署

#### H5 模式

```bash
cd stock-monitor-mobile

npm install
npm run dev:h5   # 开发模式，访问 http://localhost:3002
npm run build:h5 # 生产构建
```

#### APP 打包（Android/iOS）

1. 使用 [HBuilderX](https://www.dcloud.io/hbuilderx.html) 打开 `stock-monitor-mobile` 目录
2. 菜单：发行 → 原生App-云打包
3. 选择平台，配置证书，点击打包

## ⚙️ 配置说明

### 后端环境变量 (.env)

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=stock_monitor

# JWT 配置
SECRET_KEY=your-secret-key-at-least-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### 移动端 API 地址配置

修改 `stock-monitor-mobile/utils/request.ts`：

```typescript
const BASE_URL = 'http://your-server-ip:8000'
```

## 📱 移动端特性

### 深色模式

移动端支持跟随系统自动切换深色/浅色主题：

- `manifest.json` 配置 `darkmode: true`
- `theme.json` 定义主题变量
- `pages.json` 使用 `@变量名` 引用

> 注意：APP 平台需要重新打包自定义基座才能生效

### APP 升级中心

集成 uni-upgrade-center，支持：

- 整包更新（APK/IPA）
- wgt 热更新
- 静默更新
- 强制更新

配置步骤：

1. 绑定 uniCloud 服务空间
2. 上传云函数
3. 部署 uni-admin 管理后台
4. 在后台发布新版本

## 🔧 端口分配

| 服务 | 端口 |
|------|------|
| 后端 API | 8000 |
| PC 前端 | 3001 |
| 移动端 H5 | 3002 |
| MySQL | 3306 |

## 📖 API 文档

启动后端后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

## 🙏 致谢

- [AkShare](https://github.com/akfamily/akshare) - A股数据源
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Vue.js](https://vuejs.org/) - 前端框架
- [uni-app](https://uniapp.dcloud.io/) - 跨平台框架
- [Element Plus](https://element-plus.org/) - UI 组件库

## 📞 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/spellyaohui/A-share-stock-monitoring-system-mobile-application/issues)。

---

⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！
