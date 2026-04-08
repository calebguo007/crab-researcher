# CrabRes UI/UX 完整设计方案

> 以一个用户的视角走完整个旅程
> 每一步都在想：他会产生兴趣吗？信任吗？付费吗？碰壁了怎么办？

---

## 设计哲学

**三个关键词：可爱、聪明、可信。**

- **可爱**：Duolingo 证明了——可爱不是幼稚，可爱是让人愿意每天打开。人们不会每天打开一个"专业工具"，但会每天打开一个有感情的伙伴。
- **聪明**：CrabRes 不是宠物游戏，是一个真的能帮你赚钱的 Agent。可爱是外壳，聪明是内核。
- **可信**：indie hacker 被太多"AI 营销工具"骗过了。CrabRes 必须在 30 秒内证明自己不是又一个垃圾。

**视觉风格：**
不是像素。不是 3D 写实。不是珊瑚水母。

**是——手绘感插画 + 苹果级排版 + 微妙动效。**

像 Notion 的空状态插画 + Linear 的排版克制 + Duolingo 的性格注入。

品牌的核心视觉元素是一只**小螃蟹**——但不是通用的卡通螃蟹，是一只有性格、有表情、有故事的螃蟹。它聪明、勤劳、偶尔俏皮，但永远靠谱。

---

## 视觉风格定义

```
风格：Refined Illustration（精致插画）

参考混合体：
  Notion 的插画气质（手绘感、留白、优雅）
  + Linear 的排版和间距（极致克制）
  + Stripe 的信任感（专业、数据清晰）
  + Duolingo 的性格和情感（表情丰富、互动有趣）

不是：
  ❌ 像素复古风（太同质化）
  ❌ 3D 渲染（太重、太慢）
  ❌ 纯几何扁平（太冷、没感情）
  ❌ 赛博朋克（太不亲切）

色板：
  主色: #1E293B (深蓝灰——沉稳但不压抑)
  次色: #F8FAFC (极浅——干净但不刺眼)
  品牌色: #0EA5E9 (天空蓝——活力、信任、科技感)
  强调色: #F97316 (暖橙——螃蟹色，用于 CTA 和生物体)
  成功: #10B981
  警告: #F59E0B
  错误: #EF4444

  支持暗色/亮色切换，亮色为默认（indie hacker 白天工作多）

字体：
  标题: Geist Sans (Vercel 开源字体，现代几何感)
  正文: Inter (最佳可读性)
  数字/代码: Geist Mono
  中文: 系统默认 (苹方/思源黑体)

圆角: 12px (卡片) / 8px (按钮/输入框) — 温和但不幼稚
阴影: 极浅的 spread shadow，不用 drop shadow
间距: 8px 基础网格，宽松排列

图标: 定制的线性图标（不用 emoji，不用 lucide），
      线条粗细 1.5px，圆角端点，风格和螃蟹插画一致
```

---

## 小螃蟹（生物体）设计

### 不叫 Buddy，不叫宠物。它就是 CrabRes 本身的化身。

```
核心形象：一只小螃蟹

风格：精致插画 + 微妙动效
  · 手绘质感但边缘干净（不是 rough sketch）
  · 大眼睛（可爱的源头——Duolingo 的大眼睛是关键）
  · 简洁的身体线条（不画每一条腿的细节）
  · 品牌橙色为主色 #F97316
  · 面部表情丰富（最重要的设计维度）

表情系统（每个状态一个表情）：
  😊 默认: 微笑，温和地呼吸
  🤔 研究中: 戴上小眼镜，认真的表情
  😄 增长好: 开心地挥舞钳子
  😰 发现问题: 皱眉，举起一个小警告牌
  😴 夜间整理: 闭眼，Z-z-z
  🎉 达成里程碑: 跳舞 + 撒花
  🥺 用户久没来: 可怜巴巴地看着你
  💪 策略执行中: 戴上小安全帽，工作中

为什么不做珊瑚/水母/有机体：
  · 珊瑚没有面部表情 → 无法建立情感连接
  · 水母太抽象 → 用户不会说"我的水母今天在研究竞品"
  · 螃蟹有面部 + 钳子 → 可以做丰富的表情和动作
  · 而且品牌名就是 CrabRes → 螃蟹是天然的

每个用户的螃蟹差异化：
  · 配饰不同（不是形态不同——形态不同太抽象，配饰直观）
  · SaaS 产品 → 戴小耳机
  · 电商 → 背小购物袋
  · 社区 → 举小旗子
  · 工具 → 戴小安全帽
  · 随着使用变化：
    新用户 → 小螃蟹只有基本配饰
    活跃用户 → 螃蟹有更多装饰（围巾、徽章、小翅膀）
    高级用户 → 金色配饰
  · 配饰可收集、可展示
  · 但核心螃蟹形象一致 → 品牌统一
```

