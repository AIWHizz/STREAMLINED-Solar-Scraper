import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def clean_text(text):
    """Clean extracted text by removing extra spaces and newlines"""
    if text:
        return ' '.join(text.strip().split())
    return "Not found"

def extract_number(text):
    """Extract numeric values from text"""
    if text:
        numbers = re.findall(r'[\d,.]+', text)
        if numbers:
            return numbers[0].replace(',', '')
    return "0"

def extract_aurora_data(link):
    """Extract data from Aurora proposal"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug info
        st.write("Attempting to extract data...")
        
        # Extract client name (trying multiple possible selectors)
        name_elements = [
            soup.find('h1', {'class': 'customer-name'}),
            soup.find('div', {'class': 'customer-info'}),
            soup.find('div', text=re.compile('Dear.*')),
        ]
        client_name = next((clean_text(elem.text) for elem in name_elements if elem), "Not found")
        
        # Extract system size
        system_size_elements = [
            soup.find('div', text=re.compile('.*kW.*')),
            soup.find('span', text=re.compile('.*kW.*')),
        ]
        system_size = next((clean_text(elem.text) for elem in system_size_elements if elem), "Not found")
        
        # Extract price data
        price_elements = [
            soup.find('div', text=re.compile('\$.*')),
            soup.find('span', text=re.compile('\$.*')),
        ]
        total_cost = next((clean_text(elem.text) for elem in price_elements if elem), "Not found")
        
        # Debug the HTML structure (in development mode)
        if st.checkbox("Show HTML Structure (Debug)"):
            st.code(soup.prettify())
        
        data = {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Client Name': client_name,
            'System Size': system_size,
            'Price per Watt': "Calculating...",  # Will add calculation
            'Total Cost': total_cost,
            'Link': link
        }
        
        # Show extraction details
        st.write("Extracted Data Details:")
        for key, value in data.items():
            st.write(f"{key}: {value}")
            
        return data
        
    except Exception as e:
        st.error(f"Extraction error: {str(e)}")
        st.write("Response Status:", response.status_code if 'response' in locals() else "No response")
        return None

st.set_page_config(page_title="Aurora Proposal Data Extractor", layout="wide")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()

st.title("☀️ Aurora Proposal Data Extractor")
st.write("Extract proposal data from Aurora Solar")

link = st.text_input("Paste Aurora Proposal Link:")

if st.button("Process Link", type="primary"):
    try:
        with st.spinner("Processing proposal..."):
            data = extract_aurora_data(link)
            if data:
                new_df = pd.DataFrame([data])
                if st.session_state.data.empty:
                    st.session_state.data = new_df
                else:
                    st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)
                st.success("✅ Data extracted successfully!")
            else:
                st.error("Failed to extract data")
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

# Add debug section
with st.expander("Debug Information"):
    st.write("If you're having issues, check here for more details")
    if st.button("Test Connection"):
        try:
            response = requests.get("https://v2.aurorasolar.com")
            st.write(f"Connection Status: {response.status_code}")
        except Exception as e:
            st.write(f"Connection Error: {str(e)}")
