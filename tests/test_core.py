"""
CrabRes 核心路径测试

覆盖：
- Agent Loop 状态机
- 专家系统调度
- 工具执行和错误处理
- Growth Log 判断逻辑
- Playbook 数据模型
- ExperimentTracker CRUD
- 上下文构建
"""

import asyncio
import json
import tempfile
import os
import pytest
from pathlib import Path


# ===== Growth Log 测试 =====

class TestGrowthLog:
    """增长日志系统测试"""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        from app.agent.memory.growth_log import GrowthLog
        self.gl = GrowthLog(base_dir=self.tmpdir)

    def test_judge_result_reddit_great(self):
        from app.agent.memory.growth_log import judge_result
        r = judge_result("reddit", "post", {"upvotes": 150, "comments": 12})
        assert r["verdict"] in ("good", "great")
        assert r["score"] > 60

    def test_judge_result_reddit_poor(self):
        from app.agent.memory.growth_log import judge_result
        r = judge_result("reddit", "post", {"upvotes": 2, "comments": 0})
        assert r["verdict"] == "poor"
        assert r["score"] < 30

    def test_judge_result_x_great(self):
        from app.agent.memory.growth_log import judge_result
        r = judge_result("x", "post", {"likes": 200, "impressions": 10000})
        assert r["verdict"] == "great"
        assert r["score"] >= 80

    def test_judge_result_xiaohongshu(self):
        from app.agent.memory.growth_log import judge_result
        r = judge_result("xiaohongshu", "post", {"likes": 800, "collects": 300, "comments": 50})
        assert r["verdict"] in ("good", "great")

    def test_judge_result_unknown_platform(self):
        from app.agent.memory.growth_log import judge_result
        r = judge_result("unknown", "post", {"engagement": 150})
        assert r["verdict"] in ("good", "great")
        assert r["score"] > 50

    def test_log_action(self):
        async def run():
            entry = await self.gl.log_action("reddit", "post", "Posted in r/SaaS")
            assert entry.id.startswith("act-")
            assert entry.platform == "reddit"
            actions = await self.gl.get_today_actions()
            assert len(actions) == 1
        asyncio.run(run())

    def test_log_result_auto_judge(self):
        async def run():
            action = await self.gl.log_action("reddit", "post", "Test post")
            result = await self.gl.log_result(action.id, {"upvotes": 50, "comments": 8})
            assert result.verdict in ("good", "great")
            assert result.score > 0
        asyncio.run(run())

    def test_compute_state_empty(self):
        async def run():
            state = await self.gl.compute_state()
            assert state.total_actions == 0
            assert state.avg_score == 0
        asyncio.run(run())

    def test_compute_state_with_data(self):
        async def run():
            a1 = await self.gl.log_action("reddit", "post", "Post 1")
            a2 = await self.gl.log_action("x", "post", "Post 2")
            await self.gl.log_result(a1.id, {"upvotes": 100})
            await self.gl.log_result(a2.id, {"likes": 50})
            state = await self.gl.compute_state()
            assert state.total_actions == 2
            assert state.total_results == 2
            assert len(state.channel_weights) >= 1
        asyncio.run(run())

    def test_generate_strategy(self):
        async def run():
            entry = await self.gl.log_strategy(
                actions=["Post on Reddit", "DM 5 users"],
                reasoning="Based on channel weights"
            )
            assert entry.id.startswith("str-")
            latest = await self.gl.get_latest_strategy()
            assert latest is not None
            assert len(latest["actions"]) == 2
        asyncio.run(run())


# ===== ExperimentTracker 测试 =====

class TestExperimentTracker:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        from app.agent.memory.experiments import ExperimentTracker
        self.tracker = ExperimentTracker(base_dir=self.tmpdir)

    def test_create_experiment(self):
        async def run():
            exp = await self.tracker.create_experiment("Get 50 signups", "Reddit > X")
            assert exp.id.startswith("exp-")
            exps = await self.tracker.get_experiments()
            assert len(exps) == 1
        asyncio.run(run())

    def test_record_action(self):
        async def run():
            action = await self.tracker.record_action(
                platform="reddit", action_type="post",
                url="https://reddit.com/r/test/123", content_preview="Test"
            )
            assert action.id.startswith("act-")
            assert action.status == "posted"
            trackable = await self.tracker.get_trackable_actions()
            assert len(trackable) == 1
        asyncio.run(run())

    def test_record_result(self):
        async def run():
            action = await self.tracker.record_action("x", "post", url="https://x.com/123")
            await self.tracker.record_result(action.id, {"likes": 42})
            results = await self.tracker.get_results(action.id)
            assert len(results) == 1
            assert results[0]["metrics"]["likes"] == 42
        asyncio.run(run())

    def test_learnings(self):
        async def run():
            exp = await self.tracker.create_experiment("Test exp")
            await self.tracker.complete_experiment(exp.id, "Reddit works", ["数字标题 3x better"])
            learnings = await self.tracker.get_learnings()
            assert len(learnings) == 1
            text = await self.tracker.get_learnings_text()
            assert "GROWTH PATTERNS" in text
        asyncio.run(run())

    def test_summary(self):
        async def run():
            await self.tracker.record_action("reddit", "post")
            await self.tracker.record_action("x", "post")
            summary = await self.tracker.get_summary()
            assert summary["total_actions"] == 2
        asyncio.run(run())


