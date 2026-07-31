import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ==========================================
# 1. 載入密碼與設定網頁標題
# ==========================================
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

st.set_page_config(page_title="高登 IT 達人", page_icon="🤖")
st.title("🤖 寸嘴 IT 達人 Web 2.0")
st.caption("由 LangChain + Streamlit 強勢驅動")

# ==========================================
# 2. 初始化大腦 (只做一次)
# ==========================================
# st.session_state 係網頁嘅「快取記憶」。
# 如果唔放喺 session_state，網頁每次 reload 都會重新召喚一次大腦，會好慢！
if "llm" not in st.session_state:
    st.session_state.llm = ChatOpenAI(
        model="inclusionai/ling-3.0-flash:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7
    )

# ==========================================
# 3. 初始化對話記憶 (Memory)
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content="你係一個好寸嘴，但係技術超勁嘅香港高登 IT 達人。請用廣東話回答。")
    ]

# ==========================================
# 4. 渲染過往嘅對話 (UI 顯示)
# ==========================================
# 將記憶入面嘅對話，逐句畫喺畫面上 (跳過 SystemMessage 唔顯示)
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# ==========================================
# 5. 接收用戶新輸入與執行大腦
# ==========================================
# st.chat_input 會喺網頁底整一個輸入框
user_input = st.chat_input("有咩技術難題，隨便問啦...")

if user_input:
    # 步驟 A：將用戶問題畫上畫面，並加入記憶體
    st.chat_message("user").write(user_input)
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    # 步驟 B：顯示 Loading 動畫，呼叫大腦
    with st.chat_message("assistant"):
        with st.spinner("達人思考緊點樣串你..."):
            # 將成串歷史紀錄質俾大腦
            response = st.session_state.llm.invoke(st.session_state.chat_history)
            st.write(response.content)

    # 步驟 C：將大腦嘅答案加入記憶體
    st.session_state.chat_history.append(AIMessage(content=response.content))
