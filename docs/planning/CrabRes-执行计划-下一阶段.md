# CrabRes 执行计划 — 从 30 分到 80 分

> 写给下一个对话的 AI：读完这份文档，你就能理解产品全貌、当前差距、要做什么。
> 更新时间：2026-04-04

---

## 一、产品是什么

**CrabRes** = AI 增长策略 Agent。帮独立开发者/初创公司验证产品方向 + 制定可执行增长计划。

**核心差异化**：不是给建议，是**做研究 + 写内容 + 追踪效果**。13 个专家组成圆桌会议，各自有性格和专业视角，会争论、会互相挑战，最终由首席增长官综合出策略。

**技术栈**：FastAPI + React + OpenRouter(LLM) + Tavily(搜索) + Neon(PG) + Vercel(前端) + Render(后端)

**代码路径**：`/Users/guoyi/Desktop/market/crab-researcher/`

---

## 二、设计哲学（必须遵守）

### 三个关键词：可爱、聪明、可信

- **可爱**：Duolingo 证明了可爱让人每天打开。CrabRes 不是冷冰冰的 SaaS 工具。
- **聪明**：可爱是外壳，真正帮你赚钱是内核。
- **可信**：indie hacker 被太多 AI 营销工具骗过。30 秒内证明自己不是垃圾。

### 视觉风格：Refined Illustration

```
Notion 的插画气质 + Linear 的排版克制 + Stripe 的信任感 + Duolingo 的性格

不是：像素风❌ 3D写实❌ 纯扁平❌ 赛博朋克❌

色板：
  品牌色: #0EA5E9 (天空蓝) + #F97316 (暖橙/螃蟹色)
  亮色默认（indie hacker 白天工作多）

字体（规划指定，当前用 Space Grotesk+DM Sans，可以调整）：
  标题: Geist Sans
  正文: Inter
  代码: Geist Mono

图标：定制线性图标（不用 emoji），1.5px 粗线，圆角端点
  ⚠️ 当前全用 emoji 替代，等图片素材好了替换
```

### 品牌精神：Growth War Room（增长作战室）

用户进来不是在"聊天"，是在**指挥一支增长特种部队**。每次对话都是一场作战行动。

---

## 三、当前状态 vs 规划目标（差距分析）

### 后端 Agent 引擎

| 维度 | 规划 | 现状 | 要做什么 |
|------|------|------|---------|
| **专家对话** | 2-3 个专家各自独立分析 → 互相辩论 → Coordinator 综合 | Coordinator 一个人做所有决策，偶尔调一个专家 | **重写 AgentLoop._think()**: 改为先并行调度 2-4 个相关专家，收集各自输出，再让 Coordinator 综合。每个专家输出都 yield 给前端 |
| **专家间冲突** | 专家有性格冲突（经济学家 vs 增长官、SEO 专家 vs 社媒专家） | 专家 prompt 有性格但从不交互 | **在 Coordinator prompt 中注入其他专家的观点**，要求指出分歧和综合理由 |
| **圆桌三阶段** | Phase 1: 市场刺穿 → Phase 2: 心理博弈 → Phase 3: 终审输出 | 无阶段概念 | **在 LoopPhase 中实现圆桌阶段**，每个阶段调度不同专家组合 |
| **语言** | 用户用什么语言就回什么语言 | 已修复：添加了 CJK 检测 + 语言提醒 | ✅ 已完成 |

### 前端页面

