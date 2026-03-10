# Labor-Recruit 项目记忆

> 最后更新：2026-03-09

---

project_type: production
status: 暂停

---

## ⚡ 当前任务

```
状态：v1.1 已完成开发代码，暂停中

v1.1 开发进度：
  ✅ P0-1: Customer 模型 + API
  ✅ P0-2: Project 增加 customer_id
  ✅ P0-3: Candidate 增加 in_talent_pool/tags
  ✅ P0-4: 线索池 API
  ✅ P0-5: 人才库 API
  ✅ P1-1: 客户管理页面
  ✅ P1-2: 项目表单增加客户选择
  ✅ P1-3: 线索池页面
  ✅ P1-4: 线索导入（重复检测）
  ✅ P1-5: 人才库页面
  ✅ P2-1: 人才标签管理

下次继续时说：继续 v1.1 或 启动测试

待实现：
  [ ] 数据库迁移
  [ ] 后端/前端测试
  [ ] P2-2: 自动入库规则
```

---

## 项目概述

| 项目 | 信息 |
|------|------|
| **路径** | `D:\coding\labor-recruit` |
| **GitHub** | https://github.com/SwordImmortal/labor-recruit |
| **类型** | production（正式项目） |
| **技术栈** | Vue 3 + TS + FastAPI + MySQL |
| **业务** | RPO/BPO 招聘管理系统 |

---

## 已完成模块

| 模块 | 状态 | 完成日期 |
|------|:----:|----------|
| 用户认证 | ✅ | 2026-03-08 |
| 候选人管理 | ✅ | 2026-03-08 |
| 项目管理 | ✅ | 2026-03-09 |
| 入职管理 | ✅ | 2026-03-09 |
| 渠道管理 | ✅ | 2026-03-09 |
| 用户管理 | ✅ | 2026-03-09 |
| 字典管理 | ✅ | 2026-03-09 |
| 工作台 | ✅ | 2026-03-09 |
| 候选人详情页优化 | ✅ | 2026-03-09 |
| 数据导出功能 | ✅ | 2026-03-09 |

---

## 开发阶段

| 阶段 | 内容 | 状态 |
|------|------|:----:|
| MVP v1.0 | 核心招聘流程 | ✅ |
| P1 优化 | 体验优化 | ✅ |
| v1.1 | 客户管理/线索池/人才库 | 🔜 |
| v1.2 | 结算管理/报表/权限 | 📋 |

---

## 启动命令

### 后端 (端口 8000)
```bash
cd D:\coding\labor-recruit\backend
python main.py
```

### 前端 (端口 5173)
```bash
cd D:\coding\labor-recruit\frontend
npm run dev
```

### 访问地址
| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| API 文档 | http://localhost:8000/docs |

---

## 用户偏好

- **语言**: 中文沟通
- **工作流**: Plan → TDD → Review
- **称呼**: 叫用户"爹地"

---

## 项目结构

```
labor-recruit/
├── backend/          # FastAPI 后端
│   ├── app/api/      # API 路由
│   ├── app/models/   # 数据模型
│   └── main.py       # 入口
├── frontend/         # Vue 3 前端
│   └── src/views/    # 页面
├── docs/             # 需求文档
├── scripts/          # 工具脚本
├── PROJECT_MEMORY.md # 本文件
└── CHECKLIST.md      # 详细清单
```