# ===== Playbook 测试 =====

class TestPlaybook:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        from app.agent.memory.playbooks import PlaybookStore, Playbook, PlaybookPhase, PlaybookStep
        self.store = PlaybookStore(base_dir=self.tmpdir)
        self.Playbook = Playbook
        self.Phase = PlaybookPhase
        self.Step = PlaybookStep

    def test_save_and_load(self):
        async def run():
            pb = self.Playbook(
                name="Test Playbook",
                phases=[self.Phase(name="Phase 1", steps=[
                    self.Step(order=1, title="Step 1", detail="Do something"),
                    self.Step(order=2, title="Step 2", detail="Do more"),
                ])]
            )
            pb_id = await self.store.save_playbook(pb)
            loaded = await self.store.get_playbook(pb_id)
            assert loaded is not None
            assert loaded["name"] == "Test Playbook"
            assert len(loaded["phases"]) == 1
            assert len(loaded["phases"][0]["steps"]) == 2
        asyncio.run(run())

    def test_activate(self):
        async def run():
            pb = self.Playbook(name="Test")
            await self.store.save_playbook(pb)
            await self.store.activate_playbook(pb.id)
            active = await self.store.get_playbooks(status="active")
            assert len(active) == 1
        asyncio.run(run())

    def test_update_step(self):
        async def run():
            pb = self.Playbook(
                name="Test",
                phases=[self.Phase(name="P1", steps=[
                    self.Step(order=1, title="S1"),
                ])]
            )
            await self.store.save_playbook(pb)
            await self.store.update_step_status(pb.id, 0, 0, "done", "Completed!")
            loaded = await self.store.get_playbook(pb.id)
            assert loaded["phases"][0]["steps"][0]["status"] == "done"
        asyncio.run(run())


# ===== 知识系统测试 =====

class TestKnowledge:
    def test_all_experts_have_knowledge(self):
        from app.agent.knowledge.skills_registry import EXPERT_KNOWLEDGE, get_expert_knowledge
        assert len(EXPERT_KNOWLEDGE) == 13
        for eid in EXPERT_KNOWLEDGE:
            k = get_expert_knowledge(eid)
            assert len(k) > 100, f"Expert {eid} has too little knowledge: {len(k)} chars"

    def test_social_media_has_three_channels(self):
        from app.agent.knowledge.skills_registry import EXPERT_KNOWLEDGE
        sm = EXPERT_KNOWLEDGE.get("social_media", [])
        names = [item["name"] for item in sm]
        assert "x_twitter_deep_knowledge" in names
        assert "xiaohongshu_deep_knowledge" in names
        assert "reddit_deep_knowledge" in names

    def test_playbook_templates(self):
        from app.agent.knowledge.playbook_templates import ALL_PLAYBOOK_TEMPLATES, get_playbook_templates_prompt
        assert len(ALL_PLAYBOOK_TEMPLATES) == 3
        prompt = get_playbook_templates_prompt()
        assert "PLAYBOOK TEMPLATES" in prompt


# ===== Agent Loop 基础测试 =====

