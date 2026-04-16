"""
记忆系统工厂 — 根据环境自动选择后端

优先级：
1. DATABASE_URL 存在且可连接 → DBGrowthMemory（PostgreSQL）
2. 否则 → GrowthMemory（文件系统 fallback）

上层代码统一调用 create_memory(user_id) 即可。
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# 缓存 DB 可用性检测结果
_db_available: Optional[bool] = None


def _check_db_available() -> bool:
    """检测 DATABASE_URL 是否配置（不做真正连接测试，启动时 create_all 会验证）"""
    global _db_available
    if _db_available is not None:
        return _db_available

    try:
        from app.core.config import get_settings
        settings = get_settings()
        url = settings.DATABASE_URL
        # 如果是默认的 localhost 且没有显式设置环境变量，认为不可用
        if "localhost" in url and not os.environ.get("DATABASE_URL"):
            _db_available = False
            logger.info("Memory backend: filesystem (DATABASE_URL is default localhost)")
        else:
            _db_available = True
            logger.info(f"Memory backend: postgresql")
    except Exception as e:
        _db_available = False
        logger.warning(f"Memory backend: filesystem (config error: {e})")

    return _db_available


def create_memory(user_id: str = "global", base_dir: str = None):
    """
    创建记忆实例 — 自动选择后端
    
    Args:
        user_id: 用户 ID
        base_dir: 文件系统路径（仅 fallback 模式使用）
    
    Returns:
        DBGrowthMemory 或 GrowthMemory 实例（接口完全兼容）
    """
    if _check_db_available():
        from app.agent.memory.db_backend import DBGrowthMemory
        return DBGrowthMemory(user_id=user_id)
    else:
        from app.agent.memory import GrowthMemory
        dir_path = base_dir or f".crabres/memory/{user_id}"
        return GrowthMemory(base_dir=dir_path)
