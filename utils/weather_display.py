"""
Weather Display Module

This module provides functions to display historical weather data in the Streamlit interface.
It uses the output from weather_data_processor.py to create visualizations and summaries
of historical weather patterns for a given destination.
"""

import os
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


def find_latest_weather_files() -> Tuple[Optional[str], Optional[str]]:
    """
    Find the latest weather data files (CSV and JSON) in the weather_data directory.

    Returns:
        Tuple[Optional[str], Optional[str]]: Paths to the latest CSV and JSON files
    """
    try:
        # Get the weather_data directory path
        weather_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "outputs", "weather_data")

        if not os.path.exists(weather_data_dir):
            return None, None

        # Get all files in the directory
        all_files = os.listdir(weather_data_dir)

        # Filter CSV and JSON files
        csv_files = [f for f in all_files if f.endswith('.csv')]
        json_files = [f for f in all_files if f.endswith('.json')]

        if not csv_files:
            return None, None

        # Sort by modification time (newest first)
        csv_files.sort(key=lambda x: os.path.getmtime(
            os.path.join(weather_data_dir, x)), reverse=True)

        # Get the latest CSV file
        latest_csv = os.path.join(weather_data_dir, csv_files[0])

        # Find the corresponding JSON file
        json_file = csv_files[0].replace('.csv', '.json')
        latest_json = os.path.join(
            weather_data_dir, json_file) if json_file in json_files else None

        return latest_csv, latest_json

    except Exception as e:
        st.error(f"Error finding weather files: {str(e)}")
        return None, None


