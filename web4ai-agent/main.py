"""Web4AI Script.god participant — HTTP+JSON transport, executor role only."""

from fastapi import FastAPI, HTTPException
from protocol import Envelope, MessageType
from agent import handle_task, verify, SUPPORTED_TASK_TYPES

PARTICIPANT_ID = "web4ai"
app = FastAPI(title="Web4AI Script.god participant")


@app.post("/message")
async def receive(envelope: Envelope):
    if envelope.type == MessageType.CONNECT:
        return {"type": "ACK", "payload": {"accepted": True, "participant_id": PARTICIPANT_ID}}

    if envelope.type == MessageType.CAPABILITIES:
        return {
            "type": "CAPABILITIES",
            "payload": {
                "operations": ["INSTRUCT", "VERIFY", "RESULT"],
                "pipeline_stages": ["perceive", "understand", "retrieve", "execute", "verify"],
                "accepts_task_types": sorted(SUPPORTED_TASK_TYPES),
            },
        }

    if envelope.type == MessageType.TASK:
        task_type = envelope.payload.get("task_type")
        if task_type not in SUPPORTED_TASK_TYPES:
            return {"type": "ERROR", "payload": {"stage": "dispatch", "message": f"unsupported task_type: {task_type}", "recoverable": False}}
        try:
            result = await handle_task(task_type, envelope.payload.get("input"))
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))
        except Exception as e:
            return {"type": "BLOCKED", "payload": {"reason": str(e), "consecutive_failures": 2, "last_error": str(e)}}
        ok = await verify(task_type, result)
        return {"type": "RESULT", "payload": {"output": result, "verified": ok}}

    if envelope.type == MessageType.CANCEL:
        return {"type": "ACK", "payload": {"accepted": True}}

    return {"type": "ERROR", "payload": {"stage": "dispatch", "message": f"unhandled message type: {envelope.type}", "recoverable": False}}
