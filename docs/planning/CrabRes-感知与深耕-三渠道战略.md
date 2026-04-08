# CrabRes: 感知与深耕 — X / 小红书 / Reddit 三渠道战略

> **两个核心直觉：**
> 1. 不是完全替代营销公司，但要让用户感觉到"在往那个方向靠拢"
> 2. OpenClaw 火的原因是"Agent 能感知物理世界"——CrabRes 也需要这种存在感
>
> **Demo 阶段深覆盖三个渠道：X (Twitter)、小红书、Reddit**
>
> 更新时间：2026-04-02

---

## 一、"感知"是什么意思

### OpenClaw 为什么火

不是因为它更聪明。是因为：
- 它能操作你的电脑文件
- 它有自己的"记忆空间"（.openclaw/ 目录）
- 它能通过浏览器看到网页
- 它能发消息到微信

**用户感受：这个东西"活着"。不是问一句答一句的聊天框，是一个在真实世界里有存在感的 Agent。**

### CrabRes 需要的"感知"

```
层级 1：看得见（已实现）
  → Tavily 搜索真实网页
  → Scrape 抓取竞品页面
  → Social Search 搜索 Reddit/X 讨论

层级 2：记得住（已实现）
  → .crabres/memory/ 目录持久化
  → 产品信息 / 竞品数据 / 策略 / 实验结果

层级 3：感知效果（刚实现）
  → action→result 追踪
  → Daemon 每 30 分钟回查帖子数据

层级 4：感知平台生态（要做 ← 核心！）
  → 知道 X 的推荐算法偏好什么
  → 知道小红书的流量分发逻辑
  → 知道 Reddit 每个子版块的文化和规则
  → 能搜索实时的博主数据、话题热度、竞品动态

层级 5：操作真实世界（未来）
  → 通过浏览器自动化（用户授权后）实际执行
  → 在 Agent 沙箱中生成文件、管理素材
  → 通过 API 代发帖子
```

### Agent 沙箱设计

给 CrabRes 一个"自己的空间"，让用户感觉它是一个有实体的存在：

```
.crabres/
├── memory/           # 记忆（已有）
│   ├── product/
│   ├── research/
│   ├── strategy/
│   └── execution/
├── workspace/        # Agent 的工作区（新！）
│   ├── drafts/       # 待发布的帖子草稿
│   ├── assets/       # Agent 生成/收集的素材（图片方向、文案集）
│   ├── outreach/     # 博主外联管理（候选人表、邮件草稿、进度）
│   ├── reports/      # 自动生成的报告（周报、月报）
│   └── experiments/  # 实验记录和数据
├── playbooks/        # 活跃的增长剧本（已有）
└── config/           # 用户配置
    ├── brand.json    # 品牌信息
    ├── channels.json # 选择的渠道偏好
    └── rules.json    # 用户的规则（不做什么、预算限制等）
```

**用户能看到 Agent 在这个空间里"工作"**：
- "CrabRes 在 workspace/drafts/ 里准备了 3 篇 X 推文等你审核"
- "CrabRes 在 workspace/outreach/ 里整理了 15 个博主候选人"
- "CrabRes 在 workspace/reports/ 里生成了本周增长周报"

---

## 二、三个渠道为什么选这三个

| 渠道 | 覆盖用户 | 为什么深覆盖 |
|------|---------|------------|
| **X (Twitter)** | 海外独立开发者、Build in Public 社群 | #1 indie hacker 战场，算法可研究，API 相对开放 |
| **小红书** | 国内出海用户、消费品创业者 | 国内最有增长潜力的种草平台，CrabRes 的中文差异化 |
| **Reddit** | 所有有产品的人 | 转化率最高的免费渠道，Google SEO 加持，子版块生态丰富 |

这三个加起来覆盖了 CrabRes 的两个核心用户画像：
- **Global Vibe Voyager**（海外）→ X + Reddit
- **CN Money-Maker Coder**（国内出海）→ 小红书 + Reddit

---

## 三、每个渠道要做到多深

### 深度标准

不是"知道这个平台"的深度。
是**"一个在这个平台做了 3 年运营的人"的知识水平**。

具体来说：

