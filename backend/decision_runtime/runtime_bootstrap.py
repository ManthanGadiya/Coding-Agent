import logging

from backend.decision_runtime.environment_mode import mode_controller, EnvironmentMode
from backend.decision_runtime.registries import agent_registry, skill_registry

logger = logging.getLogger(__name__)


async def init_runtime(mode: str = "build"):
    logger.info("Initializing decision runtime...")

    mode_controller.set_mode(EnvironmentMode(mode))

    logger.info("Decision runtime initialized (mode=%s, agents=%d, skills=%d)",
                mode, len(agent_registry.list()), len(skill_registry.list()))


async def shutdown_runtime():
    logger.info("Shutting down decision runtime...")
    logger.info("Decision runtime shutdown complete")
