"""
Integrated View Module

This module provides functions to create an integrated view of flight, weather, and price data.
It consolidates information from three different APIs:
1. Flight data from SerpAPI
2. Weather data from Open-Meteo
3. Historical price data from Amadeus

The integrated view organizes information by flight/weekend, showing:
- Flight details (price, airline, times, etc.)
- Weather data (temperature, precipitation) for the destination
- Historical price metrics for the route
"""

import os
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Setup constants
CHEAPEST_FLIGHTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "outputs", "cheapest_flights")
WEATHER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "outputs", "weather_data")
AMADEUS_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "outputs", "amadeus_data")


def find_latest_files() -> Dict[str, str]:
    """
    Find the latest files from each data source.

    Returns:
        Dict[str, str]: Dictionary with paths to the latest files
    """
    files = {
        "flights": None,
        "weather_json": None,
        "weather_csv": None,
        "amadeus_combined": None
    }

    # Find latest cheapest flights file
    if os.path.exists(CHEAPEST_FLIGHTS_DIR):
        flight_files = [f for f in os.listdir(CHEAPEST_FLIGHTS_DIR)
                        if f.startswith("cheapest_flights_") and f.endswith(".json")]
        if flight_files:
            files["flights"] = os.path.join(
                CHEAPEST_FLIGHTS_DIR, sorted(flight_files)[-1])

    # Find latest weather data files
    if os.path.exists(WEATHER_DATA_DIR):
        weather_json_files = [f for f in os.listdir(
            WEATHER_DATA_DIR) if f.endswith(".json")]
        weather_csv_files = [f for f in os.listdir(
            WEATHER_DATA_DIR) if f.endswith(".csv")]

        if weather_json_files:
            files["weather_json"] = os.path.join(
                WEATHER_DATA_DIR, sorted(weather_json_files)[-1])

        if weather_csv_files:
            files["weather_csv"] = os.path.join(
                WEATHER_DATA_DIR, sorted(weather_csv_files)[-1])

    # Find latest Amadeus data files
    if os.path.exists(AMADEUS_DATA_DIR):
        amadeus_files = [f for f in os.listdir(AMADEUS_DATA_DIR)
                         if f.endswith(".json") and "combined" in f]

        if amadeus_files:
            files["amadeus_combined"] = os.path.join(
                AMADEUS_DATA_DIR, sorted(amadeus_files)[-1])

    return files


def load_flight_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load flight data from JSON file.

    Args:
        file_path (str): Path to the flight data JSON file

    Returns:
        List[Dict[str, Any]]: List of flight data dictionaries
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if "cheapest_flights" in data and isinstance(data["cheapest_flights"], list):
            return data["cheapest_flights"]
        return []
    except Exception as e:
        print(f"Error loading flight data: {e}")
        return []


