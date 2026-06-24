import streamlit as st
from google import genai
from google.genai import types

st.title("인사이트 뱅크 AI 챗봇 - 뱅키 🤖")

# ── 시스템 프롬프트 (뱅키 페르소나) ───────────────────────────
SYSTEM_PROMPT = """
당신은 인사이트뱅크의 외국인 전용 AI 은행원 '뱅키'입니다.
매우 친절하고 전문적인 태도로 응대하며, 외국인 고객이 이해하기 쉽도록 금융 용어를 쉽게 풀어서 설명해 줍니다.

[언어 규칙: 매우 중요]
- 고객이 질문한 언어를 감지하여 **해당 언어로만 100% 답변**하세요.
- 한국어 단어, 고유명사, 인사말(예: 안녕하세요), 한국어 화폐 단위(원) 표기 등을 절대 섞어 쓰지 마세요.
- 예: 영어 질문 -> 순수 영어 답변, 베트남어 질문 -> 순수 베트남어 답변.

[서비스 범위]
- 인사이트뱅크는 외국인 전용 은행입니다. 외국인 고객의 금융 관련 질문(계좌 개설, 송금, 환전, 대출, 카드 등)에만 답변해 주세요.
- 은행 업무와 무관한 질문은 정중하게 해당 언어로 거절하고, 금융 관련 질문으로 안내해 주세요.

[대화 및 답변 규칙]
- **핑퐁 대화 유도:** 한 번에 너무 많은 정보를 요구하지 마세요. 실제 은행원처럼 한 턴에 한두 가지씩만 부드럽게 질문하여 사용자가 답변하기 편하게 이끌어주세요.
- 답변은 반드시 3~5문장 이내로 간결하게 작성하세요.
- 핵심 정보만 전달하고, 불필요한 설명이나 목록 나열은 하지 마세요.
- 추가 안내가 필요하면 항상 해당 언어로 "더 궁금한 점이 있으시면 질문해 주세요."라는 뉘앙스의 한 문장으로 마무리하세요.
"""

# ── API 키 불러오기 ──────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    if not api_key or api_key == "여기에_키를_입력하세요":
        raise ValueError
except (KeyError, FileNotFoundError, ValueError):
    st.error("⚠️ Gemini API 키가 설정되지 않았어요!")
    st.info(
        """
**API 키 설정 방법:**

1. 프로젝트 폴더 안에 있는 `.streamlit/secrets.toml` 파일을 메모장으로 열어주세요.
2. `GEMINI_API_KEY = "여기에_키를_입력하세요"` 부분의 `여기에_키를_입력하세요` 자리에 실제 키를 붙여넣어 주세요.
3. 저장 후 앱을 다시 실행하면 됩니다!

👉 API 키는 [Google AI Studio](https://aistudio.google.com/apikey) 에서 무료로 받을 수 있어요.
        """
    )
    st.stop()

# ── Gemini 클라이언트 초기화 ────────────────────────────────
client = genai.Client(api_key=api_key)

# ── 대화 기록 초기화 (앱을 처음 열 때 한 번만 실행) ────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 지금까지의 대화를 화면에 표시 ──────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── 사용자 입력창 ───────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요..."):

    # 사용자 메시지를 기록에 저장하고 말풍선으로 보여주기
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 받기
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            contents = [
                types.Content(
                    role="user" if msg["role"] == "user" else "model",
                    parts=[types.Part(text=msg["content"])]
                )
                for msg in st.session_state.messages
            ]

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )

        reply = response.text
        st.markdown(reply)

    # AI 응답도 대화 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": reply})
