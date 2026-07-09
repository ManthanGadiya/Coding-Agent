import logging

from backend.decision_runtime.environment_mode import mode_controller, EnvironmentMode
from backend.decision_runtime.registries import agent_registry, skill_registry

logger = logging.getLogger(__name__)


async def init_runtime(mode: str = "build"):
    logger.info("Initializing decision runtime...")

    mode_controller.set_mode(EnvironmentMode(mode))

    agents = agent_registry.list()
    skills = skill_registry.list()

    # ponytail: bridge runtime SkillDef registry -> backend.skills BaseSkill instances
    try:
        import backend.skills as runtime_skills
        registered_names = {s.name for s in skills}
        for runtime_skill in runtime_skills.list_skills():
            if runtime_skill["name"] not in registered_names:
                logger.debug("Runtime skill %s not in decision registry (OK)", runtime_skill["name"])
    except Exception:
        logger.debug("backend.skills unavailable (OK)")

    logger.info("Decision runtime initialized (mode=%s, agents=%d, skills=%d)",
                mode, len(agents), len(skills))
    logger.debug("Registered agents: %s", [a.agent_type for a in agents])
    logger.debug("Registered skills: %s", [s.name for s in skills])


async def shutdown_runtime():
    logger.info("Shutting down decision runtime...")
    logger.info("Decision runtime shutdown complete")
