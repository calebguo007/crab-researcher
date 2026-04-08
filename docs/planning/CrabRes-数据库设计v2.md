# CrabRes 数据库设计 v2

> 当前问题：核心增长数据存在 JSON 文件里，无法跨用户聚合、无法关联查询、并发不安全。
> 目标：全部迁移到 PostgreSQL (Neon)，为"增长复利"壁垒打好数据基础。
>
> 更新时间：2026-04-03

---

## 一、当前问题审计

### 两套割裂的存储

| 存储 | 内容 | 问题 |
|------|------|------|
| **PostgreSQL (Neon)** | users, monitoring_tasks, monitoring_results, reports, rag_documents, token_usage_logs, user_products, competitor_discoveries, competitor_products | 9 张表中 7 张废弃（老 v1 B2B 调研遗留） |
| **JSON 文件 (.crabres/)** | product, loop_state, growth_plan, actions, results, experiments, learnings, growth_log, playbooks, journal | Agent 核心数据全在这里，无法聚合、并发不安全 |

### 具体问题

1. **无法跨用户聚合**：每个用户的 JSON 在 `.crabres/memory/{user_id}/` 下，聚合需遍历文件系统
2. **无法关联查询**：如"Reddit 帖子平均得多少分"需要手动 parse JSON
3. **并发不安全**：多请求同时写同一个 JSON = 数据丢失
4. **数据重复**：experiments.py 的 actions 和 growth_log.py 的 actions 是两套独立系统
5. **老表浪费**：PostgreSQL 里大部分表不再使用

---

## 二、新数据库设计

### 表结构总览

```
PostgreSQL (Neon)
├── users                    # 用户（保留）
├── growth_actions           # 增长行动记录 ← 核心
├── growth_results           # 行动结果 + 自动评分 ← 核心
├── growth_experiments       # 实验（一批行动）
├── growth_learnings         # 从数据中提取的增长规律 ← 壁垒
├── growth_strategies        # 每日策略
├── channel_weights          # 渠道权重快照（每日计算）
├── playbook_records         # Playbook 执行记录
├── agent_sessions           # Agent 会话状态
├── token_usage_logs         # Token 消耗（保留）
└── rag_documents            # 知识库向量（保留）
```

### 表关系图

```
users (1)
  ├──→ (N) growth_actions
  │         ├──→ (N) growth_results
  │
  ├──→ (N) growth_experiments
  │         ├──→ (N) growth_actions (via experiment_id)
  │         ├──→ (N) growth_learnings
  │
  ├──→ (N) growth_strategies
  ├──→ (N) channel_weights
  ├──→ (N) playbook_records
  ├──→ (N) agent_sessions
  └──→ (N) token_usage_logs
```

### 核心表字段说明

#### growth_actions — 增长行动
```sql
id              SERIAL PRIMARY KEY
uid             VARCHAR(20) UNIQUE     -- 业务 ID: act-xxxx
user_id         INT REFERENCES users   -- 谁做的
date            VARCHAR(10)            -- 哪天做的
platform        VARCHAR(30)            -- reddit/x/xiaohongshu/...
action_type     VARCHAR(30)            -- post/reply/dm/email/...
description     TEXT                   -- 一句话描述
content_preview TEXT                   -- 发布内容摘要
url             VARCHAR(1000)          -- 发布后的链接
target          VARCHAR(255)           -- 目标（r/SaaS, @某博主）
time_spent_min  INT DEFAULT 0          -- 花了多少分钟
experiment_id   INT REFERENCES growth_experiments  -- 属于哪个实验
playbook_id     VARCHAR(20)            -- 关联的 playbook
status          VARCHAR(20)            -- pending/posted/tracked/failed
created_at      TIMESTAMP

INDEXES:
  (user_id, date)      -- 按日期查询
  (user_id, platform)  -- 按渠道聚合
```

