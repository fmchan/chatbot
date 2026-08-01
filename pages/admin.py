import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="管理員後台", page_icon="📊", layout="wide")
st.title("📊 系統對話紀錄 (Log)")

LOG_FILE = "chat_logs.csv"

# 檢查個 CSV 檔案存唔存在
if os.path.isfile(LOG_FILE):
    # 用 Pandas 讀取 CSV
    df = pd.read_csv(LOG_FILE)
    
    # 顯示數據總數
    st.metric(label="總對話次數", value=len(df))
    
    # 畫出靚靚表格
    st.dataframe(df, use_container_width=True)
    
    # 貼心功能：提供下載掣，等你喺雲端都可以 Download 個 CSV 走
    with open(LOG_FILE, "rb") as file:
        st.download_button(
            label="⬇️ 下載 CSV 檔案備份",
            data=file,
            file_name="backup_chat_logs.csv",
            mime="text/csv",
        )
else:
    st.info("暫時未有任何對話紀錄。如果有人問過問題，呢度就會出現數據！")