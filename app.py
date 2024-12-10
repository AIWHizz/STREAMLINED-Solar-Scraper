import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Aurora Data Extractor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()

# Title
st.title("☀️ Aurora Proposal Data Extractor")

# Input
link = st.text_input("Paste Aurora Proposal Link:")

def extract_data(html_content):
    """Extract data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find client name
    name_selectors = [
        'div.customer-info',
        'h1.customer-name',
        'div.customer-name',
        'p.customer-name'
    ]
    
    client_name = "Not Found"
    for selector in name_selectors:
        element = soup.select_one(selector)
        if element and element.text.strip():
            client_name = element.text.strip()
            break
    
    # Find system size (kW)
    system_size = "Not Found"
    size_elements = soup.find_all(['div', 'span', 'p'])
    for elem in size_elements:
        if elem.text and 'kW' in elem.text:
            system_size = elem.text.strip()
            break
    
    # Find total cost
    total_cost = "Not Found"
    cost_elements = soup.find_all(['div', 'span', 'p'])
    for elem in cost_elements:
        if elem.text and '$' in elem.text:
            total_cost = elem.text.strip()
            break
    
    # Calculate price per watt
    try:
        size_num = float(''.join(filter(str.isdigit, system_size)))
        cost_num = float(''.join(filter(str.isdigit, total_cost)))
        price_per_watt = f"${cost_num / (size_num * 1000):.2f}"
    except:
        price_per_watt = "Not Found"
    
    return {
        'client_name': client_name,
        'system_size': system_size,
        'total_cost': total_cost,
        'price_per_watt': price_per_watt
    }

if st.button("Process Link", type="primary"):
    try:
        with st.spinner("Processing..."):
            # Setup headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            # Get the page content
            response = requests.get(link, headers=headers)
            
            # Show status code for debugging
            st.write(f"Response Status: {response.status_code}")
            
            # Extract data
            extracted_data = extract_data(response.text)
            
            # Store data
            data = {
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Client Name': extracted_data['client_name'],
                'System Size': extracted_data['system_size'],
                'Price per Watt': extracted_data['price_per_watt'],
                'Total Cost': extracted_data['total_cost'],
                'Link': link
            }
            
            # Add to dataframe
            new_df = pd.DataFrame([data])
            if st.session_state.data.empty:
                st.session_state.data = new_df
            else:
                st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)
            
        st.success("✅ Processed successfully!")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Display data
if not st.session_state.data.empty:
    st.subheader("Extracted Data")
    st.dataframe(st.session_state.data)
    
    # Download button
    csv = st.session_state.data.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="aurora_data.csv",
        mime="text/csv"
    )

# Debug section
with st.expander("Debug Information"):
    if st.button("Show HTML Structure"):
        if 'response' in locals():
            st.code(BeautifulSoup(response.text, 'html.parser').prettify())
