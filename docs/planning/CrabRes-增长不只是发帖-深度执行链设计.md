# CrabRes: 增长不只是发帖 — 深度执行链设计

> **核心反思**: 我们把"增长"窄化成了"社媒发帖 + 追踪 likes"。
> 但一个做 AI 项链的人、一个做线下烘焙店的人、一个做 B2B SaaS 的人——
> 他们的增长路径完全不同，每一条路径展开来都是一个深到底的专业。
>
> CrabRes 不能只做"帮你写帖子"，要做"帮你把每条增长路径拆到可执行的 SOP"。
>
> 更新时间：2026-04-02

---

## 一、问题诊断

### 当前 CrabRes 的输出深度

```
用户: "我做了一个 AI 项链，帮我增长"

CrabRes 当前输出:
  "建议1: 在 Instagram 上做内容营销"
  "建议2: 找科技博主合作"  
  "建议3: 考虑 Kickstarter 众筹"
  "建议4: 投 Facebook/Instagram 广告"
  "建议5: 参加 CES 展会"
  
  + 一段 Reddit 帖子文案
```

**问题：每个"建议"只有一句话。** 用户看了以后还是不知道具体怎么做。他用 ChatGPT 也能得到一样的结果。

### 用户真正需要的输出深度

```
用户: "我做了一个 AI 项链，帮我增长"

CrabRes 应该输出:

增长路径 A: KOL/博主种草 [执行链: 22 步]
增长路径 B: 众筹预热 [执行链: 18 步]
增长路径 C: 社媒内容矩阵 [执行链: 15 步]  
增长路径 D: 精准广告投放 [执行链: 20 步]
增长路径 E: 展会/活动曝光 [执行链: 12 步]
增长路径 F: PR/媒体报道 [执行链: 16 步]

每条路径展开后是：
  → 具体步骤（第一步做什么、第二步做什么）
  → 每步需要的工具（用什么平台、什么软件）
  → 每步需要的模板（邮件怎么写、合同怎么签）
  → 每步需要的预算（花多少钱、花在哪）
  → 每步的时间线（第几天到第几天）
  → 每步的成功标准（怎么判断做对了）
  → 每步的常见坑（别人踩过什么坑）
```

### 差距的本质

**不是缺 AI 能力，是缺"领域知识的结构化深度"。**

CrabRes 的 13 个专家有人格、有知识框架，但每个专家的知识还停留在"方法论级别"（AIDA 框架、CAC/LTV 公式），没有到"SOP 级别"（第一步打开 Modash.io 搜索博主、第二步用这个模板发邮件、第三步寄样用什么快递）。

---

## 二、解决方案：增长执行链（Growth Playbook）

### 核心概念

不再输出"建议"，而是输出**可执行的剧本（Playbook）**。

每个 Playbook 是一条完整的增长路径，包含：

```
Playbook = {
    name: "KOL 博主种草",
    适用场景: "有实物产品、预算 $500-5000、3个月内要见效",
    
    phases: [
        {
            phase: "准备期",
            duration: "第 1-3 天",
            steps: [
                {
                    step: 1,
                    title: "定义理想博主画像",
                    detail: "具体描述...",
                    tools: ["Modash.io", "Social Blade", "手动 Instagram 搜索"],
                    template: "博主筛选表模板（Excel/Notion）",
                    budget: "$0",
                    output: "一张包含 30 个候选博主的表格",
                    success_criteria: "至少 30 个候选，每个有粉丝量/互动率/邮箱",
                    common_mistakes: ["只找大博主（贵且不回复）", "不看互动率只看粉丝量"],
                },
                {
                    step: 2,
                    title: "搜索并筛选候选博主",
                    ...
                },
            ]
        },
        {
            phase: "执行期", 
            duration: "第 4-14 天",
            steps: [...]
        },
        {
            phase: "追踪期",
            duration: "第 15-30 天", 
            steps: [...]
        }
    ],
    
    budget_breakdown: {...},
    expected_results: {...},
    risk_factors: [...],
}
```

### 这比"建议"好在哪

| 维度 | 当前（建议级） | 目标（Playbook 级） |
|------|--------------|-------------------|
| **粒度** | "找博主合作" | 22 步 SOP，每步有模板和工具 |
| **可执行性** | 用户不知道从哪开始 | 第 1 步就能开始做 |
| **可追踪** | 无法衡量进度 | 每步有明确的 output 和 success criteria |
| **可学习** | 做完不知道做对没 | 每步有 common_mistakes 帮你避坑 |
| **可迭代** | 做一次就结束了 | 追踪期有数据 → 调整下一轮 |

---

## 三、Playbook 库设计

### 按产品类型的主要增长路径

#### 实物产品（AI 项链、智能硬件、消费品）

