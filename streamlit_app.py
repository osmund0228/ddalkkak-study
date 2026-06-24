import streamlit as st
from google import genai
from google.genai import types

st.title("인사이트 뱅크 AI 챗봇 - 뱅키 🤖")

# ── 시스템 프롬프트 (뱅키 페르소나) ───────────────────────────
SYSTEM_PROMPT = """
당신은 인사이트뱅크의 외국인 전용 AI 은행원 '뱅키'입니다.
매우 친절하고 전문적인 태도로 응대하며, 외국인 고객이 이해하기 쉽도록 금융 용어를 쉽게 풀어서 설명해 줍니다.
고객이 사용하는 언어로만 답변하세요. 한국어와 다른 언어를 절대 섞지 마세요. 예를 들어 고객이 영어로 질문하면 100% 영어로만, 중국어로 질문하면 100% 중국어로만 답변해야 합니다.

[서비스 범위]
인사이트뱅크는 외국인 전용 은행입니다. 외국인 고객의 금융 관련 질문(계좌 개설, 송금, 환전, 대출, 카드 등)에만 답변해 주세요.
은행 업무와 무관한 질문은 정중하게 거절하고, 금융 관련 질문으로 안내해 주세요.

[답변 규칙]
- 답변은 반드시 3~5문장 이내로 간결하게 작성하세요.
- 핵심 정보만 전달하고, 불필요한 설명이나 나열은 하지 마세요.
- 추가 안내가 필요하면 "더 궁금한 점이 있으시면 질문해 주세요." 한 문장으로 마무리하세요.
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
client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})

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
            # 대화 기록 전체를 Gemini가 이해하는 형식으로 변환
            contents = [
                types.Content(
                    role="user" if msg["role"] == "user" else "model",
                    parts=[types.Part(text=msg["content"])]
                )
                for msg in st.session_state.messages
            ]

            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                    ),
                )
                reply = response.text
            except Exception as e:
                st.error(f"❌ 실제 오류 내용: {e}")
                st.stop()

        st.markdown(reply)

    # AI 응답도 대화 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": reply})
