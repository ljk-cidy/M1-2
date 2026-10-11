import os
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from app.config import db
from app.models import ChatRequest
from app.services.analyzer import calculate_summary

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("")
def chat_with_ai(req: ChatRequest):
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise HTTPException(status_code=500, detail="OpenAI API key missing")

    client = OpenAI(api_key=openai_key)

    # 1. 시계열 데이터 요약 생성
    docs = db.collection("data").stream()
    data_list = [doc.to_dict() for doc in docs]
    summary = calculate_summary(data_list)

    # 2. System Prompt 구성 (컨텍스트 주입)
    system_prompt = f"""당신은 사용자의 개인 시계열 데이터를 완벽히 이해하는 친절한 맞춤형 AI 비서입니다.

[사용자 데이터 요약]
- 분석 기간: {summary['period']}
- 총 데이터 수: {summary['count']}개
- 누적 총합: {summary['metrics']['total']}
- 평균값: {summary['metrics']['average']}
- 최고/최저: 최고 {summary['metrics']['max']} / 최저 {summary['metrics']['min']}
- 최근 추세: {summary['trend']}

위 요약 정보를 바탕으로 사용자의 질문에 사실적으로 정확하고 구체적인 답변을 제공하세요.
데이터에 없는 조언을 제시할 때는 추측임을 언급하세요."""

    messages = [{"role": "system", "content": system_prompt}]

    # 기존 대화 흐름 로드 (선택적)
    existing_messages = []
    if req.conversation_id:
        doc = db.collection("conversations").document(req.conversation_id).get()
        if doc.exists:
            existing_messages = doc.to_dict().get("messages", [])
            messages.extend(existing_messages)

    # 새로운 사용자 메시지 추가
    messages.append({"role": "user", "content": req.message})

    # 3. OpenAI GPT 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    ai_reply = response.choices[0].message.content

    # 4. 대화 내용 Firestore 저장 (자동 업데이트/신규 저장)
    updated_messages = existing_messages + [
        {"role": "user", "content": req.message},
        {"role": "assistant", "content": ai_reply}
    ]

    if req.conversation_id:
        conv_ref = db.collection("conversations").document(req.conversation_id)
        conv_ref.update({"messages": updated_messages})
        conv_id = req.conversation_id
    else:
        title = req.message[:20] + "..." if len(req.message) > 20 else req.message
        conv_ref = db.collection("conversations").document()
        conv_ref.set({"title": title, "messages": updated_messages})
        conv_id = conv_ref.id

    return {
        "reply": ai_reply,
        "conversation_id": conv_id,
        "summary_used": summary
    }