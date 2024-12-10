import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import base64
from io import BytesIO
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

class AuroraScraper:
    def extract_data(self, link):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {
                'Date Extracted': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Client Name': self._extract_client_name(soup),
                'System Size (kW)': self._extract_system_size(soup),
                'Price per Watt ($)': self._extract_price_per_watt(soup),
                'Efficiency (%)': self._extract_efficiency(soup),
                'Bill Offset (%)': self._extract_bill_offset(soup),
                'Total Cost ($)': self._extract_total_cost(soup),
                'Before Monthly Bill ($)': self._extract_before_monthly(soup),
                'After Monthly Bill ($)': self._extract_after_monthly(soup),
                'Proposal Link': link
            }
            return data
        except Exception as e:
            raise Exception(f"Failed to extract data: {str(e)}")

    def _extract_client_name(self, soup):
        try:
            name_element = soup.find('h1', {'class': 'customer-name'})
            return name_element.text.strip() if name_element else "Unknown"
        except:
            return "Unknown"

    # [Other extraction methods remain similar but simplified]

def get_table_download_link(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Master Sheet', index=False)
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="aurora_data.xlsx">Download Excel file</a>'

def create_summary_stats(df):
    if df.empty:
        return {}
    return {
        "Total Proposals": len(df),
        "Average System Size": f"{df['System Size (kW)'].mean():.2f} kW",
        "Average Price/Watt": f"${df['Price per Watt ($)'].mean():.2f}",
        "Average Bill Offset": f"{df['Bill Offset (%)'].mean():.1f}%"
    }

def main():
    st.set_page_config(page_title="Aurora Proposal Data Extractor", layout="wide")
    
    st.title("☀️ Aurora Proposal Data Extractor")
    
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame()
    
    tab1, tab2, tab3 = st.tabs(["Data Entry", "Dashboard", "Export"])
    
    with tab1:
        link = st.text_input("Paste Aurora Proposal Link:")
        
        if st.button("Process Link", type="primary"):
            try:
                with st.spinner("Processing proposal..."):
                    scraper = AuroraScraper()
                    data = scraper.extract_data(link)
                    
                    new_df = pd.DataFrame([data])
                    if st.session_state.data.empty:
                        st.session_state.data = new_df
                    else:
                        st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)
                    
                st.success("✅ Data extracted successfully!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        if not st.session_state.data.empty:
            st.subheader("Summary")
            stats = create_summary_stats(st.session_state.data)
            cols = st.columns(len(stats))
            for i, (stat, value) in enumerate(stats.items()):
                cols[i].metric(stat, value)
            
            st.subheader("Data View")
            st.dataframe(st.session_state.data)
    
    with tab3:
        if not st.session_state.data.empty:
            st.subheader("Export Data")
            st.markdown(get_table_download_link(st.session_state.data), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
