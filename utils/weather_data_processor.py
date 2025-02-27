"""
Weather Data Processor

This module provides functions to fetch historical weather data for a given city and date range,
and process this data to generate statistical summaries.

It uses Open-Meteo's Geocoding API to convert city names to coordinates,
and the Historical Weather API to fetch weather data for the past 5 years.
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional

# Setup constants
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
HISTORICAL_API_URL = "https://archive-api.open-meteo.com/v1/archive"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                         "outputs", "weather_data")


def get_city_coordinates(city_name: str) -> Tuple[float, float, str]:
    """
    Get latitude and longitude for a given city name using the Geocoding API.
    
    Args:
        city_name (str): Name of the city to get coordinates for
        
    Returns:
        Tuple[float, float, str]: Latitude, longitude, and timezone of the city
        
    Raises:
        ValueError: If city not found or API request fails
    """
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    try:
        response = requests.get(GEOCODING_API_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        if not data.get("results"):
            raise ValueError(f"City '{city_name}' not found")
        
        result = data["results"][0]
        return result["latitude"], result["longitude"], result.get("timezone", "UTC")
    
    except requests.RequestException as e:
        raise ValueError(f"Failed to get coordinates for {city_name}: {str(e)}")


def get_historical_weather_data(
    city_name: str, 
    start_date: str, 
    end_date: str
) -> pd.DataFrame:
    """
    Get historical weather data for a city for the past 5 years for the given date range.
    
    Args:
        city_name (str): Name of the destination city
        start_date (str): Start date in format YYYY-MM-DD
        end_date (str): End date in format YYYY-MM-DD
        
    Returns:
        pd.DataFrame: DataFrame with historical weather data
        
    Raises:
        ValueError: If dates are invalid or API request fails
    """
    # Validate date formats
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_dt > end_dt:
            raise ValueError("Start date must be before end date")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    
    # Get city coordinates
    latitude, longitude, timezone = get_city_coordinates(city_name)
    
    # Calculate date ranges for the past 5 years
    current_year = datetime.now().year
    all_data = []
    
    # Process each of the past 5 years
    for year_offset in range(1, 6):
        year = current_year - year_offset
        
        # Adjust dates for the specific year
        year_start_date = f"{year}-{start_dt.month:02d}-{start_dt.day:02d}"
        
        # Handle February 29 for non-leap years
        if start_dt.month == 2 and start_dt.day == 29 and not is_leap_year(year):
            year_start_date = f"{year}-02-28"
            
        # Calculate end date for this year
        if end_dt.month == 2 and end_dt.day == 29 and not is_leap_year(year):
            year_end_date = f"{year}-02-28"
        else:
            year_end_date = f"{year}-{end_dt.month:02d}-{end_dt.day:02d}"
        
        # Fetch data for this year's date range
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": year_start_date,
                "end_date": year_end_date,
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
                "timezone": timezone
            }
            
            response = requests.get(HISTORICAL_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process the data
            if "daily" in data:
                daily_data = data["daily"]
                df = pd.DataFrame({
                    "date": daily_data["time"],
                    "temperature_max": daily_data["temperature_2m_max"],
                    "temperature_min": daily_data["temperature_2m_min"],
                    "precipitation": daily_data["precipitation_sum"],
                    "year": year  # Add year for reference
                })
                all_data.append(df)
            
        except requests.RequestException as e:
            print(f"Warning: Failed to fetch data for {year}: {str(e)}")
            continue
    
    # Combine all years' data
    if not all_data:
        raise ValueError("Failed to fetch weather data for all years")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Add city name for reference
    combined_df["city"] = city_name
    
    return combined_df


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def save_weather_data_to_csv(
    city_name: str, 
    start_date: str, 
    end_date: str
) -> str:
    """
    Fetch historical weather data and save it to a CSV file.
    
    Args:
        city_name (str): Name of the destination city
        start_date (str): Start date in format YYYY-MM-DD
        end_date (str): End date in format YYYY-MM-DD
        
    Returns:
        str: Path to the saved CSV file
        
    Raises:
        ValueError: If data fetching fails
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Get the weather data
        df = get_historical_weather_data(city_name, start_date, end_date)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{city_name.lower().replace(' ', '_')}_{start_date}_{end_date}_{timestamp}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        print(f"Weather data saved to {filepath}")
        
        return filepath
    
    except Exception as e:
        raise ValueError(f"Failed to save weather data: {str(e)}")