| 页面 | 规划描述 | 现状 | 差距 |
|------|---------|------|------|
| **Landing** | 30 秒交互 Demo + 嵌入式产品演示 + 真实社会证明 | 有 Demo 输入框（setTimeout 模拟）+ 群聊预览（已改为 app 窗口风格）| 缺真实演示视频/GIF、缺真实用户 logo、对比页要更有冲击力 |
| **Surface** | 极简 calm：螃蟹 + 3 数字 + 2-3 任务 + 发现。信息密度极低 | Growth Hunter 区域太复杂（3 个文案生成器），破坏 calm 感 | **砍掉 Growth Hunter**，回归规划的极简设计。任务卡片加左侧颜色条 |
| **Chat/War Room** | 群聊流 + 专家圆桌默认折叠可展开 + 工作状态实时展示 | 已改为 War Room 布局（左栏圆桌+右栏对话）| 核心问题是**后端不返回真正的专家对话**，前端空有框架没有内容 |
| **Plan** | 阶段进度条 + 策略卡片带真实数据（upvotes/visits/signups）| 有框架但数据全靠 API（API 目前返回空）| 需要 Agent 真正生成计划后存入 memory，Plan 页才有内容 |
| **Settings** | 螃蟹展示区 + 配饰收集 + 项目切换 | 基本功能有了但视觉粗糙 | 等图片素材 |
| **Onboarding** | 3 步 + 螃蟹表情变化 + 专家组装动画 | 功能完整，视觉还行 | 螃蟹表情是 SVG 固定的，等图片素材后替换 |

### 视觉/交互

| 维度 | 规划 | 现状 | 要做什么 |
|------|------|------|---------|
| **图标** | 定制线性图标，和螃蟹风格统一 | emoji 替代 | 等用户生图，替换所有 emoji → 真实图标 |
| **生物体** | 精致插画，8 种表情状态 | SVG 画的 4 种物种 + 6 个通用圆形 | 等用户生图，替换 SVG → 真实 3D 渲染 |
| **动画** | framer-motion 级别，专家头像脉冲 + 神经元连接线 | CSS animation 基础级 | 圆桌组件已用 SVG 动画重写。其他页面动画可以后续优化 |
| **字体加载** | preload + font-display: swap | Google Fonts 阻塞渲染 | 改为 `<link rel="preload">` 或本地字体 |

---

## 四、执行优先级（2026-04-04 重新排序）

> **核心判断转变**：之前 P0 是"让专家对话更好看"，现在 P0 是"让 Agent 能做事"。
> 原因：实测发现 Agent 不做研究只反复追问用户，因为工具链路根本没通。
> 再好的圆桌也不能弥补"搜不到信息"的问题。

### P0：接上手脚 — 让 Agent 能与真实世界交互

**问题实录**（2026-04-04 真实用户对话）：
```
用户: accio是竞品
Agent: 您在开发的产品和accio有什么不同点吗？
用户: 帮助vibecoder增长的营销产品
Agent: 我需要知道你在做什么才能帮你。给我一句话就行——（重复第二次）
```
Agent 没有搜索 accio，没有分析竞品，反复问已经回答过的问题。

**根因**：
1. Tavily API Key 未配 → 搜索工具不可用 → Agent 只能问用户要信息
2. `write_post`/`write_email` 只生成文案不执行 → 无法闭环
3. Playwright 只抓 HTML → 大多数现代网站拿不到有效内容
4. Growth Daemon 的行动追踪无数据源 → 闭环是断的

**执行清单**：

| # | 任务 | 改动范围 | 工时 |
|---|------|---------|------|
| 1 | 配通 Tavily API Key + 在 Render env vars 设置 | 环境配置 | 10min |
| 2 | 端到端验证：输入产品名 → 搜索 → 专家分析 → 输出 | 测试 | 1h |
| 3 | 修复 Agent 重复消息 + 去掉模板开场白 | Coordinator prompt | 0.5d |
| 4 | 接通 X/Twitter API（OAuth + 读写） | `app/agent/tools/` 新增 | 1d |
| 5 | `write_post` 升级：生成 → 确认 → 发布 + Trust Level | `tools/` + `trust.py` | 1d |
| 6 | Playwright 截图 + 多模态 LLM 理解 | `tools/browse_website.py` | 0.5d |
| 7 | Daemon 闭环：发布 → 24h 拉数据 → 打分 → 更新记忆 | `daemon/` + `growth_log.py` | 1d |

