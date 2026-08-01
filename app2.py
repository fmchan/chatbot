import streamlit as st
import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ==========================================
# 0. 基本設定與讀取密碼
# ==========================================
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")
st.set_page_config(page_title="高登 IT 達人", page_icon="🤖", layout="wide")

LOG_FILE = "chat_logs.csv"

# ==========================================
# 🛠️ 工具函數 1：獲取用戶 IP
# ==========================================
def get_user_ip():
    try:
        # Streamlit 新版功能：從伺服器 Header 攞真實 IP
        headers = st.context.headers
        # 如果放咗上 Streamlit Cloud，真實 IP 會喺 X-Forwarded-For
        return headers.get("X-Forwarded-For", "Localhost (本機)")
    except Exception:
        return "Unknown IP"

# ==========================================
# 🛠️ 工具函數 2：寫入 CSV Log
# ==========================================
def write_log(name, ip, prompt):
    # 攞當下時間
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(LOG_FILE)
    
    # mode='a' 代表 Append (附加喺尾度，唔會洗走舊資料)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 如果個檔案係新開嘅，寫入第一行 Header
        if not file_exists:
            writer.writerow(["時間 (Time)", "名字 (Name)", "IP 地址", "用戶輸入 (Prompt)"])
        # 寫入真正嘅 Log 數據
        writer.writerow([timestamp, name, ip, prompt])

# ==========================================
# 🚪 第一關：登入閘口 (Ask for Name)
# ==========================================
# 如果 session_state 入面未有 user_name，就顯示登入畫面並「截停」程式
if "user_name" not in st.session_state:
    st.title("👋 歡迎來到寸嘴 IT 達人系統")
    st.info("入去被串之前，請先留低你個大名。")
    
    name_input = st.text_input("你叫咩名？")
    if st.button("進入系統"):
        if name_input.strip() == "":
            st.warning("喂！名都唔打想白撞呀？")
        else:
            st.session_state.user_name = name_input
            st.rerun() # 重新載入網頁，進入下一步
    
    st.stop() # 🛑 極度重要：截停程式，唔俾佢繼續行下面嘅 Chatbot Code

# ==========================================
# 📂 第二關：後台側邊欄 (俾你查閱 Log)
# ==========================================
with st.sidebar:
    st.header("🕵️‍♂️ 管理員後台")
    st.write(f"目前登入者：**{st.session_state.user_name}**")
    
    if st.button("📊 查看所有對話紀錄 (Log)"):
        if os.path.isfile(LOG_FILE):
            import pandas as pd
            # 用 Pandas 讀取 CSV，然後用 Streamlit 畫成靚靚表格
            df = pd.read_csv(LOG_FILE)
            st.dataframe(df)
        else:
            st.write("暫時未有任何人問過問題。")
    
    if st.button("登出"):
        del st.session_state.user_name
        st.rerun()

# ==========================================
# 🤖 第三關：主程式 (Chatbot 核心)
# ==========================================
st.title(f"🤖 寸嘴 IT 達人 (歡迎, {st.session_state.user_name})")

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

# 畫出過往對話
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# 接收用戶新輸入
user_input = st.chat_input("有咩技術難題，隨便問啦...")

if user_input:
    # 📝 核心動作：偷抄 Log！
    current_ip = get_user_ip()
    write_log(name=st.session_state.user_name, ip=current_ip, prompt=user_input)
    
    # 正常嘅 UI 顯示與記憶體更新
    st.chat_message("user").write(user_input)
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    with st.chat_message("assistant"):
        with st.spinner("達人思考緊點樣串你..."):
            response = st.session_state.llm.invoke(st.session_state.chat_history)
            st.write(response.content)

    st.session_state.chat_history.append(AIMessage(content=response.content))