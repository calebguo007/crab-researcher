"""
CrabRes Skills 知识注册表

这不是安装 Skills 到 .claude/ 目录，而是将高质量开源 Skills 的核心知识
整合为我们专家的参考知识库。

来源（经审核的高质量 Skills）：
- superamped/ai-marketing-skills (18 Skills, MIT)
- coreyhaines31/marketingskills (52.4K installs, MIT)
- inferen-sh/skills (product-hunt-launch 8.1K installs)
- openclaudia/openclaudia-skills (60+ Skills)

每个专家在被调度时，会根据任务类型从这里获取相关的框架和模板。
"""

# 每个专家可引用的知识模块
# key = expert_id, value = 该专家可调用的知识片段

EXPERT_KNOWLEDGE: dict[str, list[dict[str, str]]] = {

    "market_researcher": [
        {
            "name": "competitor_landscape",
            "source": "superamped/ai-marketing-skills",
            "description": "跨竞品对比分析框架",
            "framework": """分析步骤:
1. Feature Matrix: 按战略重要性排序，标注 ✅❌🔶
2. Pricing Comparison: 不仅对比价格，还对比模式和价值指标，识别定价信号
3. Positioning Map: 2x2 定位图（默认: 市场presence vs 产品广度），标注空白区域
4. Aggregate SWOT: 基于整个市场格局的宏观 SWOT，不是单一公司
5. Moat Landscape: 对比网络效应、转换成本、规模经济
6. Strategic Recommendations: 赢面、弱点、市场空缺、定位建议、雷区

规则:
- 绝不编造数据，缺失标注 "data not available"
- 至少需要 2 个竞品
- 推荐必须有数据支持
- 如果用户产品处于弱势必须诚实指出""",
        },
        {
            "name": "community_discovery",
            "source": "superamped/ai-marketing-skills",
            "description": "发现目标用户活跃的在线社区",
            "framework": """搜索维度:
- Reddit: 相关子版块，按活跃度和相关度排序
- Discord/Slack: 相关服务器/频道
- Facebook Groups: 相关群组
- LinkedIn Groups: 行业群组
- 论坛/垂直社区: 行业专属论坛
评估标准: 信噪比、活跃度、商业友好度、准入门槛""",
        },
        {
            "name": "channel_discovery",
            "source": "superamped/ai-marketing-skills",
            "description": "评估最佳获客渠道",
            "framework": """按 5 个标准评分:
1. Audience fit (目标用户是否在这个渠道)
2. Competition level (竞品密度)
3. Cost efficiency (CAC 预估)
4. Scalability (能否规模化)
5. Time to results (多快见效)
输出前 3 个优先渠道，附理由""",
        },
    ],

    "economist": [
        {
            "name": "pricing_strategy",
            "source": "coreyhaines31/marketingskills + psychology",
            "description": "定价策略和心理学框架",
            "framework": """定价心理:
- 魅力定价: $99 < $100（左位效应）
- 100法则: <$100 用百分比折扣, >$100 用绝对折扣
- 好-更好-最好: 三层定价，中间层是目标
- 诱饵效应: 添加较差的第三选项使首选更吸引
- 心理账户: "$3/天" < "$90/月"（感知不同）
- 免费的力量: $0→$1 的跳跃远大于 $1→$2

单位经济分析:
- CAC = 总获客成本 / 新客户数
- LTV = ARPU × 平均生命周期
- LTV/CAC > 3 = 健康
- 回收期 = CAC / 月收入/用户""",
        },
    ],

    "content_strategist": [
        {
            "name": "keyword_research",
            "source": "aaron-he-zhu/seo-geo-claude-skills (2.3K installs)",
            "description": "关键词研究和主题集群",
            "framework": """步骤:
1. 种子关键词 → 扩展为关键词宇宙
2. 按搜索意图分组: informational / navigational / commercial / transactional
3. 评估: 搜索量 × 竞争度 × 和产品的相关度
4. 建立主题集群: 1个支柱页面 + N个集群页面
5. 内容优先级: 高相关+低竞争优先""",
        },
        {
            "name": "seo_audit",
            "source": "addyosmani/web-quality-skills (4.8K installs)",
            "description": "SEO + AI 搜索优化审计",
            "framework": """38 点审计:
- 技术 SEO: 页面速度、移动适配、Schema 标记
- 内容结构: H1/H2 层级、FAQ 区块、对比表
- AI/GEO 准备度: 结构化数据、可引用答案、FAQ Schema
- E-E-A-T: 经验、专业性、权威性、可信度""",
        },
        {
            "name": "geo_optimization",
            "source": "CrabRes 2026 + Averi.ai research",
            "description": "GEO - 生成引擎优化（让 AI 搜索引擎引用你）",
            "framework": """GEO (Generative Engine Optimization) — 2026 年最重要的新渠道

什么是 GEO:
让 ChatGPT、Perplexity、Google AI Overviews 在回答用户问题时引用你的内容。
Peter Levels 发现 AI 推荐流量一个月内从 4% 跃升到 20%。

优化方法:
1. 结构化答案格式:
   - 每篇文章开头直接给出结论（不要废话导入）
   - 使用 FAQ 格式（Question → Direct Answer）
   - 包含对比表（AI 特别喜欢引用表格数据）
   - 使用确切数字和数据（"228.8亿元" > "数百亿"）

2. Schema 标记:
   - FAQPage schema 让 AI 能解析你的问答
   - Product schema 让 AI 知道你的定价和功能
   - HowTo schema 让 AI 引用你的步骤指南
   - Comparison schema 让 AI 引用你的对比数据

3. 内容结构:
   - H2 用问题形式（"What is the best X for Y?"）
   - 每个 H2 下面第一句话直接回答（无需铺垫）
   - 列举式内容（numbered lists）比段落更容易被引用
   - 包含 "as of 2026" 时间标记（AI 偏爱新鲜内容）

4. 引用建设:
   - 被高权威网站引用的内容更容易被 AI 推荐
   - 在 Reddit/HN/StackOverflow 上回答问题并链接回你的文章
   - 创建"唯一来源"数据（原创研究/调查/基准测试）

5. 对比页面（GEO 金矿）:
   - "X vs Y" 页面是 AI 最常引用的页面类型
   - 包含功能对比表 + 定价对比 + 适用场景
   - 诚实评价（不贬低竞品，AI 会检测偏见）

衡量:
- 在 ChatGPT/Perplexity 中搜索你的关键词，看是否引用你
- 追踪来自 AI 搜索引擎的流量（GA4 的 referral 中看 chat.openai.com 等）""",
        },
    ],

    "psychologist": [
        {
            "name": "marketing_psychology",
            "source": "coreyhaines31/marketingskills (38.3K installs)",
            "description": "70+ 营销心理学原则",
            "framework": """快速参考:
| 挑战 | 模型 |
|------|------|
| 低转化 | 希克定律、活化能、BJ Fogg行为模型 |
| 价格异议 | 锚定、框架、心理账户、损失厌恶 |
| 建立信任 | 权威、社会认同、互惠、出丑效应 |
| 增加紧迫感 | 稀缺性、损失厌恶、蔡格尼克效应 |
| 留存/流失 | 禀赋效应、转换成本、现状偏见 |
| 增长停滞 | 约束理论、复利、飞轮效应 |
| 决策瘫痪 | 选择悖论、默认效应、助推理论 |
| 入职 | 目标梯度、宜家效应、承诺一致性 |

核心说服框架:
- 互惠: 先给予再要求
- 承诺一致性: 小承诺→大承诺
- 社会认同: 展示他人在做
- 权威: 专家/认证背书
- 喜好: 相似性和故事
- 稀缺性: 限时/限量（仅在真实时使用）""",
        },
        {
            "name": "conversion_audit",
            "source": "superamped/ai-marketing-skills",
            "description": "53 点转化审计",
            "framework": """审计维度:
1. 客户关注点: 是否解决了核心痛点
2. 叙事弧线: 痛点→梦想→解决方案
3. 文案质量: 清晰度、说服力、具体性
4. 设计: 视觉层级、CTA 可见度、移动适配
5. CTA: 文案、位置、紧迫感
6. 社会证明: 类型、位置、可信度""",
        },
    ],

    "copywriter": [
        {
            "name": "copywriting_framework",
            "source": "coreyhaines31/marketingskills (52.4K installs)",
            "description": "完整文案写作框架",
            "framework": """写作原则:
- 清晰 > 机智
- 利益 > 功能
- 具体 > 模糊（"4小时→15分钟" > "节省时间"）
- 客户语言 > 公司语言
- 每部分一个想法

标题公式:
- "{达到结果} without {痛点}"
- "The {类别} for {受众}"
- "Stop {痛点}. Start {结果}."
- "{数字} ways to {结果} in {时间}"

CTA 公式: [动词] + [得到什么] + [限定词]
- 弱: 提交/注册/了解更多
- 强: 开始免费试用/获取你的[东西]/创建你的第一个[东西]

页面结构:
1. 首屏: 标题+副标题+CTA
2. 社会证明: Logo/数字/推荐
3. 问题/痛点
4. 解决方案/利益(3-5个)
5. 工作原理(3-4步)
6. 异议处理/FAQ
7. 最终CTA+风险逆转""",
        },
    ],

    "social_media": [
        {
            "name": "x_twitter_deep_knowledge",
            "source": "X open-source algorithm reverse-engineering (tang-vu/x-algorithm-playbook) + Calmops 2026 indie hacker guide + 掘金实战心得",
            "description": "X/Twitter 实战运营知识（算法公式+冷启动+内容+互动+转化）",
            "framework": """=== X (TWITTER) PLATFORM PRACTITIONER-LEVEL KNOWLEDGE ===

## Algorithm Scoring Formula (from open-source reverse engineering, 2026 update)
Post Score = Σ (weight × P(action))
Algorithm predicts 19 user behaviors with these weights:
  POSITIVE: Reply (+2×), Quote (+1.5×), Retweet (+1×), Like (+1×), Follow author (+1×)
  NEGATIVE: Block (-10×), Report (-20×, devastating), Mute (-1×), "Not interested" (-1×)
  NEUTRAL (but tracked): Click, Dwell time, Profile visit

Key insight: 1 reply = 2 likes in algorithm value. 1 block = -10 likes. AVOID BLOCKS AT ALL COSTS.

## Recommendation Pipeline (4 steps)
1. Candidate Sources:
   - Thunder: tweets from people you follow (in-network, shown first)
   - Phoenix: ML-discovered tweets from strangers (out-of-network, harder to get into)
2. Filtering: 12 filters (too old, blocked author, spam, etc.) — content removed entirely
3. Scoring: Grok Transformer model predicts engagement probability → weighted score
4. Ranking: highest scores shown first. Author diversity penalty applied (don't post too frequently)

## 10 Golden Rules (from algorithm reverse-engineering)
1. REPLIES ARE KING — posts generating replies score ~2x higher
2. AVOID NEGATIVE SIGNALS — 1 block (-10×) wipes out 10 likes
3. SPACE YOUR POSTS — author diversity penalty kicks in after first post. Wait 2-4 hours between posts
4. IN-NETWORK FIRST — your followers see you before strangers do. Build follower base first
5. MEDIA MATTERS — Video > Image > Text (if video exceeds minimum length threshold)
6. DWELL TIME COUNTS — longer content = higher engagement signal (threads >> single tweets)
7. DON'T TRIGGER FILTERS — 12 filters can completely hide your content
8. AUTHENTIC ENGAGEMENT — algorithm tracks your interaction patterns. No engagement pods
9. STAY VERTICAL — consistent topic helps retrieval matching
10. QUALITY > QUANTITY — one great post beats five mediocre ones

## Cold Start Playbook (0 → 1000 followers)

### Account Setup
- Username: simple, memorable, no underscores/numbers if possible
- Bio formula: [Who you are] + [What you do] + [Value prop] + [CTA link]
- Profile photo: clear face, looking at camera, professional
- Pinned tweet: your best thread or product announcement

### Phase 1: 前两周 Reply Guy Strategy
- Find 10-20 large accounts in your niche (10K-100K followers)
- Reply to their tweets within 30 min of posting (early replies get top position)
- Reply MUST add value: data, personal experience, contrarian take (not "great point!")
- Goal: 20-30 quality replies/day → their followers notice you → follow you
- This alone can get 200-500 followers in 2 weeks

### Phase 2: 第三四周 Original Content
- Content ratio: 40% value/教学 + 25% personal/幕后 + 20% engagement + 15% promo
- 1 Thread per week (5-12 tweets): Hook → Value points → CTA
- 2-3 single tweets per day
- Post 3-5 tweets/day when <500 followers (building presence)
- Reduce to 1-2/day after 1000 followers (quality over quantity)

### Phase 3: Month 2+ Build in Public
- Share real numbers (MRR, users, failures)
- Vulnerability > perfection ("I launched and got 0 users" > fake success)
- Weekly milestones, monthly retrospectives

## Daily Engagement Routine (30-60 min, NON-NEGOTIABLE)
- Reply to 5-10 tweets from peers/targets (quality replies with data/opinions)
- Like 20-30 relevant tweets (maintain visibility)
- Quote retweet 3-5 tweets adding your perspective
- Check notifications and reply to ALL mentions
- Best times: 7-9 AM, 12-1 PM, 5-7 PM (user's target timezone). Post 30 min before peak.

## Thread Structure (the #1 growth format)
Tweet 1 (HOOK — decides everything):
  Formula: "I [did X / studied X / spent $X]. Here's what [I learned / nobody tells you / actually works]:"
  Must create curiosity gap. If hook fails, thread dies.
Tweet 2-N (VALUE):
  One idea per tweet. Short sentences. Line breaks for readability.
  Use images/screenshots to break up text.
  Each tweet should be standalone-readable (people enter mid-thread).
Last tweet (CTA):
  "Follow me for more [topic]" or "I'm building [product] — try it free: [link in reply]"
  NEVER put links in main tweet — put in reply (algorithm penalizes external links)

## Single Tweet Formulas That Work
- "I [achievement with number]. Here are the [N] things that actually worked:"
- "Most people think [common belief]. They're wrong. Here's why:"
- Before/After with specific numbers
- Screenshot of real data + 1-sentence hot take
- Contrarian opinion (drives replies which = 2× algorithm boost)

## What Kills Your Reach
- External links in main tweet (put in reply instead)
- More than 2 hashtags (looks spammy, this isn't Instagram)
- Engagement pods (algorithm detects coordinated behavior)
- Posting >5 times without spacing (author diversity penalty)
- Getting blocked by multiple users (devastating: -10× each)
- Deleting tweets (signals low quality to algorithm)

## Conversion: Followers → Customers
- Bio link → specific landing page with UTM (not homepage)
- Pinned tweet = social proof (best thread, or launch announcement)
- DM strategy: only after genuine interaction. Never cold pitch.
- Monitor keywords related to your product → jump into conversations organically
- Build relationship before selling (80/20: value/promo)""",
        },
        {
            "name": "xiaohongshu_deep_knowledge",
            "source": "千万级变现实操经验 + 蝉妈妈/飞瓜数据 + CrabRes 2026 平台研究",
            "description": "小红书实战运营知识（养号+算法+内容+人设+变现，基于千万级变现实操）",
            "framework": """=== 小红书 (XIAOHONGSHU/RED NOTE) PRACTITIONER-LEVEL KNOWLEDGE ===
(来源：已变现千万级的实操总结，不讲概念，一切基于实操)

## 底层逻辑（必须理解）
- 小红书是女性友好平台
- 小红书是种草平台（分享好物，不是卖东西）
- 小红书是"美好XX分享"平台（正面、积极、生活化）

## 四个流量口
关注 / 发现 / 本地 / 搜索
实际上只有两个重要：**发现页** + **搜索页**

### 发现页算法逻辑
笔记发布后两条路：A违规 B收录（被搜索到）
收录后的互动权重排名（口诀：**一关二评三点赞**）：
  关注 > 评论=转发 > 点赞=收藏
  1个关注 = 1个评论+1个转发
  1个评论 = 1个点赞+1个收藏

只要有人持续互动，平台持续推流，可以几个月甚至一年以上还有推荐。
口号：**做爆一篇，吃上一年**

### 搜索页算法逻辑
搜索排序决定流量，位置不固定，实时变动。
**关键词是核心中的核心！**
官方说法：好标题更多赞。标题非常重要×3。

关键词来源：
1. 系统默认推荐（基于用户标签）
2. 搜索热门（短期热搜词条）
3. 联想关键词（用户输入自动补齐）

关键词选择原则：
- 热搜是短期流量，关键词是长期流量
- 选竞争小+流量大+匹配度高的词，不要泛词
- 反推：如果你是用户，会搜什么词能找到你？
- 合理布局，别硬堆（硬堆=广告=降权废号）

## 八级流量池（真实数据）
一级 0-200：没违规就有，多篇看站内信
二级 200-500：大部分账号的常态，如果长期→检查活跃度/垂直/原创/质量
三级 500-2000：内容还行但互动率低，提高内容和互动
**注：2000以下基本是AI机器人内容水平**
四级 2000-2万：正常，新手容易达到的标准
五级 2万-10万：自然流最后一关，过了就人工审核。要找到这个节奏感
六级 10万-100万：门槛！系统判定营销号/标题党就不推了。做到10万=成功一半
七级 100万-500万：人工干预，看内容+核心价值观+舆论风险
八级 500万+：新手不用考虑

**我们的目标：常态五级（2万+），够得着六级（10万+）**

## 养号七天法（一机一卡一号，禁频繁切换）
Day 1：不改任何资料，不发内容，搜索行业关键词，认真刷30分钟×3次，真人活跃（关注点赞评论）
Day 2：同Day 1，搜索行业关键词刷，不发内容
Day 3：不用搜索，看发现页。一屏4-5篇中有3篇以上是行业内容=养号成功→修改资料→发第一篇干货
Day 4-7：每天3篇左右干货分享，7天保证10篇干货

判定成功：
- 发布第一篇就出"恭喜你XXX"提示
- 发布后10分钟点薯条推广，能加热=账号正常
- 能出恭喜=权重有保证，后续正常更新，推流越来越高

**前七天千万不能发营销内容！第一篇绝不能违规！**

## 内容创作实战

### 封面（决定点击率70%）
- 统一3:4竖屏
- 封面要跟标题对得上
- 封面加文字：把笔记内核放封面
- 单篇至少三图以上
- 要好看、简洁、有高级感
- **没思路直接抄同行**

### 标题（=武器，决定生死）
标题逻辑：**话题+情绪**，20字左右，包含主题关键词
标题跟封面、内容、选题四项要有关联

标题套路：
数字类："百分之九十的人都不知道XX这么简单" / "三招教你XX" / "十个做XX的网站"
话题+提问："XX如何赚到一百万？" / "新手如何做XX？" / "一部手机能做XX吗？"
矛盾反差："XX月入十万，但我辞职了" / "中专毕业凭什么能月入十万"
反向法："天天吃肉也能减肥" / "不运动也能减肥"
提问+方案："XX如何上手，一部手机就够了"
猎奇心理："从年入百万到外卖骑手" / "一支可以当传家宝的手表"

标题怎么找：**搜、蹭、学、抄**
搜：全网搜索平台搜你的行业词，看自动弹出的后缀=用户关心的问题
蹭：蹭热点，热点+自己的行业=爆（当天发，最迟半天内）
学：用工具拉同行爆文，提关键字+同类词，直接照抄
抄：同行写什么你就写什么，图片标题内容按自己习惯一比一复制

### 内容
- 前10篇必须优质，垃圾内容没用
- 前7天不考虑引流、转化、营销
- 不要原封不动偷图（100%识别），改图5分钟
- 文案不要照抄（照抄是傻逼），专业内容可用AI转化，首尾按个人习惯口语化改写
- 600字以上加分，800字最合适
- **不要自己思考内容×3！同行已经给了验证过的答案，先抄再优化**

## 人设模板（转化率核心）

用户已经见号色变，专家号基本没转化率了。最高转化的两类：
1. **同类人**：跟用户有一样困扰的人（"我也在减肥的姐妹"）
2. **先行者**：已经做过这件事的人（"减肥成功的普通人"）

ABC矩阵打法：
A素人展示生活 + B提问 + C回答，但ABC都是你的号
基于真实分享=信任度大大提升

具体人设选择：
- 意见领袖型：有专业性又有普适性（最佳，需技术积累）
- 普通人记录生活：最容易拉近用户，信任度高，适合多账号
- 品牌创始人：配合A种B收，专业背书增强信任

## 发布节奏
前三天一篇/天 → 七天内补到10篇 → 正式营销时15-21篇
养号后一天一更即可，每篇间隔4小时以上
发布后看是否能投流，前期不要关注浏览量×3

## 权重算法
账号权重：原创 + 垂直 + 内容质量 + 活跃度 + 等级
笔记权重 > 账号权重（好内容普通号也能爆）
关键词要有关联，宁少勿多勿乱

## 违规红线
- 一手机多账号频繁切换
- 昵称/头像/个签出现联系方式
- 搬运/非原创/刷数据/钓鱼分享
- 不友善行为/敏感内容
- 评论区留联系方式（包括暗示）
- 一上来就发营销笔记

## 变现路径
笔记 → 评论区/主页引导 → 私域（微信）→ 成交
笔记 → 小红书店铺 → 直接成交
笔记 → 品牌搜索 → 淘宝/京东成交（种草→搜索经典路径）
导流方式很多，绝不能在公开区域留联系方式""",
        },
        {
            "name": "reddit_deep_knowledge",
            "source": "Karmic Reddit Organic Playbook 2025 + ReplyAgent/OptaReach research + Reddit Pro official guide",
            "description": "Reddit 实战运营知识（Karma Ladder 四阶段 + CQS + 反封号 + 归因）",
            "framework": """=== REDDIT PRACTITIONER-LEVEL KNOWLEDGE ===
(Source: Karmic Reddit Organic Playbook + ReplyAgent + Reddit Pro official guide)

## Platform Culture (CRITICAL — violate this and you're dead)
- Reddit is ANTI-MARKETING. Users actively hunt and downvote promotional content.
- Each subreddit is its own country with its own laws (rules, mods, culture).
- Karma = credibility. Low karma account posting about a product = instant suspicion.
- Mods have absolute power. If a mod doesn't like your post, you're banned. No appeal.
- "10% rule": most subreddits expect <10% of your posts/comments to be self-promotional.
- Authenticity is currency. "I built this" posts work. "Check out this amazing tool" posts die.

## CQS: Contributor Quality Score (HIDDEN — critical to understand)
Reddit has a HIDDEN account quality score that determines if your content gets shown:
- Factors: email verified, 2FA enabled, interaction quality (comments > posts), 
  content performance relative to community, behavior patterns (bot-like = penalized),
  mod actions (posts deleted = severe CQS damage)
- LOW CQS = posts auto-hidden or removed silently (you won't even know)
- HIGH CQS = priority display, content shown more broadly
- Building CQS takes weeks of genuine participation. Destroying it takes one spam post.

## Product-Reddit-Fit Assessment (before investing time)
Not every product belongs on Reddit. Score 0-10 on:
1. Pre-purchase consideration: Do customers research heavily before buying? (SaaS=yes, impulse buy=no)
2. Total addressable audience: Are there enough potential users? (mass market=yes, ultra-niche enterprise=no)
3. Show vs Tell: Does your product need text explanation? (B2B software=tell=good fit, fashion=show=harder)

Scoring: 8-10 = go all in. 5-7 = test in 2-3 subreddits. 0-4 = skip Reddit, just monitor.

## Karma Ladder: 120-Day Four-Phase Strategy (from Karmic)

### Phase 1: Foundation (Day 1-30) — BUILD LEGITIMACY
Goal: pass Reddit's spam filters, build real karma
- Account: use "brandname_yourname" format, verify email, enable 2FA
- Day 1-2: ONLY browse. No likes, no comments. Let algorithm observe you.
- Day 3-14: Join LOW-STAKES subreddits (r/AskReddit, r/CasualConversation)
  Post 1-3 helpful comments/day. ZERO brand mentions.
- Day 15-30: Gradually join TARGET subreddits (where your users hang out)
  Continue commenting helpfully. Still NO brand mentions.
- Target: 100+ karma, 30-day account age, zero violations

### Phase 2: Authority (Day 31-90) — BECOME TRUSTED VOICE
Goal: gain recognition in target communities
- Post 1-3 comments/day in target subreddits
- Directly answer questions, provide context, share experiences
- GOLDEN RULE: never mention your brand/product/website
- If someone asks for recommendations, reply "happy to share via DM"
- Target: 250+ karma, 25+ karma in each of 1-3 target subreddits

### Phase 3: Engagement (Day 91-120) — CREATE DISCUSSION
Goal: post high-engagement topics that boost authority
- Post "engagement topics": emotional triggers, hot takes, industry debates
- Title must be compelling, body must invite discussion
- Reply to every comment on your posts (boosts engagement metrics)
- ABSOLUTELY NO self-promotion or sneaky link insertion
- Target: at least 1 post per target subreddit with 25K+ views

### Phase 4: Intent (Day 120+) — GENTLE PROMOTION
Three types of promotional content (ONLY after phases 1-3):
1. Adapted content: repurpose blog/LinkedIn posts into Reddit-native format. Remove brand jargon.
2. Brand announcements: new features, funding, partnerships. GET MOD PERMISSION FIRST.
3. AMA (Ask Me Anything): founder answers community questions. Best trust-builder. Often cited by AI engines.

## Algorithm & Ranking
- Hot algorithm: score = upvotes - downvotes, weighted by recency (logarithmic)
- First 10 upvotes = same weight as next 100 (early momentum is everything)
- First 1-2 hours critical — early downvotes kill a post permanently
- Comments ranked similarly: early upvoted comments "lock" at top
- Google indexes Reddit HEAVILY — top posts rank in search for 6-24 months
- This is why replying to Google-ranking old posts = passive long-term traffic

## Content Formats Ranked
1. "I did X. Here's what happened." (experience share) → highest trust
2. "Guide: How to do X" (tutorial) → gets bookmarked, long Google shelf life
3. "I analyzed X for Y days" (data/research) → upvoted for effort, often viral
4. "AMA about X" → great if you have genuine expertise
5. "I built X" (show & tell) → works in r/SideProject, r/startups

## Reply Strategy (often MORE effective than posting)
- Find posts ALREADY ranking on Google for your keywords → reply with value + product mention
  These get steady traffic for months. Your reply = passive leads forever.
- Reply within 2 hours of new posts (early replies get top position)
- Reply structure: 3-5 sentences genuine help + 1 sentence natural product mention
- Never reply from alt accounts (Reddit detects cross-account patterns)

## Anti-Ban Survival
- Never same link to multiple subreddits simultaneously
- Space self-promotional posts by 7+ days minimum
- If post removed: DON'T repost. Message mods politely, ask why.
- Vary content format and writing style between posts
- Old account with history >> new account (CQS advantage)
- One bad move can trigger shadowban (you post, nobody sees — check r/ShadowBan)

## Result Attribution (the hard part)
Reddit doesn't support clean UTM tracking. Use multi-signal approach:
1. Reddit metrics: karma gained, post views, comment upvotes
2. Holy grail: OTHER users mentioning your brand in threads you didn't participate in
3. Website: reddit.com referral traffic + LLM referral traffic (ChatGPT/Perplexity citing your Reddit posts)
4. Best attribution method: add "Where did you hear about us?" with "Reddit" option on signup form""",
        },
    ],

    "partnerships": [
        {
            "name": "product_hunt_launch",
            "source": "inferen-sh/skills (8.1K installs)",
            "description": "Product Hunt 发布完整策略",
            "framework": """发布前(2周):
- 准备 Gallery (5张截图+1个视频)
- 写好 tagline (60字符内)、description、first comment
- 联系 5-10 个 Hunter 找人帮你 Hunt
- 在社媒预热

发布日:
- 太平洋时间 00:01 发布
- 第一条评论: 创始人故事+为什么做这个
- 当天持续回复每一条评论
- 社媒同步推广

发布后:
- 给所有评论者发感谢邮件
- 把 PH badge 加到网站
- 发布复盘帖子""",
        },
        {
            "name": "influencer_outreach",
            "source": "dengineproblem/agents-monorepo (79 installs)",
            "description": "博主外联策略",
            "framework": """发现:
- 搜索 YouTube/Twitter/博客中讨论相关话题的人
- 优先 1K-10K 粉丝（小博主回复率高、性价比好）
- 评估: 受众匹配度、互动率、内容质量

外联:
- 邮件主题行: 具体+个人化（不要"合作邀请"）
- 第一句: 证明你看过对方的内容
- 价值交换: 你能给对方什么
- CTA: 一个明确的下一步

合作模式:
- 免费试用换评测（成本最低）
- 赞助内容（$100-1000 per post for small creators）
- 分佣/联盟（长期关系）""",
        },
    ],

    "paid_ads": [
        {
            "name": "ad_campaign_framework",
            "source": "openclaudia + superamped",
            "description": "广告投放框架",
            "framework": """测试流程:
1. 小额测试($20-50): 3组创意 × 2组受众
2. 72小时后分析: CPC、CTR、转化率
3. 砍掉最差的，放大最好的
4. 持续迭代

创意角度(5种):
- Problem: 展示痛点
- Solution: 展示结果
- Comparison: 和替代方案对比
- Proof: 用户案例/数据
- Curiosity: 激发好奇心

预算低于$500/月的建议:
- 不做 Google Ads（CPC 太贵）
- Reddit Ads 最便宜（CPM $0.5-2）
- 或者完全不做广告，把钱投到内容/合作上""",
        },
    ],

    "designer": [
        {
            "name": "social_design",
            "source": "eachlabs/skills (432 installs) + 404kidwiz",
            "description": "社媒视觉设计规范",
            "framework": """尺寸速查:
- Instagram: 1080×1080 (方) / 1080×1350 (竖)
- Twitter/X: 1200×675
- LinkedIn: 1200×627
- Facebook: 1200×630
- YouTube 缩略图: 1280×720
- TikTok 封面: 1080×1920

设计原则:
- 3秒法则: 最重要的信息最大最醒目
- 移动优先: 字号至少 24px
- 品牌一致: 固定色板(最多3色) + 固定字体
- 对比度: 文字和背景对比度 > 4.5:1

非设计师执行方案:
- Canva: 直接用模板，改文字和颜色
- Figma: 社区模板
- AI 生图: DALL-E/Midjourney/Ideogram
- 截图工具: 产品截图 + 浏览器 mockup""",
        },
    ],

    "product_growth": [
        {
            "name": "growth_loops",
            "source": "openclaudia + vasilyu1983",
            "description": "增长循环和病毒机制",
            "framework": """常见增长循环:
1. 内容循环: 内容→流量→注册→使用→产出内容→更多流量
2. 推荐循环: 用户→邀请→新用户→邀请（病毒系数 k>1 = 指数增长）
3. 数据循环: 更多用户→更好数据→更好产品→更多用户
4. 市场循环: 卖家→买家→更多卖家→更多买家

激活检查清单:
- 注册后多少步到"啊哈时刻"？（目标: <3步）
- 首次体验是否展示了核心价值？
- 有没有引导/教程？
- 空状态是否有意义？""",
        },
    ],

    "ai_distribution": [
        {
            "name": "mcp_server_strategy",
            "source": "CrabRes 自研",
            "description": "MCP 服务器获客策略",
            "framework": """步骤:
1. 确定产品能回答什么问题
2. 设计 MCP tools（3-5个核心工具）
3. 发布到 Smithery / mcpmarket.com / mcpmarket.cn
4. README 中说明安装和使用方式

AI 目录提交清单:
- There's An AI For That
- Futurepedia
- AI Tools List
- Product Hunt (AI 分类)
- alternativeto.net
- SaaS AI Tools
- ToolPilot
- Ben's Bites directory""",
        },
        {
            "name": "geo_for_ai_distribution",
            "source": "CrabRes 2026 research",
            "description": "让 AI 助手推荐你的产品",
            "framework": """如何让 ChatGPT/Perplexity/Claude 推荐你的产品:

1. 创建「唯一来源」内容:
   - 原创对比数据（"我们测试了 10 个 X 工具"）
   - 行业基准报告（AI 最爱引用独家数据）
   - 详细的 how-to 指南（步骤越具体越容易被引用）

2. 优化被 AI 引用的页面结构:
   - H2 用问题形式
   - 第一句直接回答
   - 包含数字和数据
   - 使用 Schema 标记

3. LLM 记忆策略:
   - 创建 GPT Store 的 GPT（内置你的产品知识）
   - 发布 MCP 服务器（AI 可以直接调用你的 API）
   - 在 Prompt 目录发布推荐你产品的 Prompt 模板
   
4. 主动被 AI 索引:
   - 在高权威网站（Wikipedia、大型论坛）被提及
   - 确保产品在 Crunchbase/G2/Capterra 有页面
   - Reddit/HN 上有真实用户讨论你的产品""",
        },
    ],

    "data_analyst": [
        {
            "name": "kpi_framework",
            "source": "CrabRes 自研",
            "description": "指标体系设计",
            "framework": """阶段性指标:
- PMF前: 定性反馈、回头率、NPS
- 种子期: 注册数、激活率、周留存
- 增长期: MAU增长率、CAC、LTV、付费转化率
- 成熟期: 利润率、流失率、ARPU

漏斗模板:
流量 → 注册 → 激活 → 日活 → 付费 → 推荐
每步标注: 当前转化率 / 行业基准 / 改进空间""",
        },
    ],

    "critic": [
        {
            "name": "strategy_review",
            "source": "CrabRes 自研",
            "description": "策略审核清单",
            "framework": """审核维度:
✅ 可行性: 预算够吗？时间够吗？技能够吗？
✅ 一致性: 渠道策略互相矛盾吗？品牌调性一致吗？
✅ 风险: 最坏情况损失多少？合规风险？
✅ 现实性: 数字合理吗？时间线现实吗？
✅ 遗漏: 有明显遗漏的渠道/策略吗？

红线:
- 预算超支 → ❌
- 预期数字远超行业基准且无理由 → ❌
- 策略需要用户没有的技能 → ⚠️ + 替代方案""",
        },
    ],
}