#### growth_results — 行动结果 + 自动评分
```sql
id              SERIAL PRIMARY KEY
action_id       INT REFERENCES growth_actions
user_id         INT REFERENCES users
date            VARCHAR(10)
metrics         JSON                   -- {"likes": 10, "upvotes": 50}
verdict         VARCHAR(20)            -- great/good/mediocre/poor
score           INT                    -- 0-100
auto_tracked    BOOLEAN DEFAULT FALSE  -- 自动追踪 vs 手动填
notes           TEXT
tracked_at      TIMESTAMP

INDEXES:
  (user_id, date)
  (user_id, verdict)   -- 快速统计好/坏分布
```

#### growth_learnings — 增长规律（壁垒数据）
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users
learning        TEXT                   -- "Reddit 数字标题帖转化率 3.5x"
platform        VARCHAR(30)
confidence      FLOAT DEFAULT 0.5     -- 0-1（数据点越多越高）
data_points     INT DEFAULT 1          -- 支撑的数据点数量
experiment_id   INT REFERENCES growth_experiments
created_at      TIMESTAMP

INDEXES:
  (user_id, platform)
```

#### channel_weights — 渠道权重快照
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users
date            VARCHAR(10)
platform        VARCHAR(30)
weight          FLOAT                  -- 0-1
avg_score       FLOAT
action_count    INT
created_at      TIMESTAMP
```

---

## 三、跨用户聚合查询示例

### 壁垒查询：所有用户的 Reddit 平均效果
```sql
SELECT 
    ga.platform,
    COUNT(*) as total_actions,
    AVG(gr.score) as avg_score,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gr.score) as median_score
FROM growth_actions ga
JOIN growth_results gr ON ga.id = gr.action_id
WHERE ga.platform = 'reddit'
GROUP BY ga.platform;
```

### 渠道对比：哪个渠道 ROI 最高
```sql
SELECT 
    ga.platform,
    COUNT(*) as actions,
    AVG(gr.score) as avg_score,
    SUM(CASE WHEN gr.verdict = 'great' THEN 1 ELSE 0 END) as great_count,
    AVG(ga.time_spent_min) as avg_time
FROM growth_actions ga
JOIN growth_results gr ON ga.id = gr.action_id
WHERE ga.user_id = ?
GROUP BY ga.platform
ORDER BY avg_score DESC;
```

### 时间趋势：用户的增长是否在加速
```sql
SELECT 
    date,
    AVG(score) as daily_avg_score,
    COUNT(*) as daily_actions
FROM growth_results
WHERE user_id = ?
GROUP BY date
ORDER BY date;
```

---

## 四、迁移计划

### Phase 1: 建表（立刻）
- [x] growth.py 模型已写好
- [ ] 运行 create_all 创建表
- [ ] 验证 Neon 上表结构正确

### Phase 2: 双写（过渡期）
- [ ] 新数据同时写 JSON + PostgreSQL
- [ ] 旧的 GrowthLog / ExperimentTracker 加一层 PostgreSQL 写入
- [ ] 读取仍从 JSON（保证不影响现有功能）

### Phase 3: 切换读取
- [ ] 读取切换到 PostgreSQL
- [ ] 跨用户聚合查询走 SQL
- [ ] CLI growth_loop.py 改用 PostgreSQL

### Phase 4: 清理
- [ ] 删除废弃的 v1 表（monitoring_tasks 等）
- [ ] JSON 文件作为备份保留，不再主写
- [ ] 迁移历史 JSON 数据到 PostgreSQL

---

## 五、设计原则

1. **每个 action 必须有 result** — 没有 result 的 action 系统会提醒
2. **自动评分** — 不依赖用户判断"好不好"，系统基于 benchmark 自动打分
3. **跨用户可聚合** — 匿名化后的数据是壁垒（45,000 条坑位数据）
4. **渠道权重动态** — 不是写死的"Reddit 好"，是基于数据算出来的
5. **索引设计** — 最常用的查询路径（user_id + date, user_id + platform）有索引
6. **JSON 字段兜底** — metrics、phases 等结构灵活的字段用 JSON，核心查询字段用独立列
