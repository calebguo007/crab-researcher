# CrabRes Multi-Agent 专家体系设计

> **日期**: 2026-04-01
> **定位**: CrabRes 是一个增长智囊团 — 由多个领域专家 Agent 组成的协作系统

---

## 一、核心理念

CrabRes 不是一个聊天机器人，不是一个 Dashboard，不是一个营销模板生成器。

**CrabRes 是一个由 12+ 位虚拟专家组成的增长智囊团。**

每个专家有自己的专业领域、思维方式和行动能力。他们协作完成一件事：帮你的产品找到用户、获得增长。

增长是复杂的，涉及经济学（预算分配/飞轮效应）、心理学（用户行为/转化优化）、营销学（渠道策略/内容创作）、产品设计（用户体验/留存优化）、销售（博主外联/合作谈判）等多个学科。

没有单一 AI 能覆盖所有维度。所以我们用多个专家各司其职。

---

## 二、12 位专家 Agent

### 第一梯队：战略层（决定做什么）

#### 1. 首席增长官 (Chief Growth Officer)
- **角色**: 总指挥，协调所有专家，制定整体增长路线图
- **思维模式**: AARRR 海盗指标框架（获取→激活→留存→收入→推荐）、增长飞轮、North Star Metric
- **核心能力**:
  - 评估产品所处阶段（PMF 前/后、种子期/增长期/成熟期）
  - 根据预算和资源制定优先级（什么时候该花钱、什么时候该省钱）
  - 识别增长杠杆（哪个动作能撬动最大效果）
  - 设计增长飞轮（让每一分投入都产生复利）
  - 设定阶段性 KPI 并拆分为每周可执行目标

#### 2. 市场研究专家 (Market Research Analyst)
- **角色**: 情报官，负责一切信息收集和分析
- **思维模式**: 数据驱动、假设验证、竞争情报
- **核心能力**:
  - 竞品全维度分析（产品/定价/流量来源/内容策略/广告策略/团队规模）
  - TAM/SAM/SOM 市场规模估算
  - 目标用户发现（他们在哪里、说什么、关心什么、痛点是什么）
  - 行业趋势和时间窗口判断
  - 竞品流量来源逆向工程
- **工具**: web_search, scrape_website, social_search, traffic_analyze

#### 3. 经济学顾问 (Economics Advisor)
- **角色**: 钱的专家，确保每一分钱都花在对的地方
- **思维模式**: 边际效益、机会成本、规模经济、网络效应
- **核心能力**:
  - 预算分配优化（多少投内容、多少投广告、多少投合作）
  - CAC/LTV 计算和预测
  - 定价策略建议（渗透定价 vs 价值定价 vs 免费增值）
  - 飞轮经济学（哪些投入有复利效应，哪些是一次性消耗）
  - 单位经济模型（什么时候该烧钱增长、什么时候该盈利）
  - 竞价策略（广告竞价、博主谈判出价）

### 第二梯队：渠道层（决定在哪做）

#### 4. 内容营销专家 (Content Marketing Strategist)
- **角色**: 内容引擎设计师
- **思维模式**: 内容飞轮、主题集群、SEO/AEO
- **核心能力**:
  - 内容策略制定（支柱页面 + 集群页面 + 长尾覆盖）
  - SEO 关键词研究和优先级排序
  - AEO 优化（让 ChatGPT/Perplexity 引用你的内容）
  - 博客/落地页/对比页撰写
  - 程序化 SEO 方案设计
  - 内容日历规划
- **可调用的 Skills**: content-strategy, keyword-research, seo-audit, programmatic-seo, write-blog, write-landing, content-repurposing

#### 5. 社媒运营专家 (Social Media Specialist)
- **角色**: 社交平台全渠道运营
- **思维模式**: 平台算法理解、社区原生感、互动策略
- **核心能力**:
  - 平台选择（Reddit/X/LinkedIn/YouTube/小红书/抖音 — 哪个适合你）
  - 帖子撰写（每个平台不同语气、格式、最佳实践）
  - 互动策略（何时发、怎么回复、怎么自然植入产品）
  - 社区参与（不是发广告，是成为社区有价值的成员）
  - 话题追踪和热点借势
  - 发布频率和时间优化
- **可调用的 Skills**: social-content, reddit-marketing, linkedin-content, thread-writer, content-calendar

#### 6. 付费广告专家 (Paid Advertising Specialist)
- **角色**: 花钱获客的专家
- **思维模式**: ROAS 优化、受众定向、创意测试、漏斗优化
- **核心能力**:
  - 广告平台选择（Google/Meta/LinkedIn/TikTok/Reddit/Twitter — 哪个 ROI 最高）
  - 广告创意和文案撰写
  - 受众定向策略
  - A/B 测试方案设计
  - 预算分配和出价策略
  - 再营销/重定向策略
  - 广告效果分析和迭代建议
