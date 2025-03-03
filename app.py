from utils.weather_data_processor import save_weather_data_to_csv, aggregate_weather_data
from utils.flight_data_processor import merge_weekend_flight_data, save_cheapest_flights_json
from utils.cheapest_flights_display import display_cheapest_flights
from utils.weather_display import display_weather_data, clear_weather_data_directory
from utils.integrated_view import display_integrated_dashboard
import utils.date_utils as date_utils
from flights import fetch_flights_serpapi
from components.date_selector import render_date_selector
from components.airport_selector import render_airport_selector
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys
import json
# Import Amadeus functions
from amadeus import get_amadeus_access_token, get_price_metrics, save_price_trends_to_csv, save_price_trends_to_json, clear_amadeus_data_directory

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components


# Import flight search functions

# Import date utils

# Import flight data processor

# Import weather data processor

# Set page config
st.set_page_config(
    page_title="Flight Search App",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .result-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .flight-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .flight-price {
        font-size: 22px;
        font-weight: bold;
        color: #4CAF50;
    }
    .flight-details {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }
    .flight-leg {
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
    }
    .flight-leg:last-child {
        border-bottom: none;
    }
</style>
""", unsafe_allow_html=True)


def display_flight_results(flights):
    """
    Display flight search results in a formatted way, with focus on price information.

    Args:
        flights (list): List of formatted flight dictionaries
    """
    if not flights:
        st.warning("No flights found for the selected route and dates.")
        return

    st.subheader("Flight Search Results")
    st.write(f"Found {len(flights)} flights")

    # Display price insights if available
    if flights and flights[0].get('typical_price_range'):
        typical_range = flights[0]['typical_price_range']
        st.info(
            f"💰 Typical price range for this route: ${typical_range[0]} - ${typical_range[1]}")

    # Display flights in a nice format
    for i, flight in enumerate(flights):
        # Format price display
        price_str = f"${flight.get('price', 'N/A')}"
        if flight.get('price_level'):
            price_str += f" ({flight.get('price_level', '')})"

        # Create expander title with price highlight
        expander_title = f"Flight {i+1}: {flight.get('airline', 'Unknown')} - {price_str}"
        if flight.get('is_best_flight'):
            expander_title += " ⭐"

        with st.expander(expander_title):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Departure:**")
                st.write(f"Time: {flight.get('departure_time', 'N/A')}")
                st.write(f"Airport: {flight.get('origin_airport', 'N/A')}")

            with col2:
                st.write("**Arrival:**")
                st.write(f"Time: {flight.get('arrival_time', 'N/A')}")
                st.write(
                    f"Airport: {flight.get('destination_airport', 'N/A')}")

            st.write(f"**Duration:** {flight.get('duration', 'N/A')}")

            # Display price information with more details
            st.write("**Price Information:**")
            st.write(f"Price: {price_str}")
            if flight.get('typical_price_range'):
                typical_range = flight.get('typical_price_range')
                st.write(
                    f"Typical price range: ${typical_range[0]} - ${typical_range[1]}")

            st.write(f"**Airline:** {flight.get('airline', 'N/A')}")

            if flight.get('layovers') and len(flight['layovers']) > 0:
                st.write("**Layovers:**")
                for layover in flight['layovers']:
                    st.write(f"- {layover}")


def main():
    st.title("✈️ Flight Search")

    # Initialize session state for airports if not exists
    if 'origin' not in st.session_state:
        st.session_state.origin = None
    if 'destination' not in st.session_state:
        st.session_state.destination = None

    # Create columns for airport selection
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Origin")
        origin = render_airport_selector(key="origin")

    with col2:
        st.subheader("Destination")
        destination = render_airport_selector(key="destination")

    # Date selection
    st.subheader("Travel Dates")
    col1, col2 = st.columns(2)

    with col1:
        departure_date = render_date_selector(
            "Departure Date", key="departure_date", min_date=datetime.now())

    with col2:
        return_date = render_date_selector(
            "Return Date (Optional)", key="return_date", min_date=departure_date if departure_date else datetime.now())

    # Search button
    if st.button("Search Flights"):
        if not origin or not destination:
            st.error("Please select both origin and destination airports.")
            return

        if not departure_date:
            st.error("Please select a departure date.")
            return

        if origin == destination:
            st.error("Origin and destination cannot be the same.")
            return

        # Show loading spinner while searching
        with st.spinner(f"Searching flights from {origin} to {destination}..."):
            try:
                # Get all weekends between departure and return dates
                weekends = date_utils.get_weekends_between_dates(
                    departure_date.strftime('%Y-%m-%d'),
                    return_date.strftime(
                        '%Y-%m-%d') if return_date else departure_date.strftime('%Y-%m-%d')
                )

                raw_data_dir = os.path.join("outputs", "raw_data")
                if os.path.exists(raw_data_dir):
                    for file in os.listdir(raw_data_dir):
                        file_path = os.path.join(raw_data_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    print(f"Cleaned directory: {raw_data_dir}")

                all_flights = []
                # If no weekends found, search with original dates
                if not weekends:
                    flights = fetch_flights_serpapi(
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date.strftime('%Y-%m-%d'),
                        return_date=return_date.strftime(
                            '%Y-%m-%d') if return_date else None,
                    )
                    all_flights.extend(flights)
                else:
                    # For each weekend, fetch flights
                    for weekend in weekends:
                        weekend_flights = fetch_flights_serpapi(
                            origin=origin,
                            destination=destination,
                            departure_date=weekend['departure_date'],
                            return_date=weekend['return_date'],
                        )
                        all_flights.extend(weekend_flights)

                # Process and display cheapest flights
                try:
                    # Save to file
                    cheapest_flights_dir = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), "outputs", "cheapest_flights")

                    # Ensure directory exists
                    os.makedirs(cheapest_flights_dir, exist_ok=True)

                    # Save cheapest flights data
                    save_cheapest_flights_json(
                        raw_data_dir, cheapest_flights_dir, 3)

                    display_cheapest_flights()

                    # Display weather data for destination
                    if destination:
                        # Extract destination city name from the airport code
                        destination_city = destination.split(
                            "(")[0].strip() if "(" in destination else destination

                        # Get dates for weather data
                        start_date = departure_date.strftime('%Y-%m-%d')
                        end_date = return_date.strftime(
                            '%Y-%m-%d') if return_date else departure_date.strftime('%Y-%m-%d')

                        # Clear weather data directory before generating new data
                        clear_weather_data_directory()

                        # Get weather data
                        csv_path = save_weather_data_to_csv(
                            destination_city, start_date, end_date)
                        weather_stats = aggregate_weather_data(csv_path)

                        # Display weather data using the new function
                        st.subheader(
                            "🌤️ Weather Forecast Based on Historical Data")
                        display_weather_data()

                        # Clear amadeus data directory
                        amadeus_data_dir = clear_amadeus_data_directory()

                        # Get access token
                        access_token = get_amadeus_access_token()
                        if access_token:
                            # Get price metrics for each weekend
                            all_results = []

                            # If no weekends found, use original dates
                            if not weekends:
                                departure_str = departure_date.strftime(
                                    '%Y-%m-%d')
                                data = get_price_metrics(
                                    access_token, origin, destination, departure_str)
                                if data and 'data' in data and data['data']:
                                    all_results.append(data)
                                    # Save individual date results
                                    date_filename = f"{amadeus_data_dir}/{origin}_{destination}_{departure_str}.json"
                                    save_price_trends_to_json(
                                        data, date_filename)
                                    # Save to CSV
                                    csv_filename = f"{amadeus_data_dir}/price_trends.csv"
                                    save_price_trends_to_csv(
                                        data, csv_filename)
                            else:
                                # For each weekend, get price metrics
                                for weekend in weekends:
                                    departure_str = weekend['departure_date']
                                    data = get_price_metrics(
                                        access_token, origin, destination, departure_str)
                                    if data and 'data' in data and data['data']:
                                        all_results.append(data)
                                        # Save individual date results
                                        date_filename = f"{amadeus_data_dir}/{origin}_{destination}_{departure_str}.json"
                                        save_price_trends_to_json(
                                            data, date_filename)
                                        # Save to CSV
                                        csv_filename = f"{amadeus_data_dir}/price_trends.csv"
                                        save_price_trends_to_csv(
                                            data, csv_filename)

                            # Save all results to a single JSON file
                            if all_results:
                                combined_data = {
                                    "data": [item['data'][0] for item in all_results if 'data' in item and item['data']],
                                    "meta": all_results[0].get('meta', {}) if all_results else {}
                                }

                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                combined_filename = f"{amadeus_data_dir}/{origin}_{destination}_combined_{timestamp}.json"
                                save_price_trends_to_json(
                                    combined_data, combined_filename)

                                print(
                                    f"All price trends saved to {combined_filename}")
                            else:
                                print(
                                    "No price trend data was retrieved from Amadeus API.")

                        # Display integrated dashboard with all data
                        st.subheader("🔍 Integrated Travel Analysis")
                        display_integrated_dashboard()

                except Exception as e:
                    st.warning(f"Could not process flight data: {str(e)}")

                # Save the search to history
                if 'search_history' not in st.session_state:
                    st.session_state.search_history = []

                st.session_state.search_history.append({
                    'origin': origin,
                    'destination': destination,
                    'departure_date': departure_date.strftime('%Y-%m-%d'),
                    'return_date': return_date.strftime('%Y-%m-%d') if return_date else None,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            except Exception as e:
                st.error(
                    f"An error occurred while searching for flights: {str(e)}")

    # Display search history
    if 'search_history' in st.session_state and st.session_state.search_history:
        with st.expander("Search History"):
            history_df = pd.DataFrame(st.session_state.search_history)
            st.dataframe(history_df)


if __name__ == "__main__":
    main()