**验收标准**：用户说"我做了一个帮 vibecoder 增长的工具，accio 是竞品"，Agent 在 60 秒内返回 accio 的产品分析 + 差异化建议，不追问任何已提供的信息。

### P1：对话体验

**目标**：Agent 不像客服机器人，像一个真正在帮你做事的同事。

- 去掉"您好，根据您提供的产品信息"式开场白
- 拿到产品名/竞品名就立刻行动（搜索→分析→输出）
- 信息不足时只问**最关键的一个问题**，不列 5 条清单
- 专家对话在前端正确展示（SSE expert_thinking 事件）

### P2：数据平台接入

- Google Analytics / Search Console API → 真实流量数据
- Stripe / LemonSqueezy API → 真实收入数据
- MCP 生态打通 → 用户自接 Notion/Slack/GitHub

### P3：视觉打磨

- 替换 emoji → 定制线性图标
- 替换 SVG 生物体 → 精致插画素材
- 字体优化 + 暗色模式完善

---

## 五、关键设计参考文档

这些文档在 `/Users/guoyi/Desktop/market/` 下，包含完整的设计规范：

| 文档 | 内容 |
|------|------|
| `CrabRes-UI-UX-完整设计方案.md` | 每个页面的 ASCII 线框图 + 设计细节 + 碰壁防护 |
| `CrabRes-专家圆桌实时对谈设计.md` | 圆桌三阶段脚本 + 心理学钩子 + 动画方案 |
| `CrabRes-架构终稿.md` | 为什么要圆桌而非单 Agent + Claude Code 学到的设计 |
| `CrabRes-13专家人格化Prompt.md` | 每个专家的性格、冲突点、金句 |
| `CrabRes-Multi-Agent-专家体系设计.md` | 专家调度逻辑、Token 分配 |
| `CrabRes-视觉资源生图清单.md` | 104 张素材的完整提示词（用户正在生成） |
| `CrabRes-BuildInPublic策略.md` | 发布和增长策略 |

---

## 六、已完成的工作（本轮对话）

### 安全审计 + 修复（13 项 P0 全部完成）
- JWT_SECRET 自动生成、XSS 修复、MCP/OpenClaw 速率限制
- Session TTL + 用户隔离、CORS 限制、SSL 验证
- OAuth token fragment 传递、飞书 HMAC 修复
- 分享卡片签名 token

### 冗余清理（14 项）
- 删除 demo.py、n8n-workflows/、project-architecture.html
- 删除未用 imports、EYES 常量、colorShift
- 移除 alembic/redis/multipart/passlib 依赖
- 创建 .dockerignore、更新 .gitignore

### 前端修复
- Surface hunterLoading key bug
- 所有 9 个无功能按钮接活
- Landing 虚假数据清理、年份动态化
- CreatureRenderer rAF 性能重写
- ErrorBoundary、共享 Icons、prefers-reduced-motion

### 架构改进
- TrustManager 集成到 AgentLoop
- GrowthDream.distill() 接入 daemon midnight boundary
- 语言检测 + 强制回复语言规则

### 前端视觉升级
- RoundtableSimulation SVG 重写
- Landing 群聊预览 → app 窗口风格
- Chat → Growth War Room 布局
- animationFillMode 修复

---

## 七、给下一个对话的指令

1. **先读这份文档**，理解全局
2. **最高优先级：让 Agent 能做事**。配 Tavily Key → 跑通搜索 → 验证端到端。不要碰 UI，不要加新专家，不要优化 prompt，直到 Agent 能真正搜索并返回竞品分析
3. **第二优先级：接 X/Twitter API**。这是 indie hacker 主战场，让 Agent 能读数据 + 写帖子
4. **对话风格：像同事不像客服**。去掉模板开场白，拿到信息就行动，不反复确认
5. **保持 creative** — 不要做出"普通 AI 项目"的感觉
6. **测试编译** — 每次改动后 `npx tsc -b --noEmit` 确认无误
7. **推送前先验证** — 不要推出 TypeScript 编译错误的代码