class TestAgentLoop:
    def test_action_types(self):
        from app.agent.engine.loop import ActionType
        assert hasattr(ActionType, 'THINK')
        assert hasattr(ActionType, 'ROUNDTABLE')
        assert hasattr(ActionType, 'TOOL_CALL')
        assert hasattr(ActionType, 'EXPERT')
        assert hasattr(ActionType, 'OUTPUT')
        assert hasattr(ActionType, 'ASK_USER')

    def test_agent_action_creation(self):
        from app.agent.engine.loop import AgentAction, ActionType
        a = AgentAction(type=ActionType.ROUNDTABLE, content="test", expert_ids=["a", "b"])
        assert a.expert_ids == ["a", "b"]
        assert a.type == ActionType.ROUNDTABLE

    def test_loop_phase_enum(self):
        from app.agent.engine.loop import LoopPhase
        phases = [p.value for p in LoopPhase]
        assert "intake" in phases
        assert "research" in phases
        assert "strategy" in phases

    def test_available_actions_include_roundtable(self):
        from app.agent.engine.loop import AgentLoop
        loop = AgentLoop.__new__(AgentLoop)
        loop.state = type('S', (), {
            'phase': type('P', (), {'value': 'intake'})(),
            'expert_outputs': {}, 'turn_count': 1
        })()
        loop.memory = type('M', (), {'base_dir': '/tmp'})()
        actions = loop._get_available_actions()
        names = [a['name'] for a in actions]
        assert 'consult_roundtable' in names
        assert 'web_search' in names
        assert 'output' in names


# ===== 专家系统测试 =====

class TestExperts:
    def test_expert_pool_register(self):
        from app.agent.experts import ExpertPool
        from app.agent.experts.market_researcher import MarketResearcher
        pool = ExpertPool()
        pool.register(MarketResearcher())
        assert pool.get("market_researcher") is not None
        assert pool.get("nonexistent") is None

    def test_all_experts_loadable(self):
        from app.agent.experts.market_researcher import MarketResearcher
        from app.agent.experts.economist import Economist
        from app.agent.experts.content_strategist import ContentStrategist
        from app.agent.experts.social_media import SocialMediaExpert
        from app.agent.experts.paid_ads import PaidAdsExpert
        from app.agent.experts.partnerships import PartnershipsExpert
        from app.agent.experts.ai_distribution import AIDistributionExpert
        from app.agent.experts.psychologist import ConsumerPsychologist
        from app.agent.experts.product_growth import ProductGrowthExpert
        from app.agent.experts.data_analyst import DataAnalyst
        from app.agent.experts.copywriter import MasterCopywriter
        from app.agent.experts.critic import StrategyCritic
        from app.agent.experts.designer import DesignExpert
        experts = [MarketResearcher(), Economist(), ContentStrategist(),
                   SocialMediaExpert(), PaidAdsExpert(), PartnershipsExpert(),
                   AIDistributionExpert(), ConsumerPsychologist(), ProductGrowthExpert(),
                   DataAnalyst(), MasterCopywriter(), StrategyCritic(), DesignExpert()]
        assert len(experts) == 13
        for e in experts:
            assert len(e.system_prompt) > 50

    def test_expert_has_quality_rules(self):
        """BaseExpert.analyze() 应该注入输出质量规则"""
        import inspect
        from app.agent.experts import BaseExpert
        src = inspect.getsource(BaseExpert.analyze)
        assert "NO CONSULTANT SPEAK" in src
        assert "CONTRARIAN TAKE" in src


# ===== 工具系统测试 =====

class TestTools:
    def test_tool_registry(self):
        from app.agent.tools import ToolRegistry
        from app.agent.tools.research import WebSearchTool
        reg = ToolRegistry()
        reg.register(WebSearchTool())
        assert reg.get("web_search") is not None
        assert reg.get("nonexistent") is None

    def test_all_tools_loadable(self):
        from app.agent.tools.research import WebSearchTool, ScrapeWebsiteTool, SocialSearchTool, CompetitorAnalyzeTool, DeepScrapeTool
        from app.agent.tools.actions import WritePostTool, WriteEmailTool, SubmitToDirectoryTool, SetActiveCampaignTool
        tools = [WebSearchTool(), ScrapeWebsiteTool(), SocialSearchTool(),
                 CompetitorAnalyzeTool(), DeepScrapeTool(),
                 WritePostTool(), WriteEmailTool(), SubmitToDirectoryTool(), SetActiveCampaignTool()]
        assert len(tools) == 9
        for t in tools:
            assert t.definition.name
            assert t.definition.description


# ===== DB 模型测试 =====

class TestModels:
    def test_growth_models_import(self):
        from app.models.growth import (
            GrowthAction, GrowthResult, GrowthExperiment,
            GrowthLearning, GrowthStrategy, ChannelWeight,
            PlaybookRecord, AgentSession,
        )
        assert GrowthAction.__tablename__ == "growth_actions"
        assert GrowthResult.__tablename__ == "growth_results"
        assert AgentSession.__tablename__ == "agent_sessions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