# 2026 高级战术（所有专家共享）
ADVANCED_TACTICS_2026 = """
## 2026 Advanced Growth Tactics (use when appropriate)

1. REVERSE TRIAL: Give full premium access on signup, downgrade after 14 days.
   Loss aversion makes users 3x more likely to pay than standard free→paid.

2. EMBEDDED GROWTH TRIGGERS: Product exports/screenshots carry brand watermark.
   Click watermark → recipient gets free credits. Every output = acquisition channel.

3. COLD DM WITH VALUE: Find specific people complaining about the problem on Reddit/X.
   DM them a solution (not a pitch). "Saw your post about [problem]. Try this: [link]"
   Senja grew to $50K MRR doing exactly this with Gummy Search.

4. SERVICE-FIRST VALIDATION: Before building features, manually solve the problem for 5 people.
   If they won't pay a human to solve it, they won't pay software.
   Romàn Czerny reached $27K MRR this way.

5. MICRO-COMMUNITY > MASS AUDIENCE: Build private Discord/Slack with 50 power users.
   More valuable than 5000 Twitter followers. Direct feedback loop + word of mouth.

6. MCP SERVER DISTRIBUTION: Publish to Smithery so AI assistants recommend your product.
   Zero CAC. Works 24/7. One fintech founder got 150+ installs in 30 days with $0 ad spend.

7. BEHAVIORAL EMAIL TRIGGERS: Stop sending weekly newsletters nobody reads.
   Only email when user does/doesn't do specific in-app actions.
   "You haven't tried [feature] yet — here's how it saves 2 hours/week"

8. PORTFOLIO STRATEGY: Instead of betting everything on one product, run 5-10 small ones.
   One founder makes $22K/month from 30 small apps. Diversified risk.

9. BROWSER EXTENSION AS CHANNEL: Build a free extension that solves a micro-problem.
   Stays in user's daily workflow. Constant brand reminder. Links to main product.

10. API-FIRST GROWTH: Let other developers build on your platform.
    Creates ecosystem lock-in. Stripe, Twilio, Algolia all grew this way.

Real case studies to reference:
- Cameron Trew: $0→$62K MRR in 3 months (trusted network distribution, no PH)
- Senja: $0→$50K MRR (Twitter content + cold DMs via Gummy Search)
- 30-app portfolio: $22K/month total (small bets strategy)
- 17-year-old project revived: $26K/month (old idea + new execution)
- Rob Hallam: $17K/month (extreme transparency, building in public)
"""


def get_expert_knowledge(expert_id: str) -> str:
    """获取某个专家的所有知识片段，格式化为可注入 prompt 的文本"""
    knowledge_items = EXPERT_KNOWLEDGE.get(expert_id, [])

    parts = []

    if knowledge_items:
        parts.append("\n## Your Professional Frameworks\n")
        for item in knowledge_items:
            parts.append(f"### {item['name']} ({item['source']})")
            parts.append(item["framework"])
            parts.append("")

    # 所有专家都获取 2026 高级战术
    parts.append(ADVANCED_TACTICS_2026)

    return "\n".join(parts)
