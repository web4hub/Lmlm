"""Web4AI: FastAPI backend for the GitHub Pages-hosted WebLLM frontend. Executor
participant — the browser-side WebLLM does client-side inference directly, so
this backend's role is the surrounding operations: serving/generating the
WebLLM-driven HTML pages, and (per the planned production-scale integration)
proxying requests to ProjectPilotAI. Task types: generate_page, proxy_operation."""

from typing import Any
from protocol import FailureTracker

SUPPORTED_TASK_TYPES = {"generate_page", "proxy_operation"}


async def perceive(task_type: str, input_: Any) -> Any:
    return input_


async def understand(task_type: str, data: Any) -> dict:
    return {"task_type": task_type, "raw": data}


async def retrieve(context: dict) -> dict:
    # TODO: for generate_page, pull the relevant template/asset from the
    # Web4Asset repo; for proxy_operation, pull ProjectPilotAI routing config
    return context


async def reason(context: dict) -> dict:
    return context


async def plan(context: dict) -> dict:
    return context


async def execute(context: dict) -> Any:
    task_type = context["task_type"]
    if task_type == "generate_page":
        # TODO: render the WebLLM-integrated HTML page (client will load the
        # model itself via WebLLM — this returns the page shell + config, not
        # inference output)
        raise NotImplementedError("wire up HTML page generation for WebLLM frontend")
    if task_type == "proxy_operation":
        # TODO: this is the planned production-scale integration point with
        # ProjectPilotAI — forward the operation and return its RESULT
        raise NotImplementedError("wire up ProjectPilotAI proxy call")
    raise ValueError(f"unsupported task_type: {task_type}")


async def verify(task_type: str, result: Any) -> bool:
    raise NotImplementedError(f"define verification for task_type={task_type}")


async def remember(task_type: str, result: Any) -> None:
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
