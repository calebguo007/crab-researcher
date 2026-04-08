# CrabRes 渠道激活操作手册

> 晚上按这个顺序操作

---

## 一、飞书 Bot 激活（15 分钟）

### 步骤 1：创建飞书应用
1. 打开 https://open.feishu.cn/app
2. 点击「创建企业自建应用」
3. 应用名称：`CrabRes`
4. 应用描述：`AI 增长策略 Agent`
5. 图标：用螃蟹 emoji 或上传 logo
6. 点击「创建」

### 步骤 2：开启机器人能力
1. 进入应用 → 左侧菜单「添加应用能力」
2. 点击「机器人」→ 开启
3. 机器人名称：`CrabRes`

### 步骤 3：配置事件订阅
1. 左侧菜单「事件订阅」
2. 请求网址 URL 填：
   ```
   https://crab-researcher.onrender.com/api/feishu/event
   ```
3. 点击「添加事件」，搜索并添加：
   - `im.message.receive_v1`（接收消息）
4. 保存

### 步骤 4：配置权限
1. 左侧菜单「权限管理」
2. 搜索并开通以下权限：
   - `im:message:send_as_bot`（以机器人身份发消息）
   - `im:message`（获取消息内容）
   - `im:chat:readonly`（获取群信息）
3. 点击「批量开通」

### 步骤 5：获取凭证
1. 左侧菜单「凭证与基础信息」
2. 复制 `App ID` 和 `App Secret`

### 步骤 6：配置环境变量
在 `.env` 文件末尾加：
```
FEISHU_APP_ID=你的App ID
FEISHU_APP_SECRET=你的App Secret
```

在 Render Dashboard → crab-researcher → Environment 加同样两个变量。

### 步骤 7：发布应用
1. 左侧菜单「版本管理与发布」
2. 创建版本 → 填写版本说明
3. 点击「申请发布」
4. 管理员审批后生效

### 步骤 8：测试
1. 在飞书中搜索 `CrabRes` 机器人
2. 发送：`我做了一个 AI 简历工具`
3. 应该收到研究中的提示，然后是增长建议

---

## 二、OpenClaw 微信接入（10 分钟）

### 前提
- 你的微信已收到 ClawBot 灰度测试邀请
- 已安装 OpenClaw CLI

### 步骤 1：确认 SKILL.md 已在仓库
已经创建好了：`/crab-researcher/SKILL.md`
GitHub 地址：`https://github.com/velmavalienteqejimu22-jpg/crab-researcher/blob/main/SKILL.md`

### 步骤 2：在 OpenClaw 中添加 CrabRes Skill
```bash
# 方法 A：通过 URL 添加
openclaw skill add --url https://crab-researcher.onrender.com/api/openclaw/invoke --name crabres

# 方法 B：通过 GitHub 添加
openclaw skill add velmavalienteqejimu22-jpg/crab-researcher
```

### 步骤 3：微信中测试
1. 打开微信 → 找到 ClawBot
2. 发送：`@crabres 分析一下 AI 简历工具的增长机会`
3. ClawBot 会调用 CrabRes Skill → 返回分析结果

### 步骤 4（可选）：发布到 ClawHub
```bash
openclaw skill publish crabres
```
这样所有 OpenClaw 用户都能搜到并使用 CrabRes。

---

## 三、MCP 发布到 Smithery（5 分钟）

### 步骤 1
1. 打开 https://smithery.ai
2. 注册/登录
3. 点击「Submit Server」

### 步骤 2
填写：
- Name: `crabres`
- Description: `AI Growth Strategy Agent — Research competitors, validate direction, create growth plans`
- URL: `https://crab-researcher.onrender.com/api/mcp`
- Transport: HTTP
- Categories: Marketing, Growth, Research

### 步骤 3
提交后等审核（通常 1-2 天）。

---

## 四、CLI 发布到 npm（5 分钟）

### 步骤 1
```bash
cd crab-researcher/cli
npm login  # 用你的 npm 账号
npm publish
```

### 步骤 2：测试
```bash
npx crabres help
npx crabres login
npx crabres chat "I built a SaaS tool"
```

---

## 五、Render 环境变量检查清单

确保 Render Dashboard 有以下所有变量：

```
# 已有的
DATABASE_URL=...
JWT_SECRET=...
MOONSHOT_API_KEY=...
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
FEISHU_WEBHOOK_URL=...
FEISHU_WEBHOOK_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
DEBUG=false

# 新增的
FEISHU_APP_ID=（飞书应用的 App ID）
FEISHU_APP_SECRET=（飞书应用的 App Secret）
```

---

*按顺序操作，每步都有验证方法。遇到问题随时问我。*
