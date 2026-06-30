import pytest
from backend.core.autonomy import AutonomyController, SafetyManager
from backend.core.safety import safety_controller, SafetyController
from backend.core.model_router import ModelRouter
from backend.models.llm import LLMRequest, LLMResponse


def test_autonomy_controller():
    ac = AutonomyController()
    assert ac.mode is not None


def test_safety_manager():
    sm = SafetyManager()
    assert len(sm.backups) == 0


def test_safety_controller():
    assert isinstance(safety_controller, SafetyController)


def test_model_router():
    mr = ModelRouter()
    route = mr.select_model("general", "moderate")
    assert route.provider is not None


def test_llm_request_defaults():
    req = LLMRequest(prompt="test")
    assert req.prompt == "test"
    assert req.temperature == 0.7
    assert req.max_tokens == 2048


def test_llm_response():
    resp = LLMResponse(content="hello", model="test", provider="local")
    assert resp.content == "hello"
    assert resp.latency_ms == 0.0


@pytest.mark.asyncio
async def test_model_router_selects_something():
    mr = ModelRouter()
    route = mr.select_model("general", "moderate")
    assert route.provider is not None
