# services/data_service.py
import pandas as pd
import os
from datetime import datetime
from config import CSV_FILE, MAX_DATA_POINTS

class DataService:
    def __init__(self):
        self.csv_file = CSV_FILE
        
    def save_to_csv(self, data):
        """Save sensor data to CSV file"""
        try:
            # Create DataFrame from new data
            new_df = pd.DataFrame([data])
            
            # Read existing data or create new DataFrame
            if os.path.exists(self.csv_file):
                existing_df = pd.read_csv(self.csv_file)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            # Limit data points to prevent unlimited growth
            if len(combined_df) > MAX_DATA_POINTS:
                combined_df = combined_df.tail(MAX_DATA_POINTS)
            
            # Save to CSV
            combined_df.to_csv(self.csv_file, index=False)
            print(f"💾 Saved data to CSV (Total records: {len(combined_df)})")
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
    
    def get_historical_data(self, limit=1000):
        """Get historical data from CSV"""
        try:
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
                return df.tail(limit)
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error reading historical data: {e}")
            return pd.DataFrame()
    
    def clear_old_data(self):
        """Clear old data beyond MAX_DATA_POINTS"""
        try:
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
                if len(df) > MAX_DATA_POINTS:
                    df = df.tail(MAX_DATA_POINTS)
                    df.to_csv(self.csv_file, index=False)
                    print(f"🧹 Cleared old data, kept {len(df)} records")
        except Exception as e:
            print(f"❌ Error clearing old data: {e}")