import json
import time
import uuid

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()


# 대화 메시지 한 개의 형식
class Message(BaseModel):
    role: str
    content: str


# WebUI에서 보낼 요청의 형식
class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


# WebUI의 모델 선택 목록에 표시할 정보
@app.get("/v1/models")
def models():
    return {
        "object": "list",
        "data": [{
            "id": "practice-model",
            "object": "model",
            "created": 0,
            "owned_by": "docker-lab"
        }]
    }


# 대화 요청 처리
@app.post("/v1/chat/completions")
def chat(request: ChatRequest):
    question = next(
        (m.content for m in reversed(request.messages) if m.role == "user"),
        ""
    )
    answer = f"받은 질문: {question}\n\nFastAPI에서 만든 연습용 응답입니다."
    response_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    # WebUI가 스트리밍 응답을 요청한 경우
    if request.stream:
        def events():
            for delta, finish_reason in [
                ({"role": "assistant", "content": answer}, None),
                ({}, "stop"),
            ]:
                chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": delta,
                        "finish_reason": finish_reason
                    }]
                }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    # 일반 JSON 응답
    return {
        "id": response_id,
        "object": "chat.completion",
        "created": created,
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": answer
            },
            "finish_reason": "stop"
        }]
    }
