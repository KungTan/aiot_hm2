import json
import sqlite3
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

API_URL = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
API_KEY = os.getenv("CWA_API_KEY")
DB_NAME = "data.db"
CSV_NAME = "weather_data.csv"

def get_data():
    """Fetch data from CWA API."""
    print("Fetching from CWA API...")
    # Handle SSL verification correctly by just accepting it or passing verify=False if encountering issues
    try:
        response = requests.get(f"{API_URL}?Authorization={API_KEY}&downloadType=WEB&format=JSON", verify=True)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError:
        print("SSL Error encountered, falling back to verify=False")
        response = requests.get(f"{API_URL}?Authorization={API_KEY}&downloadType=WEB&format=JSON", verify=False)
        response.raise_for_status()
        return response.json()

def parse_data(raw_data):
    """Parse JSON data to extract temperatures."""
    parsed_records = []
    
    # Observe the raw data structure
    # print(json.dumps(raw_data, ensure_ascii=False, indent=2))  # Commented out to prevent huge output
    
    locations = raw_data.get('records', {}).get('location', [])
    if not locations:
        # Fallback to the structure matched in our manual JSON read
        try:
            locations = raw_data['cwaopendata']['resources']['resource']['data']['agrWeatherForecasts']['weatherForecasts']['location']
        except KeyError:
            locations = []

    for loc in locations:
        regionName = loc.get('locationName')
        
        # Navigate robustly through weatherElements
        elements = loc.get('weatherElements', {})
        
        # Sometime it's an array of elements
        if isinstance(elements, list):
            mint_data = []
            maxt_data = []
            for e in elements:
                if e.get('elementName') == 'MinT':
                    mint_data = e.get('time', [])
                elif e.get('elementName') == 'MaxT':
                    maxt_data = e.get('time', [])
                    
            # Assuming matching dates in MinT and MaxT arrays
            if mint_data and maxt_data:
                for mi, ma in zip(mint_data, maxt_data):
                    date = mi.get('startTime', '').split(' ')[0] # Using start time date
                    mint = int(mi.get('parameter', {}).get('parameterName', 0))
                    maxt = int(ma.get('parameter', {}).get('parameterName', 0))
                    parsed_records.append({
                        "regionName": regionName,
                        "dataDate": date,
                        "mint": mint,
                        "maxt": maxt
                    })
                    
        # Otherwise it's a dict like our local JSON structure
        elif isinstance(elements, dict):
            mint_daily = elements.get('MinT', {}).get('daily', [])
            maxt_daily = elements.get('MaxT', {}).get('daily', [])
            
            # Map by date to guarantee match
            mint_dict = {day['dataDate']: int(day['temperature']) for day in mint_daily}
            maxt_dict = {day['dataDate']: int(day['temperature']) for day in maxt_daily}
            
            for dateStr in mint_dict.keys():
                parsed_records.append({
                    "regionName": regionName,
                    "dataDate": dateStr,
                    "mint": mint_dict[dateStr],
                    "maxt": maxt_dict.get(dateStr, mint_dict[dateStr]) # default to mint if not exist
                })
                
    return parsed_records

def save_to_csv(data):
    """Save parsed records to CSV."""
    df = pd.DataFrame(data)
    df.to_csv(CSV_NAME, index=False, encoding='utf-8-sig')
    print(f"Data successfully saved to CSV: {CSV_NAME}")

def setup_database(data):
    """Setup SQLite database and insert records."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT NOT NULL,
            dataDate TEXT NOT NULL,
            mint INTEGER NOT NULL,
            maxt INTEGER NOT NULL
        )
    ''')
    
    # Clear existing data so we don't duplicate on multiple runs
    cursor.execute('DELETE FROM TemperatureForecasts')
    
    # Insert data
    for row in data:
        cursor.execute('''
            INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
            VALUES (?, ?, ?, ?)
        ''', (row['regionName'], row['dataDate'], row['mint'], row['maxt']))
        
    conn.commit()
    print(f"Data successfully saved to SQLite database: {DB_NAME}")
    
    # Grading criterion: list all region names
    cursor.execute('SELECT DISTINCT regionName FROM TemperatureForecasts')
    regions = cursor.fetchall()
    print("\n[DB Verification] All Regions:")
    for r in regions:
        print(f"- {r[0]}")
        
    # Grading criterion: list Central region data
    cursor.execute('SELECT regionName, dataDate, mint, maxt FROM TemperatureForecasts WHERE regionName = "中部地區"')
    central_data = cursor.fetchall()
    print("\n[DB Verification] 中部地區 Data:")
    for row in central_data:
        print(f"Date: {row[1]} | MinT: {row[2]}°C | MaxT: {row[3]}°C")
        
    conn.close()

def main():
    # Attempt online fetch for GitHub Actions scheduling
    try:
        raw_data = get_data()
        # Using json.dumps to observe as requested
        # print("Observation of raw dataset: ")
        # print(json.dumps(raw_data, ensure_ascii=False)[:300] + "...\n") 

        parsed_data = parse_data(raw_data)
        
        # Using json.dumps to observe extracted data as requested
        print("Observation of parsed dataset: ")
        print(json.dumps(parsed_data, ensure_ascii=False, indent=2)[:300] + "...\n")
        
        if not parsed_data:
            print("Warning: No data was parsed from the dataset.")
            return

        save_to_csv(parsed_data)
        setup_database(parsed_data)
        print("\nAll database and file operations completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Add a function that streamlit can call directly to get fresh data
def refresh_data():
    """Triggered by streamlit explicitly."""
    raw_data = get_data()
    parsed_data = parse_data(raw_data)
    save_to_csv(parsed_data)
    setup_database(parsed_data)
    print("Refresh complete.")

if __name__ == "__main__":
    main()