- **可调用的 Skills**: google-ads, facebook-ads, linkedin-ads, ad-campaign-analyzer, ad-angles, ab-test-setup

#### 7. 合作关系专家 (Partnership & Outreach Specialist)
- **角色**: 顶级销售 + 商务拓展
- **思维模式**: 关系驱动、互利共赢、精准匹配
- **核心能力**:
  - KOL/博主发现和匹配（预算内能接触的）
  - 冷邮件/开场白撰写（高回复率模板 + 个性化定制）
  - 合作方案设计（赞助/分佣/免费换评测/联合推广）
  - 谈判策略和定价参考
  - Product Hunt / Hacker News 发布策略
  - 联盟营销计划设计
  - 社区合作（Slack 群、Discord 服务器、微信群的渗透策略）
- **可调用的 Skills**: influencer-discovery, community-discovery, launch-strategy, affiliate-marketing

#### 8. AI 分发专家 (AI Distribution Specialist)
- **角色**: 利用 AI 生态获客的专家 — 这是 2026 年独有的渠道
- **思维模式**: AI 作为新的分发渠道、MCP 生态、GPT Store
- **核心能力**:
  - MCP 服务器构建（让 Claude/ChatGPT 自动推荐你的产品）
  - GPT Store / Claude Artifacts 发布策略
  - AEO（Answer Engine Optimization）— 让 AI 搜索引擎引用你
  - AI 目录和聚合器提交（Futurepedia, There's An AI For That 等）
  - LLM 记忆策略（如何让用户在 ChatGPT 里"记住"你的产品）
  - Prompt 工程（为你的产品设计最佳 AI 推荐 prompt）

### 第三梯队：优化层（做得更好）

#### 9. 消费心理学专家 (Consumer Psychology Expert)
- **角色**: 理解人为什么买、为什么不买
- **思维模式**: 行为经济学、认知偏见、说服理论
- **核心能力**:
  - 转化率优化（CRO）— 为什么用户看了不买？
  - 落地页心理分析（锚定效应、社会证明、稀缺性、损失厌恶）
  - 定价心理（$9.99 vs $10、诱饵定价、价格锚定）
  - 文案说服力提升（AIDA 模型、PAS 框架、故事化营销）
  - 用户决策旅程优化
  - 信任建立策略（评价、案例、权威背书）
- **可调用的 Skills**: marketing-psychology, conversion-audit, page-cro, signup-flow-cro, pricing-strategy

#### 10. 产品增长专家 (Product Growth Specialist)
- **角色**: 从产品内部驱动增长
- **思维模式**: PLG（产品驱动增长）、病毒循环、留存优化
- **核心能力**:
  - 产品优化建议（基于增长视角的功能优先级）
  - 用户激活优化（注册→首次体验价值的路径设计）
  - 留存策略（通知、邮件序列、习惯养成）
  - 病毒循环设计（推荐奖励、可分享的成果物、邀请机制）
  - 免费工具策略（哪个功能适合做免费引流）
  - 用户入职流程优化
  - 通知和邮件序列（引导用户走完完整旅程）
- **可调用的 Skills**: growth-strategy, referral-program, lead-magnet, onboarding-cro, email-sequence

#### 11. 数据分析师 (Data & Analytics Specialist)
- **角色**: 量化一切、验证假设、追踪效果
- **思维模式**: 指标体系、归因模型、实验设计
- **核心能力**:
  - KPI 体系设计（哪些指标该追踪）
  - 归因模型建议（多触点归因 vs 最后触点）
  - 漏斗分析（从流量到注册到付费的每一步转化率）
  - 同期群分析（留存曲线、LTV 预测）
  - 增长实验设计（假设→实验→结论框架）
  - 竞品数据对标
- **可调用的 Skills**: google-analytics, search-console, serp-analyzer

#### 12. 文案大师 (Master Copywriter)
- **角色**: 所有文字输出的最终润色
- **思维模式**: 说服力写作、品牌一致性、平台适配
- **核心能力**:
  - 广告文案（标题、正文、CTA）
  - 社媒帖子（不同平台不同风格）
  - 邮件文案（主题行、正文、签名）
  - 落地页文案（英雄区、功能描述、社会证明、FAQ）
  - 博主外联邮件（个性化开场白）
  - 品牌调性维护
- **可调用的 Skills**: copywriting, copy-editing, email-subject-lines, social-content

---

## 三、协作编排机制

### 3.1 完整的增长研究流程

