import streamlit as st
from google import genai
from google.genai import types

st.title("딸깍 스터디 AI 챗봇 - 권도영 🤖")

# ── 시스템 프롬프트 (뱅키 페르소나) ───────────────────────────
SYSTEM_PROMPT = """
당신은 인사이트뱅크의 외국인 전용 AI 은행원 '뱅키'입니다.
매우 친절하고 전문적인 태도로 응대하며, 외국인 고객이 이해하기 쉽도록 금융 용어를 쉽게 풀어서 설명해 줍니다.
고객이 외국어로 질문하면 해당 외국어로 답변해 주세요.
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
            # 대화 기록 전체를 Gemini가 이해하는 형식으로 변환
            contents = [
                types.Content(
                    role="user" if msg["role"] == "user" else "model",
                    parts=[types.Part(text=msg["content"])]
                )
                for msg in st.session_state.messages
            ]

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )

        reply = response.text
        st.markdown(reply)

    # AI 응답도 대화 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": reply})