### X (Twitter) 要懂的

**算法与推荐逻辑：**
- X 的 For You 算法怎么排序（互动权重 > 时间）
- 什么类型的内容被推荐（Thread > 单推，带图 > 纯文字，争议 > 中性）
- 黄金发帖时间（按时区分）
- 新号冷启动怎么做（前 14 天算法考察期）
- 什么行为会被降权（频繁发链接、短时间大量互动、被 mute/block）

**内容策划：**
- Thread 的最佳结构（Hook → 价值点 → CTA）
- 怎么写 Hook（第一句决定生死）
- 话题标签策略（#buildinpublic #indiehacker 的实际效果）
- Reply guy 策略（回复大号的帖子蹭流量，但怎么做不像 spam）
- Build in Public 的内容模板（数据分享、教训分享、里程碑庆祝）

**数据与追踪：**
- 什么指标真正重要（impressions 虚荣，profile visits + link clicks 才算数）
- 怎么从 X Analytics 读数据
- 什么样的增长曲线是健康的

**变现路径：**
- 从 follower 到 customer 的漏斗（bio link → landing page → 注册）
- 什么时候应该推产品 vs 什么时候应该纯分享

### 小红书要懂的

**算法与分发逻辑：**
- CES 评分系统（点赞 1 分 / 收藏 1 分 / 评论 4 分 / 转发 4 分）
- 流量池递进机制（200 曝光 → 1000 → 1 万 → 10 万）
- 发布后 2 小时是黄金期（决定是否进入下一级流量池）
- 什么时间发帖最好（工作日 12:00-13:00 / 18:00-20:00 / 21:00-23:00）
- 什么行为被限流（频繁编辑、硬广、导流微信、重复内容）

**内容策划：**
- 封面设计（决定点击率的 70%——大字报 vs 对比图 vs 真人出镜）
- 标题套路（数字 + 痛点 + 情绪词）
- 正文结构（痛点引入 → 解决方案 → 使用体验 → 总结推荐）
- 关键词布局（标题 + 正文 + 标签 三处都要有）
- 评论区运营（自己评论置顶 + 回复时间影响权重）

**种草 vs 广告：**
- 种草笔记怎么写不像广告
- 报备与非报备的区别和风险
- 蒲公英平台的规则
- 素人铺量 vs 达人精投的 ROI 对比

### Reddit 要懂的

**平台文化：**
- 反营销文化是 Reddit 的 DNA（违反会被 shadowban）
- 每个 subreddit 是独立的小社区，规则完全不同
- karma 系统决定你的可信度
- mod 的权力非常大（得罪 mod = 永久 ban）

**运营策略：**
- 先潜水 → 再评论 → 最后发帖（至少 7 天不提产品）
- 高价值内容格式：经验分享 > 教程 > AMA > 工具推荐
- 回复比发帖更有效（找高排名老帖回复，Google 会持续送流量）
- 自我推广规则（大多数 sub 要求 < 10% 的帖子是自推广）

**子版块研究：**
- 每个目标 sub 的规则、文化、发帖模板、最佳时间、mod 偏好
- 竞品在哪些 sub 活跃、效果如何
- 哪些 sub 对商业内容友好，哪些绝对不行

---

## 四、知识工程路线

### Phase 1: 三渠道知识注入（优先）

把上面的知识结构化，注入到对应专家的知识库中：

```python
# skills_registry.py 扩充

EXPERT_KNOWLEDGE["social_media"].extend([
    {
        "name": "x_twitter_deep_knowledge",
        "description": "X/Twitter 平台深度运营知识",
        "framework": "... 算法逻辑 + 内容策略 + 冷启动 + 追踪指标 ..."
    },
    {
        "name": "xiaohongshu_deep_knowledge", 
        "description": "小红书平台深度运营知识",
        "framework": "... CES 评分 + 流量池 + 封面设计 + 种草技巧 ..."
    },
    {
        "name": "reddit_deep_knowledge",
        "description": "Reddit 平台深度运营知识",
        "framework": "... 反营销文化 + karma 系统 + 子版块研究方法 ..."
    },
])
```

### Phase 2: 实时感知能力

