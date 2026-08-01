import streamlit as st
import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ==========================================
# 0. 基本設定
# ==========================================
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")

# initial_sidebar_state="collapsed" 可以預設收起左邊個選單
st.set_page_config(page_title="IT 達人 @fmchan", page_icon="🤖", initial_sidebar_state="collapsed")

LOG_FILE = "chat_logs.csv"

def get_user_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "Localhost")
    except Exception:
        return "Unknown IP"

def write_log(name, ip, prompt):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["時間 (Time)", "名字 (Name)", "IP 地址", "用戶輸入 (Prompt)"])
        writer.writerow([timestamp, name, ip, prompt])

# ==========================================
# 1. 登入閘口
# ==========================================
if "user_name" not in st.session_state:
    st.title("👋 歡迎來到 IT 達人系統 @fmchan")
    name_input = st.text_input("你叫咩名？")
    if st.button("進入系統"):
        if name_input.strip() == "":
            st.warning("喂！名都唔打想白撞呀？")
        else:
            st.session_state.user_name = name_input
            st.rerun()
    st.stop()

# ==========================================
# 2. 頂部導航列 (登出按鈕)
# ==========================================
# 用 st.columns 將標題放左邊，登出掣放右邊
col1, col2 = st.columns([8, 2])
with col1:
    st.title(f"🤖 寸嘴 IT 達人 (歡迎, {st.session_state.user_name})")
with col2:
    if st.button("🚪 登出", use_container_width=True):
        del st.session_state.user_name
        st.rerun()

# ==========================================
# 3. 核心 Chatbot 邏輯
# ==========================================
if "llm" not in st.session_state:
    st.session_state.llm = ChatOpenAI(
        model="inclusionai/ling-3.0-flash:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content=f"你係一個好寸嘴嘅高登 IT 達人。而家同你講緊嘢嘅人叫做 {st.session_state.user_name}，請用廣東話回答佢。")
    ]

for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

user_input = st.chat_input("有咩技術難題，隨便問啦...")

if user_input:
    # 寫 Log
    write_log(name=st.session_state.user_name, ip=get_user_ip(), prompt=user_input)
    
    st.chat_message("user").write(user_input)
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    with st.chat_message("assistant"):
        with st.spinner("達人思考緊點樣串你..."):
            response = st.session_state.llm.invoke(st.session_state.chat_history)
            st.write(response.content)

    st.session_state.chat_history.append(AIMessage(content=response.content))