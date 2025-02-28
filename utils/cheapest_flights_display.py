"""
Utility functions for displaying cheapest flights data in the Streamlit interface.
This module handles loading and formatting flight data from JSON files.
"""

import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional


def load_cheapest_flights(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load cheapest flights data from a JSON file.

    Args:
        file_path (str, optional): Path to the JSON file. If None, uses the latest file in the cheapest_flights directory.

    Returns:
        Dict[str, Any]: Dictionary containing the cheapest flights data
    """
    try:
        # If no file path provided, find the latest file
        if not file_path:
            cheapest_flights_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                "outputs", "cheapest_flights")

            if not os.path.exists(cheapest_flights_dir):
                return {"error": "No cheapest flights directory found"}

            # Get all JSON files in the directory
            json_files = [f for f in os.listdir(
                cheapest_flights_dir) if f.endswith('.json')]

            if not json_files:
                return {"error": "No cheapest flights data found"}

            # Sort by modification time (newest first)
            json_files.sort(key=lambda x: os.path.getmtime(
                os.path.join(cheapest_flights_dir, x)), reverse=True)

            # Use the latest file
            file_path = os.path.join(cheapest_flights_dir, json_files[0])

        # Load the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if the data has the expected structure
        if "cheapest_flights" not in data:
            # Try to infer structure or return error
            if isinstance(data, list) and len(data) > 0:
                # If it's a list, wrap it in a dictionary
                return {"cheapest_flights": data}
            else:
                return {"error": "Invalid data structure in flights file"}

        return data

    except Exception as e:
        return {"error": f"Error loading cheapest flights data: {str(e)}"}


def format_price(price: Any) -> str:
    """
    Format price value for display.

    Args:
        price (Any): Price value (can be string, int, float)

    Returns:
        str: Formatted price string
    """
    if isinstance(price, (int, float)):
        return f"${price:.2f}"
    elif isinstance(price, str):
        if price.startswith('$'):
            return price
        try:
            return f"${float(price):.2f}"
        except ValueError:
            return price
    return str(price)


def display_cheapest_flights_summary(flights_data: Dict[str, Any]) -> None:
    """
    Display a summary of the cheapest flights search.

    Args:
        flights_data (Dict[str, Any]): Dictionary containing the cheapest flights data
    """
    if "error" in flights_data:
        st.error(flights_data["error"])
        return

    # Check if we have flights data
    cheapest_flights = flights_data.get("cheapest_flights", [])
    if not cheapest_flights:
        st.warning("No flights found.")
        return

    # Extract search info from the first flight
    first_flight = cheapest_flights[0]

    # Extract origin and destination from airport codes
    origin_code = first_flight.get("departure_airport_code", "")
    origin_airport = first_flight.get("departure_airport", "Unknown")

    # Get destination from the last leg of the journey
    destination_code = first_flight.get("arrival_airport_code", "")
    destination_airport = first_flight.get("arrival_airport", "Unknown")

    # Get search date and timestamp
    search_date = first_flight.get("search_date", "Unknown")
    timestamp = first_flight.get(
        "search_timestamp", first_flight.get("timestamp", "Unknown"))

    # Display search summary
    st.subheader("🔍 Search Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Origin:** {origin_airport} ({origin_code})")
        st.write(
            f"**Destination:** {destination_airport} ({destination_code})")

    with col2:
        st.write(f"**Departure Date:** {search_date}")
        # Return date might not be available in this data structure
        

    # Display timestamp in a more readable format
    if timestamp and timestamp != "Unknown":
        try:
            # Check if timestamp is already formatted
            if " " in timestamp:
                formatted_timestamp = timestamp
            else:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                formatted_timestamp = dt.strftime('%d/%m/%Y %H:%M:%S')
            st.caption(f"Search performed at: {formatted_timestamp}")
        except:
            st.caption(f"Timestamp: {timestamp}")

    # Display price range if available
    if "typical_price_min" in first_flight and "typical_price_max" in first_flight:
        min_price = first_flight["typical_price_min"]
        max_price = first_flight["typical_price_max"]
        st.info(
            f"💰 Typical price range for this route: ${min_price} - ${max_price}")


def display_cheapest_flights_cards(flights_data: Dict[str, Any]) -> None:
    """
    Display the cheapest flights as cards in the Streamlit interface.

    Args:
        flights_data (Dict[str, Any]): Dictionary containing the cheapest flights data
    """
    if "error" in flights_data:
        return

    cheapest_flights = flights_data.get("cheapest_flights", [])

    if not cheapest_flights:
        st.warning("No flights found.")
        return

    st.subheader("✈️ Cheapest Flights")

    # Display price range if available
    if cheapest_flights and "typical_price_min" in cheapest_flights[0] and "typical_price_max" in cheapest_flights[0]:
        min_price = cheapest_flights[0]["typical_price_min"]
        max_price = cheapest_flights[0]["typical_price_max"]
        st.info(
            f"💰 Typical price range for this route: ${min_price} - ${max_price}")

    # Display each flight as a card
    for i, flight in enumerate(cheapest_flights):
        # Create a card-like container
        with st.container():
            st.markdown("---")

            # Flight header with airline and price
            col1, col2 = st.columns([3, 1])

            with col1:
                airline = flight.get("airline", "Unknown")
                flight_type = "✨ Best Flight" if flight.get(
                    "is_best_flight") == "Yes" else f"Flight {i+1}"
                st.markdown(f"### {flight_type}: {airline}")

            with col2:
                price = format_price(flight.get("price", "N/A"))
                price_level = flight.get("price_level", "")
                price_display = f"{price}"
                if price_level:
                    price_display += f" ({price_level})"

                st.markdown(f"### {price_display}")
                if flight.get("is_lowest_price") == "Yes":
                    st.markdown("🏆 **Lowest price!**")

            # Flight details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Departure")
                departure_time = flight.get("departure_time", "N/A")
                departure_airport = flight.get("departure_airport", "N/A")
                departure_code = flight.get("departure_airport_code", "")

                st.markdown(f"**Time:** {departure_time}")
                st.markdown(
                    f"**Airport:** {departure_airport} ({departure_code})")

            with col2:
                st.markdown("#### Arrival")
                arrival_time = flight.get("arrival_time", "N/A")
                arrival_airport = flight.get("arrival_airport", "N/A")
                arrival_code = flight.get("arrival_airport_code", "")

                st.markdown(f"**Time:** {arrival_time}")
                st.markdown(
                    f"**Airport:** {arrival_airport} ({arrival_code})")

            # Duration and layovers
            duration = flight.get("duration", "N/A")
            if duration != "N/A":
                st.markdown(f"**Duration:** {duration}")
            else:
                total_duration_minutes = flight.get(
                    "total_duration_minutes", 0)
                if total_duration_minutes:
                    hours = total_duration_minutes // 60
                    minutes = total_duration_minutes % 60
                    st.markdown(f"**Duration:** {hours}h {minutes}min")

            # Display layovers if any
            num_layovers = flight.get("num_layovers", 0)
            if num_layovers > 0:
                layovers = flight.get("layovers", [])
                if layovers:
                    st.markdown(f"**Layovers ({num_layovers}):**")
                    for layover in layovers:
                        st.markdown(f"- {layover}")
                else:
                    st.markdown(f"**Layovers:** {num_layovers}")


def display_cheapest_flights_table(flights_data: Dict[str, Any]) -> None:
    """
    Display the cheapest flights as a table in the Streamlit interface.

    Args:
        flights_data (Dict[str, Any]): Dictionary containing the cheapest flights data
    """
    if "error" in flights_data:
        return

    cheapest_flights = flights_data.get("cheapest_flights", [])

    if not cheapest_flights:
        return

    # Create a DataFrame for the table view
    table_data = []

    for flight in cheapest_flights:
        # Calculate duration if not provided
        duration = flight.get("duration", "N/A")
        if duration == "N/A" and "total_duration_minutes" in flight:
            total_minutes = flight["total_duration_minutes"]
            hours = total_minutes // 60
            minutes = total_minutes % 60
            duration = f"{hours}h {minutes}min"

        # Format price
        price = format_price(flight.get("price", "N/A"))

        # Add row to table data
        table_data.append({
            "Airline": flight.get("airline", "N/A"),
            "Price": price,
            "Duration": duration,
            "Departure": flight.get("departure_time", "N/A"),
            "Arrival": flight.get("arrival_time", "N/A"),
            "Layovers": flight.get("num_layovers", 0)
        })

    # Create DataFrame and display
    if table_data:
        df = pd.DataFrame(table_data)
        st.subheader("📊 Comparison Table")
        st.dataframe(df)


def display_cheapest_flights(file_path: Optional[str] = None) -> None:
    """
    Main function to display cheapest flights in the Streamlit interface.

    Args:
        file_path (str, optional): Path to the JSON file. If None, uses the latest file.
    """
    # Load the data
    flights_data = load_cheapest_flights(file_path)

    if "error" in flights_data:
        st.error(flights_data["error"])
        return

    # Display summary
    display_cheapest_flights_summary(flights_data)

    # Display flights as cards
    display_cheapest_flights_cards(flights_data)

    # Display flights as table for comparison
    display_cheapest_flights_table(flights_data)

    # Add download button for the data
    if file_path:
        with open(file_path, 'rb') as f:
            json_data = f.read()

        st.download_button(
            label="Download Data (JSON)",
            data=json_data,
            file_name="cheapest_flights.json",
            mime="application/json"
        )