- X: 通过 API/Scrape 获取话题热度、竞品帖子表现、博主数据
- 小红书: 通过 Scrape 获取笔记数据、达人信息（注意反爬）
- Reddit: 通过 API 获取子版块活跃度、帖子排名、用户 karma

### Phase 3: 浏览器操控（用户授权后）

- Agent 可以打开浏览器查看平台实时数据
- Agent 可以帮用户截图竞品帖子分析
- Agent 可以辅助发帖（半自动：准备好内容 → 用户确认 → Agent 操作发布）

---

## 五、Demo 阶段的体验目标

### 用户说 "我做了一个 AI 项链" 后看到的

```
CrabRes: 正在研究你的市场...

[研究阶段 — 30 秒]
  🔍 搜索竞品: ORRA Smart Ring, Oura Ring, RingConn...
  💬 扫描 Reddit r/wearables, r/smartjewelry (12 个相关讨论)
  📱 扫描小红书 "智能首饰" (月搜索 8.2 万次)

[圆桌讨论 — 专家分析]
  🔍 Market Researcher: "3 个直接竞品，ORRA 在小红书月销 2000+，
      主要通过 50 个中腰部达人种草。Reddit 上 r/wearables 有真实需求..."
  
  💰 Economist: "ORRA 定价 $199，你的 $299 需要差异化支撑。
      建议策略：小红书种草（预算 ¥3000/月可铺 30 篇素人笔记）+ 
      Reddit 社区运营（$0 但需要每天 30 分钟）+ 
      X 上 Build in Public（$0）。总预算 < ¥5000/月。"
  
  🧠 Psychologist: "智能首饰的购买决策是'身份认同'而非'功能需求'。
      不要卖'AI 功能'，卖'这是懂科技的人才戴的首饰'。
      ⚠️ 刺痛真话：你的产品图看起来像科技产品而非首饰，
      这会吓跑 70% 的女性用户。"

[输出：3 条增长路径]

📋 路径 A: 小红书达人种草 [18 步 Playbook]
   Phase 1: 账号搭建 + 封面设计标准 (Day 1-3)
   Phase 2: 素人铺量 30 篇 (Day 4-20)  
   Phase 3: 中腰部达人合作 5 人 (Day 21-40)
   Phase 4: 追踪 + 迭代 (Day 41-60)
   预算: ¥3000-5000/月 | 预期: 月曝光 50 万+

📋 路径 B: Reddit 社区深耕 [12 步 Playbook]
   Phase 1: 子版块研究 + 信用建设 (Day 1-7)
   Phase 2: 价值内容发布 (Day 8-28)
   Phase 3: 精准 DM (Day 29-42)
   预算: $0（纯时间） | 预期: 月 50-100 次网站点击

📋 路径 C: X Build in Public [10 步 Playbook]
   Phase 1: 账号设置 + 定位 (Day 1-2)
   Phase 2: 28 天内容日历 (Day 3-30)
   Phase 3: 博主互动 + 社群建设 (持续)
   预算: $0 | 预期: 1000 followers / 3 月

选择你要优先启动的路径 →
```

**这和 ChatGPT 给出的"建议你做社媒营销"是完全不同级别的体验。**

---

## 六、执行优先级

### 立刻做
1. **三渠道深度知识注入** — 扩充 skills_registry.py（X + 小红书 + Reddit）
2. **Coordinator prompt 引导输出 Playbook 结构**（而不是纯文本）

### 下一步做
3. **Agent workspace 沙箱**（.crabres/workspace/ 文件操作）
4. **三渠道 Playbook 模板细化**（18 步 / 12 步 / 10 步的完整 SOP）

### 后续做
5. **浏览器操控能力**（Playwright/Puppeteer 用户授权后）
6. **实时数据管道**（博主搜索、话题热度、竞品监控）
7. **搜广推算法**（向量检索匹配增长路径 + 主动推荐）

---

*这份文档定义了 CrabRes Demo 阶段的核心体验。
不是做 10 件事做得一般，是做 3 件事做到让人震惊。
X + 小红书 + Reddit，每个都要深到"这不是 AI 在猜，这是真懂行的人在教我"。*