def load_weather_data(json_path: str, csv_path: str) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Load weather data from JSON and CSV files.

    Args:
        json_path (str): Path to the weather data JSON file
        csv_path (str): Path to the weather data CSV file

    Returns:
        Tuple[Dict[str, Any], pd.DataFrame]: Weather statistics and raw weather data
    """
    weather_stats = {}
    weather_df = pd.DataFrame()

    try:
        # Load JSON stats
        if json_path and os.path.exists(json_path):
            with open(json_path, 'r') as f:
                weather_stats = json.load(f)

        # Load CSV data
        if csv_path and os.path.exists(csv_path):
            weather_df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading weather data: {e}")

    return weather_stats, weather_df


def load_amadeus_data(file_path: str) -> Dict[str, Any]:
    """
    Load Amadeus price data from JSON file.

    Args:
        file_path (str): Path to the Amadeus data JSON file

    Returns:
        Dict[str, Any]: Dictionary with price metrics data
    """
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading Amadeus data: {e}")
        return {}


def get_weather_for_date(weather_df: pd.DataFrame, date_str: str) -> Dict[str, Any]:
    """
    Get weather data for a specific date from all available years.

    Args:
        weather_df (pd.DataFrame): DataFrame with weather data
        date_str (str): Date string in format 'YYYY-MM-DD'

    Returns:
        Dict[str, Any]: Dictionary with weather statistics for the date
    """
    # Extract month and day from the date
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        month, day = date.month, date.day

        # Filter data for the same month and day across all years
        date_data = weather_df[
            (weather_df['date'].str[5:7] == f"{month:02d}") &
            (weather_df['date'].str[8:10] == f"{day:02d}")
        ]

        if len(date_data) == 0:
            return {}

        # Calculate statistics
        stats = {
            "temperature_max": {
                "average": round(date_data["temperature_max"].mean(), 1),
                "by_year": {year: round(group["temperature_max"].mean(), 1)
                            for year, group in date_data.groupby("year")}
            },
            "temperature_min": {
                "average": round(date_data["temperature_min"].mean(), 1),
                "by_year": {year: round(group["temperature_min"].mean(), 1)
                            for year, group in date_data.groupby("year")}
            },
            "precipitation": {
                "average": round(date_data["precipitation"].mean(), 1),
                "by_year": {year: round(group["precipitation"].mean(), 1)
                            for year, group in date_data.groupby("year")}
            },
            "years": sorted(date_data["year"].unique().tolist())
        }

        return stats
    except Exception as e:
        print(f"Error processing weather for date {date_str}: {e}")
        return {}


def get_price_metrics_for_date(amadeus_data: Dict[str, Any], date_str: str) -> Dict[str, Any]:
    """
    Get price metrics for a specific date from Amadeus data.

    Args:
        amadeus_data (Dict[str, Any]): Amadeus data dictionary
        date_str (str): Date string in format 'YYYY-MM-DD'

    Returns:
        Dict[str, Any]: Dictionary with price metrics for the date
    """
    if not amadeus_data or "data" not in amadeus_data:
        return {}

    for item in amadeus_data["data"]:
        if item.get("departureDate") == date_str:
            metrics = {}
            for metric in item.get("priceMetrics", []):
                metrics[metric.get("quartileRanking", "").lower()] = float(
                    metric.get("amount", 0))

            return {
                "currency": item.get("currencyCode", "USD"),
                "metrics": metrics
            }

    return {}


def organize_flights_by_weekend(flights: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Organize flights by weekend/date.

    Args:
        flights (List[Dict[str, Any]]): List of flight data dictionaries

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary with flights organized by date
    """
    weekends = {}

    for flight in flights:
        date = flight.get("search_date", "")
        if date:
            if date not in weekends:
                weekends[date] = []
            weekends[date].append(flight)

    return weekends


def plot_weather_history(weather_data: Dict[str, Any], date_str: str) -> plt.Figure:
    """
    Create a plot showing historical weather data for a specific date.

    Args:
        weather_data (Dict[str, Any]): Weather data for the date
        date_str (str): Date string in format 'YYYY-MM-DD'

    Returns:
        plt.Figure: Matplotlib figure with the plot
    """
    if not weather_data or "years" not in weather_data:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No weather data available",
                ha='center', va='center', fontsize=12)
        return fig

    years = weather_data["years"]
    max_temps = [weather_data["temperature_max"]
                 ["by_year"].get(year, 0) for year in years]
    min_temps = [weather_data["temperature_min"]
                 ["by_year"].get(year, 0) for year in years]
    precip = [weather_data["precipitation"]
              ["by_year"].get(year, 0) for year in years]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(
        10, 8), gridspec_kw={'height_ratios': [3, 1]})

    # Temperature plot
    ax1.plot(years, max_temps, 'o-', color='red', label='Max Temperature (°C)')
    ax1.plot(years, min_temps, 'o-', color='blue',
             label='Min Temperature (°C)')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title(
        f'Historical Weather for {date_str} (Last {len(years)} Years)')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()

    # Precipitation plot
    bars = ax2.bar(years, precip, color='skyblue', alpha=0.7)
    ax2.set_ylabel('Precipitation (mm)')
    ax2.set_xlabel('Year')
    ax2.grid(True, linestyle='--', alpha=0.7, axis='y')

    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.1f}', ha='center', va='bottom')

    plt.tight_layout()
    return fig


def evaluate_price(current_price: float, price_metrics: Dict[str, Any]) -> Tuple[str, str]:
    """
    Evaluate if the current price is good compared to historical data.

    Args:
        current_price (float): Current price of the flight
        price_metrics (Dict[str, Any]): Historical price metrics

    Returns:
        Tuple[str, str]: Price evaluation and color
    """
    if not price_metrics or "metrics" not in price_metrics:
        return "No historical data", "gray"

    metrics = price_metrics["metrics"]

    if "minimum" not in metrics or "maximum" not in metrics:
        return "Incomplete data", "gray"

    minimum = metrics.get("minimum", 0)
    first = metrics.get("first", 0)
    medium = metrics.get("medium", 0)
    third = metrics.get("third", 0)
    maximum = metrics.get("maximum", 0)

    # Convert current price to same currency if needed
    # This is a simplification - in a real app, you'd use currency conversion

    if current_price <= minimum * 1.1:
        return "Excellent price! (Lowest historical)", "green"
    elif current_price <= first:
        return "Very good price (Lower 25%)", "lightgreen"
    elif current_price <= medium:
        return "Average price (25-50%)", "blue"
    elif current_price <= third:
        return "Above average (50-75%)", "orange"
    else:
        return "High price (Top 25%)", "red"


