# CrabRes: 从玩具到增长操作系统 — L5 闭环路线图

> **核心判断**: 如果关掉 CrabRes，用户是否真的损失钱/用户/机会？
> 当前答案：不会（只是少了个灵感工具）→ ❌ 玩具
> 目标答案：会（我少了一个帮我持续获客的系统）→ ✅ 操作系统
>
> 更新时间：2026-04-02

---

## 一、市面竞品真实闭环能力审计

调研时间：2026-04-02，覆盖 20+ 个产品。

### 分层模型

| 层级 | 定义 | 代表产品 | 能做到 | 做不到 |
|------|------|---------|--------|--------|
| **L1** | 只生成 | ChatGPT, Taskade, VenturOS | 写文案、出计划 | 不研究、不发布、不追踪 |
| **L2** | 生成+发布 | MarketOwl, NoimosAI | 写内容 + 定时发到 LinkedIn/X | 不追踪效果、不自动调整 |
| **L3** | 单渠道闭环 | ReplyAgent, Scaloom, RedReach | Reddit 自动找帖 + 自动回复 + 反封号 | 只做 Reddit，不做策略，不追踪转化 |
| **L4** | 多渠道执行 | OptaReach | LinkedIn/Reddit/X/Email 多渠道 DM + 追踪回复率 + ICP 评分 | 策略调整还需人工，不是真闭环 |
| **L5** | 闭环操作系统 | **不存在** | action→result→adjust 全链路自动 | — |

### 关键发现

1. **MarketOwl** — 能 auto-publish 到 LinkedIn/X，但不追踪每条帖子效果，不会根据 tweet_1=10 likes vs tweet_2=200 likes 自动调整方向。
2. **OptaReach** — 最接近多渠道执行，追踪回复率但不自动调整 DM 话术。
3. **ReplyAgent** — Reddit 单渠道最成熟（自动回复 + 反 shadowban），但不做策略、不跨渠道。
4. **NoimosAI** — 宣传"fully autonomous 24/7"，实际是内容生成+SEO 发布，无 action→result 闭环。

### 结论

**L5 是空白市场。** 没有任何产品做到了"定目标→拆实验→执行→记录结果→根据结果调整下一轮"的完整闭环。

**CrabRes 当前处于 L1.5**（比 ChatGPT 好——能真搜索真研究，但输出仍然是建议和文案，不是执行结果）。

---

## 二、目标架构：增长操作系统

### 当前（AI = 大脑）

```
用户 → CrabRes → 研究 + 策略 + 文案 → 用户自己复制粘贴去执行 → ??? 
```

用户得到：灵感和文案。关掉 CrabRes，他可以用 ChatGPT 替代。

### 目标（AI = 操作系统）

```
用户 → 定义目标 → CrabRes 拆成实验 → 执行 → 记录结果 → 学习规律 → 调整 → 循环
                                         ↑                                    ↓
                                         └────────────────────────────────────┘
```

用户得到：持续增长的结果。关掉 CrabRes，他的获客引擎停转。

### 五步闭环

| Step | 内容 | 举例 | 当前状态 |
|------|------|------|---------|
| **1. 定义目标** | 用户设定可量化的增长目标 | "7 天涨 1000 follower" | ✅ Onboarding 已有 |
| **2. 拆成实验** | Agent 将目标拆成可执行的实验清单 | "发 20 条 tweet、回 50 条 Reddit、DM 30 人" | ⚠️ 能拆但不够结构化 |
| **3. 执行** | 真发、真评论、真 DM（至少半自动） | 用户确认 → CrabRes 代发 | ❌ 完全缺失 |
| **4. 记录结果** | 每个 action 对应一个 result | "tweet_1→10 likes, tweet_2→200 likes, dm_1→无回复" | ❌ 完全缺失 |
| **5. 学习调整** | AI 根据结果优化下一轮策略 | "带数字标题转化率 3x，下周全用数字标题" | ❌ 完全缺失 |

---

## 三、要补的三个系统块

### 块 1: 感知层（Eyes）— 追踪 action→result

**优先级：P0（最先做，因为不依赖 OAuth 接入）**

即使用户自己手动发帖，只要把链接贴回 CrabRes，系统就能自动追踪效果。

#### 数据模型