| Playbook | 核心动作 | 预算 | 时间 |
|----------|---------|------|------|
| **KOL 种草** | 找博主 → 谈合作 → 寄样 → 追踪内容 → 计算 ROI | $500-5K | 1-3 月 |
| **众筹发布** | 预热 → 建邮件列表 → Kickstarter 页面 → 发布日 → 后续 | $1K-5K | 2-3 月 |
| **社媒内容矩阵** | 拍摄 → 编辑 → 多平台发布 → 互动 → 建粉丝群 | $0-500 | 持续 |
| **精准广告投放** | 素材制作 → 受众定义 → 小额测试 → 放大 → 优化 | $1K-10K | 持续 |
| **展会曝光** | 选展会 → 展位设计 → 物料准备 → 现场转化 → 跟进 | $2K-20K | 按活动 |
| **PR 媒体** | 写 pitch → 找记者 → 跟进 → 发布后放大 | $0-2K | 1-2 月 |
| **独立站优化** | 落地页 → 产品页 → 购物流程 → 支付 → 复购 | $0-500 | 1-2 周 |

#### SaaS / 数字产品

| Playbook | 核心动作 |
|----------|---------|
| **Reddit 社区增长** | 找子版块 → 提供价值 → 自然引流 → 追踪转化 |
| **SEO + GEO 长线** | 关键词研究 → 内容创作 → 技术 SEO → AI 搜索优化 |
| **Product Hunt 发布** | 预热 → 页面准备 → 发布日作战 → 后续利用 |
| **Build in Public** | X/Twitter 日更 → 里程碑分享 → 免费分析换社会证明 |
| **MCP/AI 分发** | 构建 MCP Server → 发布到 Smithery → AI 目录提交 |
| **冷外联** | 找目标用户 → 个性化 DM/Email → 跟进 → 转化 |
| **免费工具引流** | 构建免费工具 → SEO → 引导到付费产品 |

#### 本地服务 / O2O

| Playbook | 核心动作 |
|----------|---------|
| **本地 SEO** | Google My Business → 本地关键词 → 评价管理 |
| **社群裂变** | 微信群 → 老带新 → 优惠券机制 |
| **异业合作** | 找互补商家 → 联合活动 → 共享客源 |
| **美团/点评运营** | 开店 → 评价 → 活动 → 排名 |

---

## 四、技术实现方案

### 方案核心：Playbook 不是写死的模板，是 Agent 动态生成的

关键区分：
- ❌ 不是预写 100 个 Playbook 存在数据库里
- ✅ 是 Agent 基于研究结果 + 专家知识 + Playbook 结构模板，为每个用户动态生成个性化 Playbook

### 架构变化

```
当前架构:
  用户输入 → 研究 → 专家讨论 → 输出一段文字建议

新架构:
  用户输入 → 研究 → 专家讨论 → 选择 3-5 条增长路径
  → 每条路径展开为 Playbook（多 phase、每 phase 多 step）
  → 每个 step 有模板/工具/预算/时间线
  → 用户选择优先路径 → 开始执行 → 追踪结果 → 迭代
```

### Playbook 数据模型

```python
@dataclass
class PlaybookStep:
    order: int
    title: str
    detail: str                 # 具体描述
    tools: list[str]            # 推荐工具
    templates: list[str]        # 提供的模板（邮件/表格/文案）
    budget: str                 # 这一步的预算
    duration: str               # 耗时
    output: str                 # 这一步完成后的产出物
    success_criteria: str       # 怎么判断做对了
    common_mistakes: list[str]  # 避坑指南
    status: str = "pending"     # pending / in_progress / done / skipped

@dataclass
class PlaybookPhase:
    name: str                   # "准备期" / "执行期" / "追踪期"
    duration: str               # "第 1-3 天"
    steps: list[PlaybookStep]

@dataclass
class Playbook:
    id: str
    name: str                   # "KOL 博主种草"
    description: str
    suitable_for: str           # "有实物产品、预算 $500-5K"
    phases: list[PlaybookPhase]
    total_budget: str
    expected_timeline: str
    expected_results: str
    risk_factors: list[str]
    priority: int               # Agent 推荐的优先级
```

### Coordinator 如何调度

```
Step 1: 研究用户产品（和现在一样）
Step 2: 圆桌讨论（和现在一样，但增加一个新指令）
Step 3: 选择增长路径
  → Coordinator 根据产品类型、预算、目标、竞品情况
  → 从可能的路径中选出 3-5 条最适合的
  → 用 consult_roundtable 让专家们对每条路径的可行性打分

Step 4: 生成 Playbook（新！）
  → 对每条选中的路径，调度相关专家生成详细 SOP
  → 博主种草 → partnerships + copywriter + designer
  → 广告投放 → paid_ads + designer + psychologist + economist
  → 众筹发布 → partnerships + copywriter + product_growth + psychologist
  → 每个专家负责自己专业维度的 steps

Step 5: 用户选择优先路径
  → "我想先做 KOL 种草，预算 $1000"
  → CrabRes 把这条 Playbook 激活，开始追踪执行进度

Step 6: 逐步执行 + 追踪（接入 Phase A 的实验系统）
```

