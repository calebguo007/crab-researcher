# CrabRes — Todo

> Last updated: 2026-04-04
> Status: Agent 架构完成，核心问题是无法与真实世界交互

---

## 核心问题

实测发现 Agent 不做研究只反复问问题。原因：工具链路未跑通，Tavily 未配，执行器只生成不执行。
**大脑 85 分，手脚 20 分。下一步全部聚焦"接上手脚"。**

---

## P0：让 Agent 能看到和做到（从聊天机器人 → 真 Agent）

- [ ] 配通 Tavily API Key，在 Render env vars 中设置
- [ ] 端到端验证：用户输入产品 → Agent 搜索 → 专家分析 → 输出策略（不再反复追问）
- [ ] 接通 X/Twitter API（OAuth 授权，读帖子数据 + 写发布）
- [ ] `write_post` 升级：生成文案 → 用户确认 → 真正发布到 X
- [ ] Trust Level 实际落地（Level 1 建议 / Level 2 确认发布 / Level 3 自主发布）
- [ ] Playwright 工具升级：截图 → 多模态 LLM 理解（替代 HTML 解析）
- [ ] Growth Daemon 闭环：发布 → 追踪数据 → 打分 → 更新记忆

## P1：对话体验

- [ ] 去掉模板化开场白（"您好，根据您提供的..."），直接做事
- [ ] 拿到产品名/竞品名就立刻搜索，不反复确认
- [ ] 修复 Agent 重复发送相同消息的 bug
- [ ] 确保专家对话在前端正确展示（SSE expert_thinking 事件）

## P2：数据平台接入

- [ ] Google Analytics / Search Console API
- [ ] Stripe / LemonSqueezy API（收入数据）
- [ ] MCP 生态打通（用户自接 Notion/Slack/GitHub 等）

## P3：视觉与体验打磨

- [ ] 6 个剩余生物体详细 SVG
- [ ] 替换 emoji → 定制线性图标
- [ ] 替换 SVG 生物体 → 精致插画素材
- [ ] 暗色模式完善
- [ ] 字体加载优化（preload / 本地字体）

## P4：增长

- [ ] 买域名（crabres.com 或 crabres.ai）
- [ ] 第一条 X/Twitter thread："Building an AI growth agent"
- [ ] 用 CrabRes 自己增长 CrabRes（dogfooding）
- [ ] 10 个免费 beta 用户招募
- [ ] Product Hunt 发布准备

---

## 已完成

### Agent 引擎（完成）
- [x] ReAct Loop（8轮迭代，3级恢复）
- [x] 13 专家 Agent + 18 知识模块
- [x] 圆桌三阶段（Intelligence → Debate → Playbooks）
- [x] Moonshot 直连 + OpenRouter 备选 + 4 Tier 成本控制
- [x] 8 个工具（search/scrape/deep_scrape/browse/social_search/competitor/write_post/write_email）
- [x] Growth Daemon（30min 心跳）+ Growth Dream（午夜蒸馏）
- [x] 记忆系统（7+1 类）+ Context Engine + Prompt Cache
- [x] Harness Engineering（产品类型→专家权重矩阵 + 依赖图）
- [x] Deep Strategy Session + Mood Sensing（5维）
- [x] MCP 客户端 + Playwright 浏览器
- [x] 多通道通知（Discord/Slack/Telegram/飞书）
- [x] JWT + OAuth + 安全审计（13 项 P0）
- [x] 31 pytest 测试 + 上下文压缩 + 工具重试
- [x] 语言检测（CJK → 中文回复）
- [x] 强制圆桌触发 + 循环 Fallback + CITE RESEARCH

### 前端（完成）
- [x] Landing + Compare + Auth + Onboarding + Surface + Chat + Plan + Settings
- [x] 生物体系统（10 物种 × 10 情绪，SVG + 60fps 动画）
- [x] SSE 流式 + 专家 @ 提及 + 圆桌可视化
- [x] 设计系统 v2 + ErrorBoundary + 共享 Icons
- [x] 9 个按钮接活 + Landing 虚假数据清理

### 基础设施（完成）
- [x] Vercel + Render 自动部署
- [x] Neon PostgreSQL + pgvector
