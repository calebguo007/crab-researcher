# CrabRes 部署与 Git 指南

> 给新同学的快速上手文档。5 分钟搞懂怎么改代码、怎么部署。

---

## 一、项目结构

```
/Users/guoyi/Desktop/market/crab-researcher/
├── app/                  # 后端 Python (FastAPI)
│   ├── agent/            # Agent 引擎（核心）
│   ├── api/              # REST API 端点
│   ├── core/             # 配置、数据库、安全
│   ├── channels/         # 飞书/OpenClaw 渠道
│   ├── services/         # v1 老服务（可忽略）
│   └── main.py           # 应用入口
├── frontend/             # 前端 React + TypeScript
│   ├── src/
│   │   ├── pages/        # 7 个页面
│   │   ├── components/   # 组件
│   │   ├── lib/          # API 层、专家配置
│   │   └── index.css     # 设计系统
│   └── package.json
├── cli/                  # CLI 工具 (Node.js)
├── mcp/                  # MCP Server 配置
├── .env                  # 环境变量（不进 Git）
├── requirements.txt      # Python 依赖
└── render.yaml           # Render 部署配置
```

---

## 二、Git 仓库

```
仓库地址: https://github.com/velmavalienteqejimu22-jpg/crab-researcher.git
分支: main（唯一分支）
```

---

## 三、部署架构

```
用户浏览器
    ↓
Vercel（前端 React SPA）    ← git push 自动部署
    ↓ API 请求
Render（后端 FastAPI）       ← git push 自动部署
    ↓
Neon（PostgreSQL 数据库）    ← 云托管，无需部署
```

| 服务 | 平台 | URL | 触发方式 |
|------|------|-----|---------|
| **前端** | Vercel | https://crab-researcher.vercel.app | push 到 main 自动部署 |
| **后端** | Render | https://crab-researcher.onrender.com | push 到 main 自动部署 |
| **数据库** | Neon | 见 .env 中 DATABASE_URL | 云托管，自动 |
| **API 文档** | Render | https://crab-researcher.onrender.com/docs | 自动生成 |

**关键：push 到 GitHub main 分支 = 前端和后端同时自动部署。无需手动操作。**

---

## 四、日常开发流程

### 改代码 → 部署上线

```bash
# 1. 进入项目目录
cd /Users/guoyi/Desktop/market/crab-researcher

# 2. 查看改了什么
git status

# 3. 添加所有改动
git add -A

# 4. 提交（写清楚改了什么）
git commit -m "fix: 修复了什么 / feat: 新增了什么"

# 5. 推送到 GitHub（会自动触发 Vercel + Render 部署）
git push
```

就这 5 步。push 之后等 1-3 分钟，线上就更新了。

### 只改了前端？

一样的流程。Vercel 会检测 `frontend/` 目录变化自动构建。

### 只改了后端？

一样的流程。Render 会检测 Python 文件变化自动重启。

---

## 五、部署前检查（重要！）

### 前端编译检查

```bash
cd /Users/guoyi/Desktop/market/crab-researcher/frontend
npx tsc -b --noEmit
```

**如果有报错，不要 push！** TypeScript 编译失败 = Vercel 部署失败。

### 后端语法检查

```bash
cd /Users/guoyi/Desktop/market/crab-researcher
python3 -c "import app.main"
```

能 import 成功说明没有语法错误。

---

## 六、环境变量

### 本地开发

本地环境变量在 `.env` 文件中（不进 Git）。如果需要重建：

```bash
cp .env.example .env
# 然后填入真实的 API Key
```

### 线上环境变量

| 平台 | 在哪配 |
|------|--------|
| **Render（后端）** | https://dashboard.render.com → crab-researcher-api → Environment |
| **Vercel（前端）** | https://vercel.com → crab-researcher → Settings → Environment Variables |

**线上必须配的变量（后端 Render）：**

```
DATABASE_URL          # Neon PostgreSQL 连接串
JWT_SECRET            # JWT 签名密钥（强随机值）
OPENROUTER_API_KEY    # 主力 LLM（必须）
TAVILY_API_KEY        # 搜索 API（必须）
FIRECRAWL_API_KEY     # JS 渲染抓取（可选）
MOONSHOT_API_KEY      # 降级 LLM（可选）
GOOGLE_CLIENT_ID      # Google OAuth
GOOGLE_CLIENT_SECRET
GITHUB_CLIENT_ID      # GitHub OAuth
GITHUB_CLIENT_SECRET
FEISHU_WEBHOOK_URL    # 飞书通知（可选）
FEISHU_WEBHOOK_SECRET
FRONTEND_URL          # = https://crab-researcher.vercel.app
```

**线上必须配的变量（前端 Vercel）：**

```
VITE_API_BASE         # = https://crab-researcher.onrender.com/api
```

---

## 七、常见问题

### Q: push 了但前端没变化？
1. 去 Vercel Dashboard 看构建日志，是否有 TypeScript 报错
2. 本地先跑 `npx tsc -b --noEmit` 确认编译通过

### Q: push 了但后端没变化？
1. Render Free Plan 会休眠，第一次请求需要 30-60 秒冷启动
2. 去 Render Dashboard 看 Deploy 日志

### Q: 后端接口 404？
1. 检查路径是否以 `/api` 开头（所有路由都有这个前缀）
2. 后端 API 文档：https://crab-researcher.onrender.com/docs

### Q: OAuth 登录失败？
1. 确认 Render 环境变量中 GOOGLE_CLIENT_ID/SECRET 已配置
2. Google Cloud Console 中 redirect URI 要包含 `https://crab-researcher.onrender.com/api/oauth/google/callback`
3. GitHub OAuth App 中 callback URL 要包含 `https://crab-researcher.onrender.com/api/oauth/github/callback`

### Q: 怎么看后端日志？
Render Dashboard → crab-researcher-api → Logs

### Q: 怎么看前端构建日志？
Vercel Dashboard → crab-researcher → Deployments → 点击最新部署

### Q: 数据库怎么看？
Neon Console：https://console.neon.tech
数据库名：neondb

---

## 八、本地开发（可选）

如果想在本地跑起来调试：

### 后端

```bash
cd /Users/guoyi/Desktop/market/crab-researcher
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
# 后端跑在 http://localhost:8002
# API 文档在 http://localhost:8002/docs
```

### 前端

```bash
cd /Users/guoyi/Desktop/market/crab-researcher/frontend
npm install
npm run dev
# 前端跑在 http://localhost:3000
# 会自动代理 /api 请求到 localhost:8002
```

---

## 九、commit 消息规范

```
feat: 新功能          例: feat: add expert roundtable dialog
fix: 修 bug          例: fix: language detection for CJK
refactor: 重构       例: refactor: simplify Surface page
style: 样式调整      例: style: improve landing chat preview
chore: 杂务          例: chore: remove unused dependencies
docs: 文档           例: docs: add deployment guide
```
