"""
Flight data processing utilities for merging and analyzing flight data from CSV files.
"""

import os
import pandas as pd
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


def merge_weekend_flight_data(directory_path: str, num_cheapest_flights: int = 3) -> str:
    """
    Merge all CSV files in the specified directory and find the cheapest flights.
    
    Args:
        directory_path (str): Path to the directory containing flight CSV files
        num_cheapest_flights (int): Number of cheapest flights to return
        
    Returns:
        str: JSON string containing the cheapest flights with all metadata
    """
    # Check if directory exists
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    
    if not csv_files:
        raise ValueError(f"No CSV files found in directory: {directory_path}")
    
    # Initialize an empty list to store all dataframes
    all_dfs = []
    
    # Read and combine all CSV files
    for file in csv_files:
        file_path = os.path.join(directory_path, file)
        try:
            # Extract date information from filename (assuming format serpapi_raw_ORIGIN_DEST_YYYY-MM-DD.csv)
            date_info = file.split('_')[-1].replace('.csv', '')
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Add source file information
            df['source_file'] = file
            df['search_date'] = date_info
            
            # Append to the list of dataframes
            all_dfs.append(df)
            
        except Exception as e:
            print(f"Error reading file {file}: {str(e)}")
    
    # Combine all dataframes
    if not all_dfs:
        raise ValueError("No valid data found in CSV files")
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Convert price to numeric to ensure proper sorting
    combined_df['price'] = pd.to_numeric(combined_df['price'], errors='coerce')
    
    # Sort by price and get the cheapest flights
    cheapest_flights = combined_df.sort_values('price').head(num_cheapest_flights)
    
    # Convert to dictionary format
    result = []
    for _, flight in cheapest_flights.iterrows():
        flight_dict = flight.to_dict()
        
        # Add additional metadata
        flight_dict['search_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean up the dictionary (remove NaN values)
        flight_dict = {k: ('' if pd.isna(v) else v) for k, v in flight_dict.items()}
        
        result.append(flight_dict)
    
    # Convert to JSON
    json_result = json.dumps(result, indent=2)
    
    return json_result


def save_cheapest_flights_json(directory_path: str, output_dir: str, num_cheapest_flights: int = 3) -> str:
    """
    Find the cheapest flights from CSV files and save the results to a JSON file.
    
    Args:
        directory_path (str): Path to the directory containing flight CSV files
        output_dir (str): Directory to save the output JSON file
        num_cheapest_flights (int): Number of cheapest flights to return
        
    Returns:
        str: Path to the saved JSON file
    """
    try:
        # Get the cheapest flights as JSON
        json_data = merge_weekend_flight_data(directory_path, num_cheapest_flights)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f"cheapest_flights_{timestamp}.json")
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(json_data)
        
        print(f"Saved cheapest flights data to {output_file}")
        return output_file
    
    except Exception as e:
        print(f"Error saving cheapest flights: {str(e)}")
        return ""


def analyze_weekend_flight_trends(directory_path: str) -> Dict[str, Any]:
    """
    Analyze trends in weekend flight data from CSV files.
    
    Args:
        directory_path (str): Path to the directory containing flight CSV files
        
    Returns:
        Dict: Dictionary containing trend analysis results
    """
    try:
        # Get all CSV files in the directory
        csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
        
        if not csv_files:
            return {"error": f"No CSV files found in directory: {directory_path}"}
        
        # Initialize an empty list to store all dataframes
        all_dfs = []
        
        # Read and combine all CSV files
        for file in csv_files:
            file_path = os.path.join(directory_path, file)
            try:
                # Extract date information from filename
                date_parts = file.split('_')
                if len(date_parts) >= 4:
                    origin = date_parts[2]
                    dest_date = date_parts[3].replace('.csv', '')
                    dest, date = dest_date.split('_') if '_' in dest_date else (dest_date.split('-')[0], dest_date)
                else:
                    origin, dest, date = "unknown", "unknown", "unknown"
                
                # Read the CSV file
                df = pd.read_csv(file_path)
                
                # Add metadata
                df['origin'] = origin
                df['destination'] = dest
                df['date'] = date
                df['source_file'] = file
                
                # Append to the list of dataframes
                all_dfs.append(df)
                
            except Exception as e:
                print(f"Error reading file {file}: {str(e)}")
        
        # Combine all dataframes
        if not all_dfs:
            return {"error": "No valid data found in CSV files"}
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # Convert price to numeric
        combined_df['price'] = pd.to_numeric(combined_df['price'], errors='coerce')
        
        # Analyze the data
        analysis = {
            "total_flights": len(combined_df),
            "unique_airlines": combined_df['airline'].nunique(),
            "price_statistics": {
                "min": combined_df['price'].min(),
                "max": combined_df['price'].max(),
                "mean": combined_df['price'].mean(),
                "median": combined_df['price'].median()
            },
            "airlines": combined_df['airline'].value_counts().to_dict(),
            "cheapest_airline": combined_df.groupby('airline')['price'].mean().idxmin(),
            "most_expensive_airline": combined_df.groupby('airline')['price'].mean().idxmax(),
        }
        
        return analysis
    
    except Exception as e:
        return {"error": f"Error analyzing flight trends: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    try:
        # Path to the directory containing flight CSV files
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "outputs", "raw_data")
        
        # Output directory path
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 "outputs", "cheapest_flights")
        
        # Find and save the 3 cheapest flights
        save_cheapest_flights_json(data_dir, output_dir, 3)
        
        # Analyze flight trends
        trends = analyze_weekend_flight_trends(data_dir)
        print("\nFlight Trends Analysis:")
        print(json.dumps(trends, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")