def load_weather_data(json_path: str) -> Dict[str, Any]:
    """
    Load weather data from a JSON file.

    Args:
        json_path (str): Path to the JSON file with aggregated weather data

    Returns:
        Dict[str, Any]: Dictionary containing the weather data

    Raises:
        ValueError: If file not found or invalid JSON
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise ValueError(f"Error loading weather data: {str(e)}")


def load_raw_weather_data(csv_path: str) -> pd.DataFrame:
    """
    Load raw weather data from a CSV file.

    Args:
        csv_path (str): Path to the CSV file with raw weather data

    Returns:
        pd.DataFrame: DataFrame containing the raw weather data

    Raises:
        ValueError: If file not found or invalid CSV
    """
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        raise ValueError(f"Error loading raw weather data: {str(e)}")


def display_weather_summary(weather_data: Dict[str, Any]) -> None:
    """
    Display a summary of the weather data.

    Args:
        weather_data (Dict[str, Any]): Dictionary containing the aggregated weather data
    """
    if not weather_data:
        st.error("No weather data available")
        return

    # Extract basic information
    city = weather_data.get("city", "Unknown")
    years_analyzed = weather_data.get("years_analyzed", 0)
    total_days = weather_data.get("total_days_analyzed", 0)

    # Display header
    st.subheader(f"🌤️ Historical Weather Data for {city}")
    st.write(
        f"Analysis based on {years_analyzed} years of data ({total_days} days)")

    # Create columns for temperature and precipitation
    col1, col2 = st.columns(2)

    # Temperature data
    with col1:
        st.markdown("### 🌡️ Temperature")

        temp_max = weather_data.get("temperature", {}).get("max", {})
        temp_min = weather_data.get("temperature", {}).get("min", {})

        st.write(f"**Average High:** {temp_max.get('average', 'N/A')}°C")
        st.write(f"**Average Low:** {temp_min.get('average', 'N/A')}°C")
        st.write(f"**Highest Recorded:** {temp_max.get('highest', 'N/A')}°C")
        st.write(f"**Lowest Recorded:** {temp_min.get('lowest', 'N/A')}°C")

    # Precipitation data
    with col2:
        st.markdown("### 🌧️ Precipitation")

        precip = weather_data.get("precipitation", {})

        st.write(f"**Average Daily:** {precip.get('average_daily', 'N/A')} mm")
        st.write(f"**Maximum Daily:** {precip.get('max_daily', 'N/A')} mm")
        st.write(
            f"**Rainy Days:** {precip.get('rainy_days_percentage', 'N/A')}% of the period")


def display_monthly_breakdown(weather_data: Dict[str, Any]) -> None:
    """
    Display monthly breakdown of weather data.

    Args:
        weather_data (Dict[str, Any]): Dictionary containing the aggregated weather data
    """
    monthly_data = weather_data.get("monthly_breakdown", [])

    if not monthly_data:
        return

    st.markdown("### 📅 Monthly Weather Patterns")

    # Create dataframe for the monthly data
    df = pd.DataFrame(monthly_data)

    # Create bar chart for temperature
    fig, ax = plt.subplots(figsize=(10, 6))

    x = range(len(df))
    width = 0.35

    ax.bar([i - width/2 for i in x], df["temperature_max_avg"],
           width, label="Avg Max Temp (°C)")
    ax.bar([i + width/2 for i in x], df["temperature_min_avg"],
           width, label="Avg Min Temp (°C)")

    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Average Monthly Temperatures")
    ax.set_xticks(x)
    ax.set_xticklabels(df["month"])
    ax.legend()

    st.pyplot(fig)

    # Create bar chart for precipitation and rainy days
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Precipitation (mm)', color=color)
    ax1.bar(df["month"], df["precipitation_avg"], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Rainy Days (%)', color=color)
    ax2.plot(df["month"], df["rainy_days_percentage"],
             color=color, marker='o', linestyle='-', linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.title("Average Monthly Precipitation and Rainy Days")

    st.pyplot(fig)


def display_yearly_comparison(csv_path: str) -> None:
    """
    Display yearly comparison of weather data.

    Args:
        csv_path (str): Path to the CSV file with raw weather data
    """
    try:
        df = pd.read_csv(csv_path)

        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Extract month and day
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day

        # Create month-day string for grouping
        df['month_day'] = df['date'].dt.strftime('%m-%d')

        st.markdown("### 📊 Year-by-Year Comparison")

        # Create tabs for different metrics
        tab1, tab2, tab3 = st.tabs(
            ["Max Temperature", "Min Temperature", "Precipitation"])

        with tab1:
            fig, ax = plt.subplots(figsize=(12, 6))

            for year in df['year'].unique():
                year_data = df[df['year'] == year]
                ax.plot(year_data['month_day'],
                        year_data['temperature_max'], label=str(year))

            ax.set_title("Maximum Temperature by Year")
            ax.set_xlabel("Date (Month-Day)")
            ax.set_ylabel("Temperature (°C)")
            ax.legend()

            # Improve x-axis labels
            if len(df['month_day'].unique()) > 12:
                # Show only every 5th label
                every_nth = 5
                for n, label in enumerate(ax.xaxis.get_ticklabels()):
                    if n % every_nth != 0:
                        label.set_visible(False)

            st.pyplot(fig)

        with tab2:
            fig, ax = plt.subplots(figsize=(12, 6))

            for year in df['year'].unique():
                year_data = df[df['year'] == year]
                ax.plot(year_data['month_day'],
                        year_data['temperature_min'], label=str(year))

            ax.set_title("Minimum Temperature by Year")
            ax.set_xlabel("Date (Month-Day)")
            ax.set_ylabel("Temperature (°C)")
            ax.legend()

            # Improve x-axis labels
            if len(df['month_day'].unique()) > 12:
                # Show only every 5th label
                every_nth = 5
                for n, label in enumerate(ax.xaxis.get_ticklabels()):
                    if n % every_nth != 0:
                        label.set_visible(False)

            st.pyplot(fig)

        with tab3:
            fig, ax = plt.subplots(figsize=(12, 6))

            for year in df['year'].unique():
                year_data = df[df['year'] == year]
                ax.plot(year_data['month_day'],
                        year_data['precipitation'], label=str(year))

            ax.set_title("Daily Precipitation by Year")
            ax.set_xlabel("Date (Month-Day)")
            ax.set_ylabel("Precipitation (mm)")
            ax.legend()

            # Improve x-axis labels
            if len(df['month_day'].unique()) > 12:
                # Show only every 5th label
                every_nth = 5
                for n, label in enumerate(ax.xaxis.get_ticklabels()):
                    if n % every_nth != 0:
                        label.set_visible(False)

            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error displaying yearly comparison: {str(e)}")


def display_weather_data() -> None:
    """
    Main function to display weather data in the Streamlit interface.

    This function automatically finds the latest weather data files in the weather_data directory
    and displays the data.
    """
    try:
        # Find the latest weather data files
        csv_path, json_path = find_latest_weather_files()

        if not csv_path:
            st.warning(
                "No weather data files found. Please search for flights to generate weather data.")
            return

        if not json_path:
            st.warning("Weather data JSON file not found. Using CSV data only.")
            # Try to generate JSON from CSV
            from utils.weather_data_processor import aggregate_weather_data
            try:
                weather_data = aggregate_weather_data(csv_path)
                json_path = csv_path.replace('.csv', '.json')
            except Exception as e:
                st.error(f"Error generating weather data summary: {str(e)}")
                return

        # Load the JSON data
        weather_data = load_weather_data(json_path)

        # Display the data
        display_weather_summary(weather_data)
        display_monthly_breakdown(weather_data)
        display_yearly_comparison(csv_path)

        # Add download buttons for the data
        col1, col2 = st.columns(2)

        with col1:
            with open(csv_path, 'rb') as f:
                csv_data = f.read()

            st.download_button(
                label="Download Raw Data (CSV)",
                data=csv_data,
                file_name=os.path.basename(csv_path),
                mime="text/csv"
            )

        with col2:
            with open(json_path, 'rb') as f:
                json_data = f.read()

            st.download_button(
                label="Download Aggregated Data (JSON)",
                data=json_data,
                file_name=os.path.basename(json_path),
                mime="application/json"
            )

    except Exception as e:
        st.error(f"Error displaying weather data: {str(e)}")


def clear_weather_data_directory() -> None:
    """
    Clear all files in the weather_data directory.

    This function should be called before generating new weather data to ensure
    that only the latest data is displayed.
    """
    try:
        weather_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "outputs", "weather_data")

        if os.path.exists(weather_data_dir):
            for file in os.listdir(weather_data_dir):
                file_path = os.path.join(weather_data_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"Cleaned weather data directory: {weather_data_dir}")

    except Exception as e:
        print(f"Error clearing weather data directory: {str(e)}")