```python
class GrowthAction:
    """一次增长实验的执行记录"""
    id: str                    # action-uuid
    experiment_id: str         # 属于哪个实验批次
    platform: str              # "reddit" / "x" / "linkedin" / "email"
    action_type: str           # "post" / "reply" / "dm" / "email"
    content_preview: str       # 发布内容的前 200 字
    url: str                   # 发布后的链接（用户贴回或自动获取）
    posted_at: float           # 发布时间
    status: str                # "pending" / "posted" / "tracked" / "failed"

class GrowthResult:
    """一次行动的效果追踪"""
    action_id: str
    tracked_at: float
    metrics: dict              # {"likes": 10, "replies": 2, "clicks": 5, "follows": 1}
    conversion: dict           # {"signups": 0, "revenue": 0} — 如果能追踪到
    notes: str                 # Agent 的分析备注

class GrowthExperiment:
    """一批实验"""
    id: str
    goal: str                  # "Get 50 signups from Reddit this week"
    hypothesis: str            # "Resume review posts in r/resumes convert 3x better than tips posts"
    actions: list[str]         # action IDs
    started_at: float
    ended_at: float | None
    conclusion: str            # Agent 总结的结论
    learnings: list[str]       # 提取的规律
```

#### 追踪机制

1. **用户贴链接回来**：在 Surface 页面或 Chat 中，用户说"我发了 https://x.com/xxx/status/123"，Agent 自动创建 GrowthAction 记录
2. **定时回查**：Growth Daemon 每 30 分钟 tick 时，对所有 status="posted" 的 action 做效果回查
   - X/Twitter：抓取 likes/retweets/replies（通过 scrape 或 API）
   - Reddit：抓取 upvotes/comments
   - LinkedIn：抓取 reactions/comments
3. **存入记忆**：结果写入 `.crabres/memory/{user_id}/execution/` 目录

#### Surface 页面展示

```
─── Growth Experiments ────────────────
┌────────────────────────────────────────┐
│  Experiment: Reddit Week 1             │
│  Goal: 50 signups from r/resumes       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                        │
│  tweet_1  "I reviewed 200 resumes..."  │
│           → 67 upvotes, 12 clicks  ✅  │
│                                        │
│  tweet_2  "5 common resume mistakes"   │
│           → 234 upvotes, 45 clicks 🔥  │
│                                        │
│  dm_1     @resume_helper               │
│           → no reply  ❌               │
│                                        │
│  dm_2     @career_coach_amy            │
│           → replied, interested  ✅    │
│                                        │
│  ─── Learning ───                      │
│  "数字标题帖 (+234) 比叙事帖 (+67)     │
│   效果 3.5x。下周全用数字标题。"       │
│                                        │
│  Total: 78 clicks → 8 signups (10.2%)  │
│  [Start next experiment →]             │
└────────────────────────────────────────┘
```

### 块 2: 执行层（Hands）— 真发、真评论、真 DM

**优先级：P1（块 1 做完后做，因为需要 OAuth）**

#### 阶段路径

```
阶段 A（现在就能做）：生成 + 一键跳转
  用户点击 → 复制内容到剪贴板 + 打开 X 发帖页面
  （当前已有，但没有追踪后续效果）

阶段 B（下一步）：半自动（用户确认 → 系统代发）
  Agent 生成内容 → Surface 显示待发清单 → 用户点"Approve"
  → CrabRes 通过 OAuth 代发 → 自动记录 URL → 自动追踪
  
阶段 C（终极）：全自动（Trust Level 4 用户）
  Agent 自动生成 + 自动发布 + 自动追踪 + 自动调整
  用户只需每周审核一次
```

#### OAuth 接入优先级

| 平台 | 难度 | ROI | 优先级 |
|------|------|-----|--------|
| X/Twitter | 中（API v2 + OAuth 2.0） | 高（indie hacker 主战场） | P0 |
| Reddit | 高（反封号复杂） | 高（转化率最好） | P1 |
| LinkedIn | 中（API 限制多） | 中 | P2 |
| Email | 低（SMTP） | 中（outreach 用） | P2 |

### 块 3: 学习层（Brain 2.0）— 根据结果调整

**优先级：P2（块 1 有数据后自然可做）**

#### 升级 GrowthDream

当前 GrowthDream 在午夜做记忆蒸馏（整理矛盾、合并重复）。升级为：

```
GrowthDream v2:

Phase 1: Orient（定向）— 和现在一样
Phase 2: Gather（采集）— 新增：收集所有 GrowthResult
Phase 3: Analyze（分析）— 新增：提取增长规律
  输入：最近 7 天的所有 action→result 数据
  输出：
    - "带数字标题帖 conversion 3.5x vs 叙事帖"
    - "周二 9am EST 发帖效果最好（avg 2.3x engagement）"  
    - "DM 中提到'看了你的帖子'回复率 5x vs 冷 DM"
    - "r/cscareerquestions 转化率 12% vs r/resumes 转化率 4%"
Phase 4: Inject（注入）— 新增：将规律注入 Coordinator prompt
  把 Phase 3 的输出存入 memory/strategy/growth_patterns.json
  Coordinator 下次调度专家时自动加载这些规律
Phase 5: Prune（修剪）— 和现在一样
```

#### Coordinator prompt 注入