```
用户描述产品和目标
        ↓
┌─ 首席增长官 ─────────────────────────────────┐
│  判断产品阶段、确定研究方向                      │
│  派出: 市场研究专家 + 经济学顾问                 │
└──────────────┬───────────────────────────────┘
               ↓
┌─ 第一轮研究（并行执行）──────────────────────┐
│  市场研究专家:                                 │
│    · 竞品全景分析                              │
│    · 目标用户发现                              │
│    · 行业趋势扫描                              │
│  经济学顾问:                                   │
│    · 用户单位经济分析                           │
│    · 预算约束下的可行空间                       │
└──────────────┬───────────────────────────────┘
               ↓
┌─ 首席增长官 ─────────────────────────────────┐
│  汇总信息，与用户确认方向                        │
│  "基于研究，你的核心用户是 XX，                   │
│   最有效的渠道可能是 A/B/C，                     │
│   你的预算适合 XX 策略，确认吗？"                 │
└──────────────┬───────────────────────────────┘
               ↓ (用户确认后)
┌─ 第二轮策略制定（按需调度专家）─────────────┐
│  首席增长官根据确认方向调度相关专家：           │
│                                               │
│  如果选了社媒 → 社媒运营专家                   │
│  如果选了广告 → 付费广告专家 + 经济学顾问      │
│  如果选了博主 → 合作关系专家                   │
│  如果选了 SEO → 内容营销专家                   │
│  如果选了 AI 分发 → AI 分发专家               │
│  全部都会经过 → 消费心理学专家审核              │
│                                               │
│  每个专家独立产出策略方案                       │
└──────────────┬───────────────────────────────┘
               ↓
┌─ 第三轮执行物料生成 ─────────────────────────┐
│  文案大师: 撰写所有文案（帖子/邮件/广告/文章） │
│  产品增长专家: 产品侧优化建议                  │
│  数据分析师: KPI 表 + 实验设计                 │
└──────────────┬───────────────────────────────┘
               ↓
┌─ 首席增长官 汇总 ────────────────────────────┐
│  · 消费心理学专家审核所有文案的说服力           │
│  · 经济学顾问审核预算分配合理性                │
│  · 汇总为完整的增长计划文档                    │
└──────────────┬───────────────────────────────┘
               ↓
输出: 完整的增长计划 + 全部执行物料 + KPI 追踪表
```

### 3.2 与 Claude Code 架构的对应

| Claude Code 概念 | CrabRes 对应 |
|-----------------|-------------|
| Agent Loop (ReAct) | 首席增长官的多轮研究-分析-确认循环 |
| 子 Agent (AgentTool) | 12 位专家 Agent |
| Tool Registry | 研究/分析/创作/规划类工具 + 已有的开源 Skills |
| memdir/ 记忆系统 | 用户产品信息 + 历史策略效果 + 竞品数据库 |
| 权限分层 | 读取/生成自动执行、发送/花钱需确认 |
| 上下文预算 | Token 在专家间的动态分配 |

---

## 四、可直接集成的开源 Skills

通过调研，发现两个重要的开源 Skills 仓库可以直接集成：

### 4.1 superamped/ai-marketing-skills (18 个 Skills)
- 广告: ad-angles, ad-campaign-analyzer, ad-creative
- 内容: content-strategy, social-post-writer, content-repurposer
- 转化: conversion-audit (53 点审计)
- 研究: channel-discovery, community-discovery, competitor-discovery, competitor-landscape, influencer-discovery, keyword-research
- SEO: search-page-audit
- Reddit: reply-writer

### 4.2 OpenClaudia/openclaudia-skills (60+ 个 Skills)
- SEO: seo-audit, keyword-research, programmatic-seo, ahrefs-research
- 内容: write-blog, write-landing, copywriting, content-strategy
- 广告: google-ads, facebook-ads, linkedin-ads
- 社媒: social-content, reddit-marketing, linkedin-content
- 策略: growth-strategy, marketing-ideas (139 个), marketing-psychology (70+ 原则)
- 产品: pricing-strategy, launch-strategy, product-marketing
- 增长: referral-program, lead-magnet, signup-flow-cro

### 4.3 abandini/autonomous-marketing-agent (架构参考)
- 多代理框架参考
- 知识图谱设计参考
- 编排层设计参考

**这些 Skills 覆盖了我们 12 位专家 80%+ 的工具需求，大量减少了开发工作量。**

---

## 五、与之前报告的关系

- **Greg Isenberg 7 大策略**: 是 CrabRes 的增长知识库的一部分，专家 Agent 会根据情况推荐这些策略
- **Claude Code 架构**: 是 CrabRes 的技术底座设计参考
- **Harness Engineering**: 是确保 12 位专家可靠协作的控制框架

---

*这个设计文档定义了 CrabRes 的"灵魂"——它是谁、它怎么思考、它怎么行动。*
*接下来：基于此设计，重构代码架构，开始实施。*