---

## 用户旅程：从第一次看到 → 付费

### 第 0 步：Landing Page（第一印象，30 秒决定生死）

```
用户从 X/Reddit/Product Hunt 点进来。

┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌──────┐                          [Log in]  [Sign up]  │
│  │ 🦀   │ CrabRes                                       │
│  └──────┘                                               │
│                                                         │
│              You build it.                              │
│              We grow it.                                │
│                                                         │
│    The AI growth agent that does the work —             │
│    not just the advice.                                 │
│                                                         │
│         [Start free — no credit card →]                 │
│                                                         │
│  ─── 已帮助 ───                                         │
│                                                         │
│  [Logo] [Logo] [Logo] [Logo] [Logo]                     │
│  "312 products growing with CrabRes"                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────┐         │
│  │                                            │         │
│  │  (嵌入的 30 秒产品演示视频/动态截图)        │         │
│  │  展示：用户输入产品 → 螃蟹开始研究          │         │
│  │  → 专家圆桌讨论 → 输出完整增长计划          │         │
│  │                                            │         │
│  └────────────────────────────────────────────┘         │
│                                                         │
│                                                         │
│  ── Not another marketing tool. ──                      │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 🔍       │  │ 🧠       │  │ ✍️       │              │
│  │ Validates │  │ Thinks   │  │ Writes   │              │
│  │ your     │  │ like a   │  │ every    │              │
│  │ direction│  │ team of  │  │ post,    │              │
│  │ first    │  │ 13       │  │ email,   │              │
│  │          │  │ experts  │  │ plan     │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                         │
│  "Most tools write you a template.                      │
│   CrabRes researches your specific market,              │
│   analyzes your competitors by name,                    │
│   and tells you if your direction is wrong              │
│   — before you waste months."                           │
│                                                         │
│                                                         │
│  ── What users say ──                                   │
│                                                         │
│  ┌─────────────────────────────────────┐                │
│  │ "CrabRes told me my product idea    │                │
│  │  had no market. Saved me 6 months." │                │
│  │  — @indie_maker, 320 followers      │                │
│  └─────────────────────────────────────┘                │
│  ┌─────────────────────────────────────┐                │
│  │ "I literally copy-pasted the Reddit │                │
│  │  posts it wrote. Got 40 upvotes     │                │
│  │  and 12 signups from ONE post."     │                │
│  │  — @saas_builder, 1.2K followers    │                │
│  └─────────────────────────────────────┘                │
│                                                         │
│                                                         │
│  ── Pricing ──                                          │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐          │
│  │  Free    │  │  Pro ← best  │  │  Team    │          │
│  │  $0      │  │  $29/mo      │  │  $79/mo  │          │
│  │          │  │              │  │          │          │
│  │ 1 project│  │ 3 projects   │  │ unlimited│          │
│  │ Basic    │  │ 13 experts   │  │ + API    │          │
│  │ research │  │ Full plans   │  │ + collab │          │
│  │          │  │ Daily tasks  │  │ + custom │          │
│  │ [Start]  │  │ [Start free] │  │ [Contact]│          │
│  └──────────┘  └──────────────┘  └──────────┘          │
│                                                         │
│  "Pro is free for 14 days. No credit card."             │
│                                                         │
│                                                         │
│  ── FAQ ──                                              │
│  (折叠式，解决常见疑虑)                                  │
│  · "How is this different from ChatGPT?"                │
│  · "Will it work for my niche?"                         │
│  · "What if I have zero marketing experience?"          │
│  · "Can I cancel anytime?"                              │
│                                                         │
│  ─────────────────────────────────────                  │
│  🦀 CrabRes · © 2026 · Privacy · Terms                 │
│                                                         │
└─────────────────────────────────────────────────────────┘

信任构建策略：
  1. 用户 logo（即使最初只有 5 个 beta 用户，也要展示）
  2. 具体数字："312 products" 而非 "many users"
  3. 真实推荐（带 @ 和粉丝数，可验证）
  4. "No credit card" 反复出现（消除阻力）
  5. FAQ 直接回答"这和 ChatGPT 有什么区别"（最大的质疑）
```

