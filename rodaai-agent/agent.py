"""RODA-AI (Republic of Data Analytics & AI): open-source AI/data-science/analytics
platform. Coordinator participant — registers other participants (including Lola),
ROUTEs tasks to the right one, and reconciles state via SYNC. Task-type-specific
analytics logic lives in `execute`, but this participant's real job is routing."""

from typing import Any, Optional
from protocol import FailureTracker

# TODO: back this with real service discovery/config rather than an in-memory dict
REGISTRY: dict[str, dict] = {
    # "lola": {"url": "http://localhost:8001/message", "accepts": {"chat", "voice_transcribe", ...}},
}


def register_participant(participant_id: str, url: str, accepts: set[str]) -> None:
    REGISTRY[participant_id] = {"url": url, "accepts": accepts}


def route(task_type: str) -> Optional[str]:
    """Pick which registered participant should handle this task_type.
    TODO: replace first-match with real policy (load, capability score, etc.)."""
    for participant_id, info in REGISTRY.items():
        if task_type in info["accepts"]:
            return participant_id
    return None


async def perceive(task_type: str, input_: Any) -> Any:
    return input_


async def understand(task_type: str, data: Any) -> dict:
    return {"task_type": task_type, "raw": data}


async def retrieve(context: dict) -> dict:
    # TODO: pull cross-participant state relevant to this task (analytics history,
    # prior dataset context) before routing
    return context


async def reason(context: dict) -> dict:
    return context


async def plan(context: dict) -> dict:
    target = route(context["task_type"])
    if target is None:
        raise ValueError(f"no registered participant accepts task_type: {context['task_type']}")
    context["_route_target"] = target
    return context


async def execute(context: dict) -> Any:
    target = context["_route_target"]
    # TODO: actually POST a TASK envelope to REGISTRY[target]["url"] and await RESULT
    # (this is the ROUTE + INSTRUCT operations in practice). Local analytics task
    # types that RODA-AI itself owns (not delegated) also get handled here.
    raise NotImplementedError(f"wire up dispatch to participant '{target}' or local analytics logic")


async def verify(task_type: str, result: Any) -> bool:
    raise NotImplementedError(f"define verification for task_type={task_type}")


async def remember(task_type: str, result: Any) -> None:
    # TODO: SYNC state back to any participant that needs to know this task completed
    pass


async def handle_task(task_type: str, input_: Any) -> Any:
    tracker = FailureTracker()
    perceived = await perceive(task_type, input_)
    context = await understand(task_type, perceived)
    context = await retrieve(context)
    context = await reason(context)
    context = await plan(context)
    while True:
        try:
            out = await execute(context)
            tracker.reset()
            await remember(task_type, out)
            return out
        except NotImplementedError:
            raise
        except Exception:
            if tracker.record_failure():
                raise
