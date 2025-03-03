"""
Weather Display Module

This module provides functions to clear the weather data directory.
It is used by app.py to ensure that only the latest weather data is present.
"""

import os
import streamlit as st


def clear_weather_data_directory() -> None:
    """
    Clear all files in the weather_data directory.
    This ensures that only the latest search results are present.
    """
    try:
        # Get the weather_data directory path
        weather_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "outputs", "weather_data")

        # Create directory if it doesn't exist
        if not os.path.exists(weather_data_dir):
            os.makedirs(weather_data_dir)
            return

        # Remove all files in the directory
        for file in os.listdir(weather_data_dir):
            file_path = os.path.join(weather_data_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        print(f"Cleared weather data directory: {weather_data_dir}")
    except Exception as e:
        print(f"Error clearing weather data directory: {str(e)}")