### 第 1 步：注册（最大限度降低摩擦）

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  🦀 Welcome to CrabRes                          │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  [Continue with Google]                   │  │
│  │  [Continue with GitHub]                   │  │
│  │  ─── or ───                               │  │
│  │  Email: [                              ]  │  │
│  │  Password: [                           ]  │  │
│  │  [Create account]                         │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  By signing up you agree to Terms & Privacy     │
│                                                 │
│  ── 背书区 ──                                    │
│  "Backed by research from 18 open-source        │
│   marketing frameworks used by 100K+ teams"     │
│                                                 │
│  [Stripe logo] [Vercel logo] [Linear logo]      │
│  ↑ 使用相同技术栈的公司，建立技术信任           │
│                                                 │
└─────────────────────────────────────────────────┘

关键：
  · Google/GitHub 一键登录（开发者用 GitHub，普通人用 Google）
  · 不问任何多余信息（公司名/手机号统统不要）
  · 注册页也有背书信息
```

### 第 2 步：Onboarding（3 步，不超过 2 分钟）

```
注册后不是进 Dashboard，是进一个温暖的引导流：

Step 1/3:
┌─────────────────────────────────────────────────┐
│                                                 │
│  🦀 (螃蟹开心地挥手)                             │
│                                                 │
│  "Hi! I'm CrabRes.                              │
│   Tell me about your product                    │
│   and I'll start researching."                  │
│                                                 │
│  What's your product?                           │
│  [                                           ]  │
│  (example: "AI resume optimizer for job seekers")│
│                                                 │
│  Product URL (optional):                        │
│  [                                           ]  │
│                                                 │
│                              [Next →]           │
│                                                 │
└─────────────────────────────────────────────────┘

Step 2/3:
┌─────────────────────────────────────────────────┐
│                                                 │
│  🦀 (螃蟹戴上眼镜，认真听)                       │
│                                                 │
│  "What's your growth goal?"                     │
│                                                 │
│  Target users in 3 months:                      │
│  [ 100 ] [ 500 ] [ 1000 ] [ 5000 ] [ custom ]  │
│                                                 │
│  Monthly budget for marketing:                  │
│  [ $0 ] [ $100 ] [ $500 ] [ $1000+ ]            │
│                                                 │
│                              [Next →]           │
│                                                 │
└─────────────────────────────────────────────────┘