def display_integrated_view():
    """
    Display an integrated view of flight, weather, and price data.
    """
    st.title("🌍✈️ Integrated Travel Planner")

    # Find latest files
    files = find_latest_files()

    if not files["flights"]:
        st.warning("No flight data found. Please search for flights first.")
        return

    # Load data
    flights = load_flight_data(files["flights"])
    weather_stats, weather_df = load_weather_data(
        files["weather_json"], files["weather_csv"])
    amadeus_data = load_amadeus_data(files["amadeus_combined"])

    if not flights:
        st.warning("No flight data available.")
        return

    # Organize flights by weekend
    weekends = organize_flights_by_weekend(flights)

    # Display each weekend section
    for date, date_flights in weekends.items():
        st.header(f"🗓️ Weekend of {date}")

        # Get weather data for this date
        date_weather = get_weather_for_date(weather_df, date)

        # Get price metrics for this date
        price_metrics = get_price_metrics_for_date(amadeus_data, date)

        # Display each flight in this weekend
        for i, flight in enumerate(date_flights):
            with st.container():
                cols = st.columns([3, 2])

                with cols[0]:
                    # Flight details
                    st.subheader(
                        f"✈️ {flight.get('airline', 'Unknown')} Flight")

                    # Price and evaluation
                    price = flight.get('price', 0)
                    evaluation, color = evaluate_price(price, price_metrics)

                    st.markdown(f"""
                    **Price:** ${price:.2f} - <span style='color:{color};'>{evaluation}</span>
                    
                    **From:** {flight.get('departure_airport', '')} ({flight.get('departure_airport_code', '')})  
                    **To:** {flight.get('arrival_airport', '')} ({flight.get('arrival_airport_code', '')})
                    
                    **Departure:** {flight.get('departure_time', '')}  
                    **Arrival:** {flight.get('arrival_time', '')}
                    
                    **Duration:** {flight.get('total_duration_minutes', 0) // 60}h {flight.get('total_duration_minutes', 0) % 60}m  
                    **Layovers:** {flight.get('num_layovers', 0)}
                    """, unsafe_allow_html=True)

                with cols[1]:
                    # Weather summary
                    if date_weather:
                        st.subheader("🌤️ Weather Summary")
                        st.markdown(f"""
                        **Average Max Temp:** {date_weather.get('temperature_max', {}).get('average', 'N/A')}°C  
                        **Average Min Temp:** {date_weather.get('temperature_min', {}).get('average', 'N/A')}°C  
                        **Average Precipitation:** {date_weather.get('precipitation', {}).get('average', 'N/A')} mm
                        """)

                    # Price metrics
                    if price_metrics and "metrics" in price_metrics:
                        metrics = price_metrics["metrics"]
                        currency = price_metrics.get("currency", "USD")

                        st.subheader("💰 Historical Price Range")
                        st.markdown(f"""
                        **Minimum:** ${metrics.get('minimum', 'N/A')} {currency}  
                        **Median:** ${metrics.get('medium', 'N/A')} {currency}  
                        **Maximum:** ${metrics.get('maximum', 'N/A')} {currency}
                        """)

                # Historical weather chart
                if date_weather:
                    st.subheader("📊 Historical Weather Trends")
                    fig = plot_weather_history(date_weather, date)
                    st.pyplot(fig)

                st.markdown("---")


def display_integrated_dashboard():
    """
    Display the main integrated dashboard.
    """
    # Find latest files
    files = find_latest_files()

    if not files["flights"]:
        st.warning("No flight data found. Please search for flights first.")
        return

    # Load data
    flights = load_flight_data(files["flights"])
    weather_stats, weather_df = load_weather_data(
        files["weather_json"], files["weather_csv"])
    amadeus_data = load_amadeus_data(files["amadeus_combined"])

    if not flights:
        st.warning("No flight data available.")
        return

    # Organize flights by weekend
    weekends = organize_flights_by_weekend(flights)

    # Display the integrated view directly without tabs
    display_integrated_view()


if __name__ == "__main__":
    # This is for testing purposes
    st.set_page_config(page_title="Integrated Travel Planner", layout="wide")
    display_integrated_dashboard()
