# 蓝领招聘与项目运营系统

[![Vue 3](https://img.shields.io/badge/Vue-3.4+-4FC08D?logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?logo=mysql)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

蓝领招聘与项目运营系统（RPO/BPO），支持候选人全流程管理、项目供人进度追踪、入离职管理等功能。

## 功能特性

- 🔐 **用户权限** - 多角色权限管理（管理员/主管/专员）
- 👥 **候选人管理** - 线索录入、状态跟进、人才库
- 📊 **项目管理** - 供人目标、进度追踪、双状态模型
- 📋 **入职管理** - 入职登记、在职管理、离职补招
- 📱 **移动端适配** - 响应式设计，支持手机/平板/PC

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | 3.4+ |
| 构建工具 | Vite | 5.0+ |
| UI框架 | Ant Design Vue | 4.1+ |
| 状态管理 | Pinia | 2.1+ |
| 后端框架 | FastAPI | 0.109+ |
| ORM | SQLAlchemy | 2.0+ |
| 数据库 | MySQL | 8.0+ |

## 项目结构

```
labor-recruit/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/             # API 接口
│   │   ├── components/      # 公共组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # 状态管理
│   │   ├── router/          # 路由
│   │   └── utils/           # 工具函数
│   └── package.json
│
├── backend/                  # 后端项目
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── services/        # 业务逻辑
│   │   └── core/            # 核心配置
│   ├── alembic/             # 数据库迁移
│   └── requirements.txt
│
├── docs/                     # 文档
├── requirements/             # 原始需求
└── README.md
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.11+
- MySQL 8.0+

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 修改 .env 文件中的数据库连接信息

# 创建数据库
mysql -u root -p -e "CREATE DATABASE labor_recruit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 启动服务
python main.py
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

## 默认账号

首次启动需要手动注册管理员账号，或通过 API 创建：

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","phone":"13800138000","role":"admin"}'
```

## 开发进度

### MVP v1.0（进行中）

| 模块 | 状态 |
|------|:----:|
| 用户登录认证 | ✅ |
| 用户管理 | 🚧 |
| 候选人管理 | ✅ |
| 项目管理 | ✅ |
| 入职管理 | 🚧 |
| 渠道管理 | 🚧 |
| 字典管理 | 🚧 |

## 相关文档

- [需求设计文档](./docs/需求设计-v1.0.md)
- [原始需求](./requirements/)

## License

MIT
