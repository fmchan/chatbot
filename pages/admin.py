import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os

st.set_page_config(page_title="管理員後台", page_icon="📊", layout="wide")
st.title("📊 系統對話紀錄 (Log)")

load_dotenv()
admin_password = os.getenv("ADMIN_PASSWORD") or st.secrets.get("ADMIN_PASSWORD")

# ==========================================
# 1. 管理員密碼閘口
# ==========================================
# 如果未驗證過，預設為 False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# 如果未登入，顯示輸入密碼畫面，並截停程式
if not st.session_state.admin_authenticated:
    st.info("🔒 呢度係機密重地，請輸入管理員密碼。")
    
    # type="password" 會令輸入嘅字變成黑點，防止俾人偷睇
    pwd_input = st.text_input("密碼：", type="password")
    
    if st.button("登入後台"):
        if pwd_input == admin_password:
            st.session_state.admin_authenticated = True
            st.rerun() # 密碼啱，重新整理，進入下面嘅畫面
        else:
            st.error("❌ 密碼錯誤！想白撞呀？")
            
    st.stop() # 🛑 截停程式，冇密碼絕對睇唔到下面嘅 Log

# ==========================================
# 2. 登出按鈕 (已登入先會見到)
# ==========================================
# 將登出掣放喺右上角
col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🚪 登出後台", use_container_width=True):
        st.session_state.admin_authenticated = False
        st.rerun()

st.divider() # 畫一條橫線分隔

# ==========================================
# 3. 顯示 Log 數據
# ==========================================
LOG_FILE = "chat_logs.csv"

if os.path.isfile(LOG_FILE):
    # 用 Pandas 讀取 CSV
    df = pd.read_csv(LOG_FILE)
    
    # 顯示數據總數
    st.metric(label="總對話次數", value=len(df))
    
    # 畫出靚靚表格
    st.dataframe(df, use_container_width=True)
    
    # 貼心功能：提供下載掣
    with open(LOG_FILE, "rb") as file:
        st.download_button(
            label="⬇️ 下載 CSV 檔案備份",
            data=file,
            file_name="backup_chat_logs.csv",
            mime="text/csv",
        )
else:
    st.info("暫時未有任何對話紀錄。如果有人問過問題，呢度就會出現數據！")