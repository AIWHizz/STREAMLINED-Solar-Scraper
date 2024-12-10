import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

def extract_aurora_data(link):
    try:
        # Setup headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://v2.aurorasolar.com/',
            'Origin': 'https://v2.aurorasolar.com'
        }
        
        # Extract proposal ID
        proposal_id = link.split('/')[-1]
        
        # Try the API endpoint first
        api_url = f"https://v2.aurorasolar.com/api/v2/proposals/{proposal_id}"
        response = requests.get(api_url, headers=headers)
        
        # Debug information
        st.write("Attempting to fetch data...")
        st.write(f"API Response Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                st.write("Successfully retrieved JSON data")
                return {
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Client Name': data.get('customer', {}).get('name', 'Not found'),
                    'System Size': f"{data.get('system', {}).get('size_kw', 0)} kW",
                    'Price per Watt': f"${data.get('pricing', {}).get('price_per_watt', 0):.2f}",
                    'Total Cost': f"${data.get('pricing', {}).get('total_cost', 0):,.2f}",
                    'Link': link
                }
            except json.JSONDecodeError:
                st.write("Could not parse JSON response")
        
        # Fallback to HTML scraping
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for data in script tags
        scripts = soup.find_all('script')
        data_script = None
        for script in scripts:
            if script.string and ('__INITIAL_STATE__' in script.string or 'window.PROPOSAL_DATA' in script.string):
                data_script = script.string
                break
        
        if data_script:
            # Try to extract JSON data
            try:
                json_str = re.search(r'({.*})', data_script).group(1)
                data = json.loads(json_str)
                st.write("Found data in script tag")
                return {
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Client Name': data.get('customer', {}).get('name', 'Not found'),
                    'System Size': f"{data.get('system', {}).get('size_kw', 0)} kW",
                    'Price per Watt': f"${data.get('pricing', {}).get('price_per_watt', 0):.2f}",
                    'Total Cost': f"${data.get('pricing', {}).get('total_cost', 0):,.2f}",
                    'Link': link
                }
            except Exception as e:
                st.write(f"Error parsing script data: {str(e)}")
        
        # If all else fails, try direct HTML elements
        client_name = soup.find('p', {'class': re.compile('.*customer-name.*')})
        system_size = soup.find(string=re.compile(r'.*kW.*'))
        price = soup.find(string=re.compile(r'\$[\d,]+\.?\d*'))
        
        return {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Client Name': client_name.text if client_name else "Not found",
            'System Size': system_size if system_size else "Not found",
            'Price per Watt': "Not found",
            'Total Cost': price if price else "Not found",
            'Link': link
        }
        
    except Exception as e:
        st.error(f"Error during extraction: {str(e)}")
        return None
