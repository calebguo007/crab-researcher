# CrabRes 工程差距与补齐计划

> 对比 Manus / OpenClaw / Claude Code，CrabRes 在工程层面的差距和补齐路线。
> 不是功能差距，是"让产品不像玩具"的工程质量差距。
>
> 更新时间：2026-04-03

---

## 核心差距（按投入产出比排序）

| # | 差距 | 对比谁 | 严重度 | 工时 |
|---|------|--------|--------|------|
| **1** | 零测试 | CC 有成千上万测试 | 极大 | 1-2d |
| **2** | 上下文管理粗糙（20条全塞） | CC 动态压缩+缓存 | 大 | 0.5d |
| **3** | 无 MCP 客户端（不能调外部工具） | CC/OpenClaw 原生支持 | 大 | 1d |
| **4** | 工具无重试+结果验证 | CC 每个工具有完整错误处理 | 大 | 0.5d |
| **5** | 无浏览器操控 | Manus Playwright | 大 | 1-2d |
| **6** | 会话状态不完整 | CC 完整检查点 | 大 | 1d |
| **7** | 无结构化日志/metrics | 生产级标配 | 中 | 0.5d |
| **8** | 无连接池/限流 | 生产级标配 | 中 | 0.5d |

## 执行计划

### P0（立刻做）✅ 已完成
- [x] 核心路径测试：31 个 pytest 测试覆盖 7 模块
- [x] 上下文智能压缩：过滤 status、截断工具结果/专家输出、旧对话压缩
- [x] 工具重试 + 结果验证：max 2 retries + 空结果检测

### P1（本周）✅ 已完成
- [x] MCP 客户端：MCPClient + MCPToolBridge + MCPRegistry
- [x] 完整会话检查点：v2 格式，保存完整专家输出 + 版本号 + 时间戳

### P2（下周）✅ 已完成
- [x] Playwright 浏览器操控：BrowseWebsiteTool + httpx 降级
- [x] 结构化日志 + metrics：MetricsCollector + /api/metrics 端点

### 额外修复（2026-04-03）
- [x] Moonshot 直连：LLM 适配器改为 Moonshot 为主力，OpenRouter 为备选
- [x] 强制圆桌触发：搜索 3 轮后注入 SYSTEM OVERRIDE 停止无限搜索
- [x] 循环 Fallback：max_iter 用完后强制圆桌 + 输出，不再静默退出
- [x] CITE RESEARCH 规则：prompt 中强制要求引用搜索数据

### 端到端测试 Take 5 结果（2026-04-03）
- **评分：85/100**（从 5/100 提升到 85/100）
- LLM：Moonshot V1 128K 直连
- 耗时：252.6s | 成本：$0.0875 | Token：109K
- 5 位专家参与（market_researcher, economist, social_media, product_growth, paid_ads）
- 3089 字符实质性回复，含具体竞品数据（Teal 4.8M, Jobscan 2.1M, Kickresume 890K）
- 包含预算分配、渠道策略、可执行步骤

---

*这份文档是 CrabRes-执行计划-下一阶段.md 和 CrabRes-核心壁垒战略.md 的工程补充。
壁垒靠数据和知识，但数据的可靠性靠工程质量。没有测试的壁垒是纸糊的。*

---

### CC 特性补齐（2026-04-03 下午）
- [x] **ULTRAPLAN / Deep Strategy**：后台异步深度策略引擎
  - 触发词检测（"deep strategy" / "pivot" / "重新制定" 等）
  - 后台 asyncio.create_task 执行：多轮搜索 → 8 专家圆桌 → CGO 综合
  - 完成后通知用户 + 持久化结果到磁盘
  - API 端点：`GET /api/deep-strategy/jobs` + `GET /api/deep-strategy/jobs/{id}`
- [x] **Frustration Detection / Mood Sensing**：5 维情绪感知
  - 焦虑 / 失去动力 / 方向迷茫 / 过度乐观 / 执行疲劳
  - 正则模式匹配 + 置信度计算 + 连续短消息加权
  - 自动注入 Coordinator prompt，调整沟通风格
- [x] **圆桌三阶段升级**：
  - Phase 1: Market Intelligence（数据先行）
  - Phase 2: Expert Debate（专家争论 + CGO 判决）
  - Phase 3: Execution Playbooks（可执行计划 + 模板）
  - 强制 Hard Truth + Quick Win + CGO Verdict

### CC 特性对照表（更新后 11/11 = 100%）
| CC 特性 | CrabRes 实现 | 状态 |
|---------|-------------|------|
| Agent Loop | Growth Loop (ReAct) | ✅ |
| Multi-model routing | Tier 分级 + 降级链 | ✅ |
| Prompt Cache | PromptCache hash 去重 + 选择性注入 | ✅ UPGRADED |
| Tool retry + validation | 2x retry + 空结果检测 | ✅ |
| Write-Ahead Log | WAL + v2 检查点 | ✅ |
| Buddy System | Growth Mascot (10物种) | ✅ |
| Permission Levels | Trust Levels (5级) | ✅ |
| YOLO Classifier | Coordinator 自主决策 | ✅ |
| ULTRAPLAN | Deep Strategy Session | ✅ |
| Frustration Detection | Mood Sensing (5维) | ✅ |
| Coordinator Mode | Growth Roundtable (三阶段) | ✅ |
| **Sub-agent 隔离** | **Context Engine 选择性注入** | ✅ NEW |
| **多层记忆** | **Knowledge 层 + 版本管理 + 触发条件** | ✅ NEW |
| **Harness Engineering** | **产品→专家权重矩阵 + 依赖图分批执行** | ✅ NEW |

### Context Engineering 补齐（2026-04-03 晚）
- [x] **Prompt Cache**：`prompt_cache.py` — 对产品/策略等稳定内容做 hash 去重，同 session 不重复注入
- [x] **选择性知识注入**：`context_engine.py` — 根据任务检测渠道关键词，social_media 专家只注入相关渠道知识
  - 效果：Reddit 任务 8354 chars vs 全量 16265 chars → **节省 49% token**
- [x] **Sub-agent 上下文隔离**：`build_expert_context()` — 专家只看到相关工具结果 + 其他专家摘要（300字），不看完整对话历史/trust/mood
- [x] **多层记忆升级**：`GrowthMemory` 新增 `knowledge/` 分类、`save_knowledge()` + `get_triggered_knowledge()` 支持触发条件和过期时间
  - 版本追踪：每次 save 自动递增 `_version` + `_content_hash`（支持 Dream 去重）
  - 记忆统计：`get_memory_stats()` 输出文件数/大小
- [x] **Harness Engineering**：`context_engine.py`
  - 6 种产品类型（saas/ecommerce/community/content/tool/default）× 专家优先级矩阵
  - 专家发言依赖图：economist 依赖 market_researcher，copywriter 依赖 social_media+psychologist
  - `select_roundtable_experts()` 替代硬编码 4 人组
  - `get_expert_execution_order()` 分批执行：无依赖先行 → 有依赖后行 → 后批能看到前批结果