Step 3/3:
┌─────────────────────────────────────────────────┐
│                                                 │
│  🦀 (螃蟹系上围裙，准备工作)                     │
│                                                 │
│  "Got it! I'm assembling your growth team."     │
│                                                 │
│  (动画：13 个小图标依次亮起，代表 13 位专家)      │
│                                                 │
│  🔍 Market Research... ready                    │
│  💰 Economics... ready                          │
│  📝 Content... ready                            │
│  🎯 Social Media... ready                       │
│  ...                                            │
│  ✅ All 13 experts assembled!                   │
│                                                 │
│  "Starting research now. This takes 1-2 min."   │
│                                                 │
│                          [Let's go →]           │
│                                                 │
└─────────────────────────────────────────────────┘

碰壁防护：
  · 每步都可以跳过/稍后填写（但说明为什么这些信息重要）
  · 产品描述可以很简短（"AI tool for X"就够）
  · 预算选 $0 完全没问题（免费策略也很多）
  · 如果用户犹豫，螃蟹会说"You can always change this later"
```

### 第 3 步：主界面 — Surface（日常模式）

```
┌──────────────────────────────────────────────────────────┐
│  🦀 CrabRes          JobPilot ▾         [🔔] [⚙️] [👤] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│         ┌─────────────────────┐                          │
│         │     🦀               │                         │
│         │    (戴着眼镜,        │  ← 你的螃蟹             │
│         │     身旁有小徽章)    │     有自己的配饰和表情    │
│         │                     │     在轻轻地晃动         │
│         │  "Good morning!     │                          │
│         │   3 things today."  │  ← 每天一句话，有个性    │
│         └─────────────────────┘                          │
│                                                          │
│      ┌────────┐  ┌────────┐  ┌────────┐                 │
│      │  +23%  │  │   51   │  │  12d   │                 │
│      │ growth │  │ users  │  │ streak │                 │
│      └────────┘  └────────┘  └────────┘                 │
│                                                          │
│  ─── Today ───────────────────────────────────           │
│                                                          │
│  ┌───────────────────────────────────────────────┐       │
│  │  ✍  Publish Reddit post              [Do it →]│       │
│  │     r/cscareerquestions · draft ready          │       │
│  ├───────────────────────────────────────────────┤       │
│  │  💬  Reply to high-value comment      [View →]│       │
│  │     Someone asking about resume tools         │       │
│  └───────────────────────────────────────────────┘       │
│                                                          │
│  ─── Discoveries ─────────────────────────────           │
│                                                          │
│  ┌───────────────────────────────────────────────┐       │
│  │  ⚡ Competitor Jobscan dropped price 20%       │       │
│  │     [Let me analyze →]                        │       │
│  ├───────────────────────────────────────────────┤       │
│  │  🎯 @JeffSu posted "Best resume tools 2026"  │       │
│  │     You're not in it. [Want me to email him?] │       │
│  └───────────────────────────────────────────────┘       │
│                                                          │
│  ─── ─── ─── ─── ─── ─── ─── ─── ───                    │
│                                                          │
│  ┌────────────────────┐  ┌─────────────────────┐        │
│  │  💬 Talk to CrabRes│  │  📋 Growth Plan     │        │
│  └────────────────────┘  └─────────────────────┘        │
│                                                          │
└──────────────────────────────────────────────────────────┘

设计细节：
  · 螃蟹在最上方，不大（大约 80px），但是有灵魂
  · 螃蟹每天说一句不一样的话（不是模板，是基于当前状态）
  · 3 个数字用大字体，没有装饰框——信息密度极低
  · 任务卡片用柔和的玻璃卡片，左侧有颜色条标识类型
  · 所有按钮右对齐，操作明确
  · 自定义图标（不是 emoji），风格和螃蟹插画统一
```

### 第 4 步：对话页面 — Dialogue

```
点击"Talk to CrabRes"进入：

┌──────────────────────────────────────────────────────────┐
│  ← Back              CrabRes Chat            JobPilot ▾  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ 🦀 CrabRes ────────────────────────────────────── │ │
│  │                                                    │ │
│  │  Based on my research, here are 3 key findings:    │ │
│  │                                                    │ │
│  │  1. Jobscan's price drop is defensive — their      │ │
│  │     traffic didn't increase. Not a threat.         │ │
│  │                                                    │ │
│  │  2. Your "mock interview" feature is unique.       │ │
│  │     No direct competitor has it.                   │ │
│  │                                                    │ │
│  │  3. I suggest repositioning: lead with             │ │
│  │     "interview prep" not "resume builder".         │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────┐      │ │
│  │  │  ▶ See expert roundtable discussion      │      │ │
│  │  └──────────────────────────────────────────┘      │ │
│  │                                                    │ │
│  │  What do you think? Should I adjust the plan?      │ │
│  └────────────────────────────────────────────────── │ │
│                                                          │
│  ┌─ 展开: Expert Roundtable ──────────────────────── │ │
│  │                                                    │ │
│  │  🔍 Market Researcher                              │ │
│  │  "Jobscan's SimilarWeb data shows flat traffic     │ │
│  │   despite the price drop..."                       │ │
│  │                                                    │ │
│  │  💰 Economist                                      │ │
│  │  "At $200/mo budget, don't price-match. Your       │ │
│  │   CAC via Reddit is $0.8 vs their $12 via ads..."  │ │
│  │                                                    │ │
│  │  🧠 Psychologist                                   │ │
│  │  "Interview anxiety > resume anxiety. Repositioning│ │
│  │   to 'interview prep' triggers loss aversion..."   │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────── │ │
│                                                          │
│  ┌─ You ────────────────────────────────────────── │   │
│  │  Yes, let's adjust. Can you rewrite the           │   │
│  │  landing page copy?                               │   │
│  └─────────────────────────────────────────────── │   │
│                                                          │
│  ┌─ 🦀 ──── working... ──────────────────────────── │ │
│  │  ✍ Copywriter is drafting new landing page...     │ │
│  │  🎨 Designer is preparing visual guidelines...     │ │
│  └────────────────────────────────────────────────── │ │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Type your message...                   [Send →] │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘

设计细节：
  · CrabRes 消息带螃蟹小头像（同一只螃蟹）
  · 用户消息右对齐，简洁
  · "Expert Roundtable"默认折叠，点击展开
  · 专家图标用统一风格的小图标（不是 emoji）
  · 工作状态实时展示，让用户知道在等什么
```

### 第 5 步：增长计划页面 — Strategy

```
┌──────────────────────────────────────────────────────────┐
│  ← Back          Growth Plan v3        [Export] [Share]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ═══●════════════●═══════════○═══════════○═════          │
│    Research     Strategy     Execute     Review          │
│    ✓ done      ✓ done      in progress                  │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │  Goal: 1,000 users in 90 days                │        │
│  │  Budget: $200/mo · Week 3 of 12              │        │
│  │  Progress: 51/1000 (5.1%)                    │        │
│  │  ████░░░░░░░░░░░░░░░░                        │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌── Strategy A ──── Active ──── +34 users ──────┐      │
│  │  Reddit Community Engagement                   │      │
│  │  r/cscareerquestions · r/resumes               │      │
│  │  3 posts/week + 15min/day replies              │      │
│  │                                                │      │
│  │  This week: 67 upvotes · 34 visits · 2 signups│      │
│  │  [See this week's posts] [View analytics]      │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ┌── Strategy B ──── In progress ────────────────┐      │
│  │  Career Coach Partnerships                     │      │
│  │  Contacted 3 · 1 replied · 0 confirmed         │      │
│  │  [See email status] [Try more coaches]         │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ┌── Strategy C ──── Early stage ────────────────┐      │
│  │  SEO Long-term Play                            │      │
│  │  3 articles published · 0 keywords in top 50   │      │
│  │  [See articles] [See keyword rankings]         │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ── This week's content ──                               │
│  Mon ✅ Reddit post (published)                          │
│  Wed 📝 LinkedIn article (draft ready)                   │
│  Fri 📝 Reddit post (draft ready)                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 第 6 步：个人管理页面

```
┌──────────────────────────────────────────────────────────┐
│  ← Back              Settings                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ Profile ─────────────────────────────────────────┐  │
│  │  🦀 (你的螃蟹，带着所有配饰)                       │  │
│  │  Name: Caleb                                      │  │
│  │  Email: caleb@example.com                         │  │
│  │  Plan: Pro · $29/mo · since Mar 2026              │  │
│  │  [Edit profile] [Manage subscription]             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ Your Crab ───────────────────────────────────────┐  │
│  │  Species: Tech Crab (SaaS)                        │  │
│  │  Accessories: 🎧 Headphones · 🏅 First-100 badge  │  │
│  │  Streak: 12 days 🔥                               │  │
│  │  [View all accessories] [Share your crab]         │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ Projects ────────────────────────────────────────┐  │
│  │  JobPilot (active) · 51 users · Plan v3           │  │
│  │  [Switch to] [Settings]                           │  │
│  │                                                   │  │
│  │  [+ Add new project]                              │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ Notifications ───────────────────────────────────┐  │
│  │  Email daily digest: [On]                         │  │
│  │  Push notifications: [Off]                        │  │
│  │  Slack/Discord: [Connect →]                       │  │
│  │  Telegram: [Connect →]                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ API & Integrations ──────────────────────────────┐  │
│  │  Google Analytics: [Connect →]                    │  │
│  │  API key: [Generate →]                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  [Log out]                    [Delete account]           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 第 7 步：螃蟹说明/产品介绍页

```
在 Landing Page 或设置里点击"About your Crab"：

┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Meet your CrabRes 🦀                                    │
│                                                          │
│  Your crab is the living reflection of your              │
│  product's growth journey.                               │
│                                                          │
│  (插画：不同阶段的螃蟹，从小到大)                         │
│                                                          │
│  ── How it works ──                                      │
│                                                          │
│  Your crab grows as your product grows.                  │
│  It earns accessories from your achievements.            │
│  It shows emotions based on your growth status.          │
│  No two crabs are alike — because no two                 │
│  products grow the same way.                             │
│                                                          │
│  ── Accessories ──                                       │
│                                                          │
│  🎧 Headphones — SaaS products                          │
│  🛒 Shopping bag — E-commerce                            │
│  📢 Megaphone — Community products                       │
│  🏅 First-100 badge — Reach 100 users                    │
│  ⭐ Gold star — Reach 1,000 users                        │
│  👑 Crown — Reach 10,000 users                           │
│  🔥 Flame scarf — 30-day streak                          │
│  ...and more to discover                                 │
│                                                          │
│  ── Share your crab ──                                   │
│                                                          │
│  (生成分享卡片的预览)                                     │
│  [Share to X] [Share to LinkedIn] [Download image]       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 关于圆桌的介绍

```
在 Landing Page 或首次使用时展示：

── Your AI growth team ──

CrabRes isn't one AI. It's a team of 13
specialized experts working together.

(插画：13 个小图标围成圆桌)

They research, debate, and challenge each other
to find the best strategy for YOUR product.
Not templates. Not generic advice.

🔍 Market Researcher — finds your competitors and users
💰 Economist — makes sure every dollar counts
📝 Content Strategist — builds your content engine
🎯 Social Media — knows every platform's culture
📢 Partnerships — connects you with the right people
🧠 Psychologist — understands why people buy
...and 7 more specialists

You hear one voice. Behind it, 13 minds are working.
```

---

## 碰壁点预判和解决

| 用户可能碰壁的地方 | 怎么解决 |
|--|--|
| "这和 ChatGPT 有什么区别？" | Landing page FAQ 第一条。核心答案：ChatGPT 不会研究你的竞品、不会追踪你的进展、不会主动通知你机会 |
| "我不会营销，这东西我能用吗？" | Onboarding 只需 3 步，只问产品是什么和目标，不问任何营销术语 |
| "生成的策略靠谱吗？" | 可展开专家圆桌看到推理过程；引用具体数据（竞品名、流量数字）而非泛泛建议 |
| "我没有预算" | $0 预算完全可用，Free 版提供基础研究和 1 个项目 |
| "太多信息了" | Surface 层只有螃蟹 + 3 个数字 + 今天的 2 个任务。复杂性全在深层 |
| "我开始执行了但不知道效果好不好" | Growth Plan 页面追踪每个策略的具体效果数据 |
| "用了几天就忘了打开" | 螃蟹的连胜机制 + 邮件/推送提醒 + 发现新机会时主动通知 |
| "想付费但不确定值不值" | 14 天免费 Pro 试用，试用期间看到真实研究结果后自然转化 |
| "试用结束了还没决定" | 降为 Free 但保留数据，螃蟹说"I'll still be here when you're ready" |

---

*这份文档覆盖了从第一眼到付费的完整用户旅程。
每一个像素都有目的：产生兴趣、建立信任、降低摩擦、推动行动。*
