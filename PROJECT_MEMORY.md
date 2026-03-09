# Labor-Recruit 项目记忆

> 最后更新：2026-03-09 | MVP v1.0 ✅ 完成

---

## ⚡ 当前任务

```
状态：待测试验收

优先级 P1（体验优化）：
  [ ] 候选人详情页 - 跟进记录时间线
  [ ] 数据导出 - Excel 导出功能
  [ ] 表单验证优化
  [ ] 搜索增强 - 日期范围筛选

下次继续时说：启动测试 或 继续开发 P1
```

---

## 📋 项目概况

| 项目 | 信息 |
|------|------|
| **路径** | `D:\coding\labor-recruit` |
| **GitHub** | https://github.com/SwordImmortal/labor-recruit |
| **技术栈** | Vue 3 + TS + FastAPI + MySQL |
| **业务** | RPO/BPO 招聘管理系统 |

---

## ✅ 已完成功能

| 模块 | 功能 |
|------|------|
| 工作台 | 统计数据、最近候选人 |
| 候选人 | 搜索/新增/跟进/状态流转 |
| 项目 | 新增/编辑/进度展示 |
| 入职 | 入职登记/离职登记 |
| 渠道 | 新增/编辑/启用停用 |
| 用户 | 新增/编辑/重置密码 |
| 字典 | 类型管理/字典项管理 |

---

## 🚀 快速启动

```bash
# 后端 (端口 8000)
cd D:\coding\labor-recruit\backend
python main.py

# 前端 (端口 5173)
cd D:\coding\labor-recruit\frontend
npm run dev
```

**访问地址**：
- 前端：http://localhost:5173
- API 文档：http://localhost:8000/docs

---

## 📂 项目结构

```
labor-recruit/
├── backend/          # FastAPI 后端
│   ├── app/api/      # API 路由 ✅
│   ├── app/models/   # 数据模型 ✅
│   └── main.py       # 入口
├── frontend/         # Vue 3 前端
│   └── src/views/    # 页面 ✅
├── docs/             # 需求文档
├── scripts/          # 工具脚本
├── PROJECT_MEMORY.md # 本文件
└── CHECKLIST.md      # 详细清单
```

---

## 📅 开发计划

| 阶段 | 状态 | 内容 |
|------|:----:|------|
| MVP v1.0 | ✅ | 核心招聘流程 |
| P1 优化 | 🔜 | 体验优化（详情页/导出/验证） |
| v1.1 | 📋 | 客户管理/线索池/人才库 |
| v1.2 | 📋 | 结算管理/报表/权限 |

---

## 📝 最近更新

**2026-03-09**
- ✅ MVP v1.0 开发完成
- ✅ 工作台/项目/入职/渠道/用户/字典管理
- ✅ 代码推送到 GitHub
