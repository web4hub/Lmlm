"""Lola: personalized AI companion (Samantha AI-based). Executor participant —
receives TASK, runs it through the LMLM pipeline, returns RESULT. Task types:
chat, voice_transcribe, journal_entry, emotion_track. Backs the shared Python
backend for the planned React Native/Expo + Next.js clients."""

from typing import Any
from protocol import FailureTracker

SUPPORTED_TASK_TYPES = {"chat", "voice_transcribe", "journal_entry", "emotion_track"}


async def perceive(task_type: str, input_: Any) -> Any:
    # TODO: for voice_transcribe, this is where raw audio bytes/stream enter
    return input_


async def understand(task_type: str, data: Any) -> dict:
    # TODO: intent + emotional-tone extraction — feeds emotion_track and shapes
    # how `execute` responds (supportive presence vs. creative muse vs. assistant)
    return {"task_type": task_type, "raw": data, "intent": None, "emotional_tone": None}


async def retrieve(understood: dict) -> dict:
    # TODO: pull relevant journal history / prior emotional-tracking state so
    # responses stay consistent with what Lola already knows about the user
    understood["memory"] = []
    return understood


async def reason(context: dict) -> dict:
    return context


async def plan(context: dict) -> dict:
    return context


async def execute(context: dict) -> Any:
    task_type = context["task_type"]
    if task_type not in SUPPORTED_TASK_TYPES:
        raise ValueError(f"unsupported task_type: {task_type}")
    if task_type == "chat":
        raise NotImplementedError("wire up the companion response model here")
    if task_type == "voice_transcribe":
        raise NotImplementedError("wire up speech-to-text here")
    if task_type == "journal_entry":
        raise NotImplementedError("wire up journal storage/retrieval here")
    if task_type == "emotion_track":
        raise NotImplementedError("wire up emotional-state logging here")


async def verify(task_type: str, result: Any) -> bool:
    # TODO: for chat/voice, this is the safety/appropriateness check before a
    # response reaches the user — do not stub this out with `return True`
    raise NotImplementedError(f"define verification for task_type={task_type}")


async def remember(task_type: str, result: Any) -> None:
    # TODO: journal_entry and emotion_track results persist here; chat results
    # may also need to update conversational memory
    pass


async def handle_task(task_type: str, input_: Any) -> Any:
    """Wires perceive→...→execute with halt-after-two-failures."""
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
            raise  # not a runtime failure — surface immediately, don't count against the tracker
        except Exception:
            if tracker.record_failure():
                raise  # caller emits BLOCKED, does not retry further