### 专家如何分工

不再是"每个专家给一段话"，而是"每个专家负责 Playbook 中自己专业的 steps"：

| Playbook | 主要专家 | 负责的 Steps |
|----------|---------|-------------|
| **KOL 种草** | partnerships | 博主发现、外联策略、合同模板 |
| | copywriter | 外联邮件模板、DM 模板、brief 模板 |
| | designer | 产品拍摄指南、内容风格指南 |
| | economist | 预算分配、ROI 计算、分层报价 |
| | data_analyst | 追踪表设计、效果归因 |
| **广告投放** | paid_ads | 平台选择、受众定义、出价策略 |
| | designer | 广告图片尺寸/规格、视频脚本 |
| | psychologist | 文案说服力、CTA 优化 |
| | copywriter | 广告文案（标题+正文+CTA） |
| | economist | 预算分配、ROAS 目标 |
| **众筹发布** | partnerships | 预热策略、Launch 日作战计划 |
| | copywriter | 众筹页面文案、更新帖文案 |
| | designer | 页面视觉规范、视频脚本 |
| | psychologist | 早鸟定价心理、紧迫感设计 |
| | social_media | 社媒预热日历 |

---

## 五、对"深度"的重新定义

### CrabRes 的深度不在于 AI 模型多强

**深度 = 领域知识的结构化程度 × 执行链的完整度**

| 维度 | L1（当前） | L3（目标） |
|------|-----------|-----------|
| **博主合作** | "建议找博主" | 22 步 SOP + 邮件模板 + 筛选表 + 跟进日历 + ROI 追踪 |
| **广告投放** | "建议投 Instagram 广告" | 素材规格 + 受众设置指南 + 出价策略 + A/B 测试方案 + 优化周期 |
| **众筹** | "建议做 Kickstarter" | 预热 60 天倒计时 + 邮件序列 + 页面结构 + 发布日剧本 + 达标后 stretch goals |
| **展会** | "建议参加 CES" | 展位设计指南 + 物料清单 + 现场话术 + 名片跟进模板 + 成本清单 |
| **PR** | "建议联系媒体" | 记者名单 + pitch 模板 + 新闻稿模板 + 跟进策略 + 发布后放大 |

### 这意味着 skills_registry.py 需要大幅扩充

当前 `skills_registry.py` 有 500 行知识。要做到 Playbook 级别的深度，每个 Playbook 模板需要 200-500 行结构化知识。

但**不需要一次性全做**。策略：
1. 先做 3 个最通用的 Playbook 模板（Reddit 社区增长 / KOL 种草 / 冷外联）
2. 每个 Playbook 模板只是一个"结构骨架"
3. Agent 在运行时基于实际研究数据填充具体内容（博主名字、价格、时间线）
4. 用户反馈 + 实验结果 → 逐步丰富 Playbook 细节

---

## 六、执行计划

### 立刻做（本周）

1. **Playbook 数据模型** — `app/agent/memory/playbooks.py`
2. **Coordinator prompt 升级** — 输出 Playbook 而不是纯文本建议
3. **3 个 Playbook 骨架模板** — 注入到 skills_registry.py
   - Reddit/社区增长（适合所有类型）
   - KOL/博主种草（适合有实物或可视化的产品）
   - 冷外联/DM（适合 B2B 和 SaaS）
4. **Surface/Plan 页面适配** — 展示 Playbook 的 phase→step 结构

### 下周做

5. **更多 Playbook 骨架** — 广告投放、众筹、PR、展会
6. **Playbook 执行追踪** — 每个 step 可标记完成，接入实验系统
7. **Playbook 内嵌模板** — 邮件模板、筛选表、brief 等可直接复制

### 后续做

8. **用户自定义 Playbook** — 用户可以修改/创建自己的增长路径
9. **社区共享 Playbook** — 成功的 Playbook 可以分享给其他用户
10. **AI 自动优化 Playbook** — 基于全量用户的实验数据，自动调整 step 顺序和权重

---

## 七、验证标准

### 用户说"卧槽靠谱"的三个信号

1. **"我从没想过要做这一步"** — Playbook 里有用户自己想不到的步骤
2. **"这个模板我直接就能用"** — 不是建议，是可以复制粘贴的模板
3. **"它告诉我第 3 步做错了"** — success_criteria 和 common_mistakes 让用户感觉有个教练在

### 和"玩具"的根本区别

玩具：给你一个建议列表，你自己去想怎么做。
操作系统：给你一本执行手册，告诉你今天做第 7 步，明天做第 8 步，做完了帮你量效果。

---

*这份文档重新定义了 CrabRes 的执行深度。
之前的"L5 闭环路线图"解决的是"追踪和学习"的问题。
这份文档解决的是"到底追踪什么、每一步到底多细"的问题。
两者结合 = 真正的增长操作系统。*
