import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Aurora Proposal Data Extractor", layout="wide")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()

st.title("☀️ Aurora Proposal Data Extractor")

link = st.text_input("Paste Aurora Proposal Link:")

if st.button("Process Link", type="primary"):
    try:
        with st.spinner("Processing proposal..."):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Client Name': soup.find(class_='customer-name').text.strip() if soup.find(class_='customer-name') else "Not found",
                'System Size': "TBD",
                'Price per Watt': "TBD",
                'Total Cost': "TBD",
                'Link': link
            }
            
            new_df = pd.DataFrame([data])
            if st.session_state.data.empty:
                st.session_state.data = new_df
            else:
                st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)
            
        st.success("✅ Data extracted successfully!")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

if not st.session_state.data.empty:
    st.subheader("Extracted Data")
    st.dataframe(st.session_state.data)
    
    csv = st.session_state.data.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="aurora_data.csv",
        mime="text/csv"
    )