def aggregate_weather_data(csv_path: str) -> Dict[str, Any]:
    """
    Aggregate weather data from a CSV file and return a JSON object with statistics.
    
    Args:
        csv_path (str): Path to the CSV file with weather data
        
    Returns:
        Dict[str, Any]: JSON-serializable dictionary with aggregated weather statistics
        
    Raises:
        ValueError: If CSV processing fails
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Extract city and date range from filename
        filename = os.path.basename(csv_path)
        parts = filename.split('_')
        city_name = parts[0].replace('_', ' ').title()
        
        # Calculate aggregated statistics
        stats = {
            "city": city_name,
            "data_source": "Open-Meteo Historical Weather API",
            "analysis_date": datetime.now().strftime('%Y-%m-%d'),
            "years_analyzed": df["year"].nunique(),
            "total_days_analyzed": len(df),
            "temperature": {
                "max": {
                    "average": round(df["temperature_max"].mean(), 1),
                    "highest": round(df["temperature_max"].max(), 1),
                    "lowest": round(df["temperature_max"].min(), 1),
                    "std_dev": round(df["temperature_max"].std(), 1)
                },
                "min": {
                    "average": round(df["temperature_min"].mean(), 1),
                    "highest": round(df["temperature_min"].max(), 1),
                    "lowest": round(df["temperature_min"].min(), 1),
                    "std_dev": round(df["temperature_min"].std(), 1)
                }
            },
            "precipitation": {
                "average_daily": round(df["precipitation"].mean(), 1),
                "max_daily": round(df["precipitation"].max(), 1),
                "total": round(df["precipitation"].sum(), 1),
                "rainy_days": int((df["precipitation"] > 0.1).sum()),
                "rainy_days_percentage": round((df["precipitation"] > 0.1).mean() * 100, 1)
            },
            "monthly_breakdown": get_monthly_breakdown(df)
        }
        
        # Save the JSON to a file
        json_path = csv_path.replace('.csv', '.json')
        with open(json_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Aggregated weather data saved to {json_path}")
        return stats
    
    except Exception as e:
        raise ValueError(f"Failed to aggregate weather data: {str(e)}")


def get_monthly_breakdown(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate monthly statistics breakdown from weather data.
    
    Args:
        df (pd.DataFrame): DataFrame with weather data
        
    Returns:
        List[Dict[str, Any]]: List of monthly statistics
    """
    # Extract month from date
    df['month'] = pd.to_datetime(df['date']).dt.month
    
    # Group by month and calculate statistics
    monthly_stats = []
    
    for month in range(1, 13):
        month_df = df[df['month'] == month]
        
        # Skip months with no data
        if len(month_df) == 0:
            continue
        
        month_name = datetime(2000, month, 1).strftime('%B')
        stats = {
            "month": month_name,
            "days_with_data": len(month_df),
            "temperature_max_avg": round(month_df["temperature_max"].mean(), 1),
            "temperature_min_avg": round(month_df["temperature_min"].mean(), 1),
            "precipitation_avg": round(month_df["precipitation"].mean(), 1),
            "rainy_days_percentage": round((month_df["precipitation"] > 0.1).mean() * 100, 1)
        }
        monthly_stats.append(stats)
    
    return monthly_stats


if __name__ == "__main__":
    # Example usage
    try:
        # Example: Get weather data for Madrid for a summer vacation period
        city = input("Enter city name: ")
        start = input("Enter start date (YYYY-MM-DD): ")
        end = input("Enter end date (YYYY-MM-DD): ")
        
        print(f"Fetching historical weather data for {city} from {start} to {end}...")
        csv_path = save_weather_data_to_csv(city, start, end)
        
        print("\nAggregating weather data...")
        weather_stats = aggregate_weather_data(csv_path)
        
        print("\nWeather Analysis Summary:")
        print(f"City: {weather_stats['city']}")
        print(f"Average Max Temperature: {weather_stats['temperature']['max']['average']}°C")
        print(f"Average Min Temperature: {weather_stats['temperature']['min']['average']}°C")
        print(f"Rainy Days Percentage: {weather_stats['precipitation']['rainy_days_percentage']}%")
        
    except Exception as e:
        print(f"Error: {str(e)}")