```
## LEARNED GROWTH PATTERNS (from real execution data)
- Reddit: numbered-list titles get 3.5x more engagement than narrative titles
- X: tweets posted Tue 9am EST get 2.3x more engagement
- DM: mentioning their specific content gets 5x reply rate
- Subreddit ROI: r/cscareerquestions (12% CVR) >> r/resumes (4% CVR)

Use these patterns when planning the next experiment batch.
Prioritize what worked. Kill what didn't.
```

---

## 四、执行路线图

### Phase A: 感知层（本周）

| # | 任务 | 文件 | 耗时 |
|---|------|------|------|
| A1 | 新增 GrowthAction/GrowthResult/GrowthExperiment 数据模型 | `app/agent/memory/experiments.py` | 1h |
| A2 | Agent 能识别用户贴回的链接并自动创建 action | `loop.py` 的 `_maybe_save_product_info` 扩展 | 1h |
| A3 | Growth Daemon 追踪已发布帖子的效果（scrape metrics） | `daemon/__init__.py` 新增 `_scan_action_results` | 2h |
| A4 | `/api/growth/experiments` CRUD 端点 | `app/api/v2/experiments.py` | 1h |
| A5 | Surface 页面新增 Experiment 追踪卡片 | `frontend/src/pages/Surface.tsx` | 2h |
| A6 | Chat 中 Agent 能引用历史实验结果 | `loop.py` 的 `_build_context` 扩展 | 1h |

### Phase B: 半自动执行层（下周）

| # | 任务 | 文件 | 耗时 |
|---|------|------|------|
| B1 | X/Twitter OAuth 2.0 接入（发帖 + 读取 metrics） | `app/channels/twitter.py` | 3h |
| B2 | Surface "待发布"队列：Agent 生成 → 用户审核 → 一键发布 | 前端+后端 | 3h |
| B3 | 发布后自动创建 GrowthAction + 记录 URL | 联动 A2 | 1h |
| B4 | Reddit API 接入（读取帖子 metrics，先不做自动发帖） | `app/channels/reddit.py` | 2h |

### Phase C: 学习层（第三周）

| # | 任务 | 文件 | 耗时 |
|---|------|------|------|
| C1 | GrowthDream v2：从 action→result 数据中提取规律 | `engine/dream.py` 升级 | 2h |
| C2 | 规律自动注入 Coordinator prompt | `loop.py` 的 `_build_coordinator_prompt` | 30min |
| C3 | "下一轮实验"自动生成：基于规律拆出新的 action 清单 | Coordinator prompt 逻辑 | 1h |
| C4 | 周报自动生成：本周所有实验的 action→result→learning | `daemon/__init__.py` | 1h |

---

## 五、验证标准

### 最小闭环验证（Phase A 完成后）

用户手动操作：
1. 在 CrabRes 中拿到 Reddit 帖子文案
2. 自己复制粘贴发到 Reddit
3. 把帖子链接贴回 CrabRes（Chat 中或 Surface 中）
4. 24 小时后，CrabRes 自动显示：upvotes 数、comments 数、来源点击数
5. 一周后，CrabRes 自动总结："数字标题帖效果 3x，建议下周..."

**如果这个流程跑通，CrabRes 就从"灵感工具"变成了"增长追踪系统"。**

### 半自动验证（Phase B 完成后）

1. CrabRes 生成 3 条 X/Twitter 帖子
2. Surface 显示"待发布"队列
3. 用户点击 "Approve & Post"
4. CrabRes 通过 OAuth 代发
5. 自动追踪效果
6. 3 天后自动出结论

**如果这个流程跑通，CrabRes 就从"追踪系统"变成了"半自动增长引擎"。**

### 全闭环验证（Phase C 完成后）

1. 用户只说："帮我在 Reddit 涨 100 个注册"
2. CrabRes 自动拆实验、自动写帖子、等用户审核发布
3. 自动追踪效果
4. 自动总结规律
5. 自动生成下一轮实验
6. 周报自动发到飞书/邮件

**如果这个流程跑通，关掉 CrabRes 用户会真的损失获客渠道。**

---

## 六、底线原则

1. **半自动优于全自动** — 用户确认再发，不要偷偷发。Trust Level 4 才开放全自动。
2. **真数据优于假数据** — 宁可少一个 metric 也不编数据。scrape 失败就标"N/A"。
3. **一个渠道做通 > 五个渠道半吊子** — 先把 Reddit 或 X 的完整闭环做到位。
4. **每个 action 必须有 result** — 没有 result 的 action 是浪费。系统强制追踪。
5. **规律必须来自数据** — "带数字标题好" 必须有 ≥5 个数据点支撑，不是 LLM 猜的。

---

*这份文档是 CrabRes 从 30 分到 80 分的路线图。
执行计划-下一阶段.md 解决的是"看起来不错"的问题。
这份文档解决的是"真的有用"的问题。*
