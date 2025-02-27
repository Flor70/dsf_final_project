import pandas as pd
import os

def load_airports_data(file_path):
    """
    Load airport data from CSV file.
    
    Args:
        file_path (str): Path to the airport CSV file
        
    Returns:
        pandas.DataFrame: DataFrame containing airport data
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        
        # Load CSV file
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        required_columns = ['code', 'name', 'city', 'country']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Required columns missing in file: {', '.join(missing_columns)}")
        
        # Create display column for dropdown
        df['display_name'] = df.apply(
            lambda row: f"{row['code']} - {row['name']} ({row['city']}, {row['country']})" 
            if pd.notna(row['city']) else f"{row['code']} - {row['name']} ({row['country']})",
            axis=1
        )
        
        return df
    
    except Exception as e:
        print(f"Error loading airport data: {str(e)}")
        # Return empty DataFrame in case of error
        return pd.DataFrame(columns=['code', 'name', 'city', 'country', 'display_name'])
