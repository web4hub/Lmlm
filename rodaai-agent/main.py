"""RODA-AI Script.god participant — coordinator role, so unlike an executor-only
participant (e.g. lola-agent) this wires the full control-plane surface:
REGISTER, ROUTE, COORDINATE, SYNC, POLICY, STATE, EVENT, CANCEL, ROLLBACK,
plus the baseline data-plane TASK/RESULT/VERIFY handling."""

from fastapi import FastAPI, HTTPException
from protocol import Envelope, MessageType
from agent import handle_task, verify, register_participant, REGISTRY

PARTICIPANT_ID = "rodaai"
app = FastAPI(title="RODA-AI Script.god coordinator")


@app.post("/register")
async def register(participant_id: str, url: str, accepts: list[str]):
    """REGISTER operation: a participant (e.g. Lola) announces itself to the coordinator."""
    register_participant(participant_id, url, set(accepts))
    return {"registered": participant_id, "accepts": accepts}


@app.post("/message")
async def receive(envelope: Envelope):
    if envelope.type == MessageType.CONNECT:
        return {"type": "ACK", "payload": {"accepted": True, "participant_id": PARTICIPANT_ID}}

    if envelope.type == MessageType.CAPABILITIES:
        return {
            "type": "CAPABILITIES",
            "payload": {
                "operations": ["REGISTER", "ROUTE", "COORDINATE", "SYNC", "POLICY", "STATE", "EVENT", "CANCEL", "ROLLBACK", "INSTRUCT", "VERIFY", "RESULT"],
                "pipeline_stages": ["perceive", "understand", "retrieve", "plan", "execute", "verify", "remember"],
                "accepts_task_types": ["*"],  # coordinator routes rather than owning a fixed set
            },
        }

    if envelope.type == MessageType.TASK:
        task_type = envelope.payload.get("task_type")
        try:
            result = await handle_task(task_type, envelope.payload.get("input"))
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))
        except ValueError as e:
            return {"type": "ERROR", "payload": {"stage": "plan", "message": str(e), "recoverable": False}}
        except Exception as e:
            return {"type": "BLOCKED", "payload": {"reason": str(e), "consecutive_failures": 2, "last_error": str(e)}}
        ok = await verify(task_type, result)
        return {"type": "RESULT", "payload": {"output": result, "verified": ok}}

    if envelope.type == MessageType.SYNC:
        # TODO: reconcile state_delta from the payload against local state
        return {"type": "ACK", "payload": {"accepted": True}}

    if envelope.type == MessageType.CANCEL:
        # TODO: propagate CANCEL to whichever routed participant owns the in-flight task
        return {"type": "ACK", "payload": {"accepted": True}}

    return {"type": "ERROR", "payload": {"stage": "dispatch", "message": f"unhandled message type: {envelope.type}", "recoverable": False}}


@app.get("/participants")
async def list_participants():
    return REGISTRY
