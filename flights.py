import requests
import pandas as pd
from datetime import datetime, timedelta
import csv
import time
import os
import json
from serpapi.google_search import GoogleSearch


# SerpAPI Google Flights configuration
SERPAPI_KEY = "941677836c67bebee8d9f3d0c2e43fe2644374fd67e6db64b6d0bf8b80c10b3f"
SERPAPI_BASE_URL = "https://serpapi.com/search"


# --- SerpAPI Google Flights Functions ---
def fetch_flights_serpapi(origin, destination, departure_date, return_date=None, currency="USD", locale="en"):
    """
    Fetch flight data from SerpAPI Google Flights.

    Args:
        origin (str): Origin airport code (IATA)
        destination (str): Destination airport code (IATA)
        departure_date (str): Departure date in YYYY-MM-DD format
        return_date (str, optional): Return date in YYYY-MM-DD format. Defaults to None.
        currency (str, optional): Currency code. Defaults to "USD".
        locale (str, optional): Locale code. Defaults to "en".
        save_raw_data (bool, optional): Whether to save raw API response to CSV. Defaults to False.

    Returns:
        list: Formatted flight data
    """
    try:
        # Prepare SerpAPI parameters
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "currency": currency,
            "hl": locale,
            "api_key": SERPAPI_KEY
        }

        # Add return date if provided
        if return_date:
            params["return_date"] = return_date

        # Make API request
        search = GoogleSearch(params)
        results = search.get_dict()

        csv_filename = f"serpapi_raw_{origin}_{destination}_{departure_date}.csv"
        save_serpapi_response_to_csv(results, csv_filename)

        # Format results
        formatted_flights = format_serpapi_results(results)
        return formatted_flights

    except Exception as e:
        print(f"Error fetching flights from SerpAPI: {str(e)}")
        return []


def format_serpapi_results(serpapi_data):
    """
    Format flight search results from SerpAPI Google Flights into a standardized format,
    focusing on price information.

    Args:
        serpapi_data (dict): Raw API response from SerpAPI

    Returns:
        list: List of formatted flight dictionaries with price focus
    """
    formatted_flights = []

    # Check if we have valid data
    if not serpapi_data or "error" in serpapi_data:
        print(
            f"Error in SerpAPI response: {serpapi_data.get('error', 'Unknown error')}")
        return []

    # Extract price insights if available
    price_insights = serpapi_data.get("price_insights", {})
    lowest_price = price_insights.get("lowest_price")
    price_level = price_insights.get("price_level")
    typical_price_range = price_insights.get("typical_price_range", [])

    # Process best flights first
    best_flights = serpapi_data.get("best_flights", [])
    if best_flights:
        for flight in best_flights:
            # Extract basic flight information
            airline = flight.get('airline', 'Unknown')
            price = flight.get('price', 'N/A')
            total_duration = flight.get('total_duration', 0)

            # Format duration in hours and minutes
            duration_formatted = f"{total_duration // 60}h {total_duration % 60}m" if total_duration else 'N/A'

            # Extract departure and arrival information from the first flight segment
            flight_segments = flight.get('flights', [])
            if flight_segments:
                first_segment = flight_segments[0]
                departure_airport = first_segment.get('departure_airport', {})
                arrival_airport = first_segment.get('arrival_airport', {})

                # Extract departure and arrival times
                departure_time = departure_airport.get('time', 'N/A')
                arrival_time = arrival_airport.get('time', 'N/A')

                # Extract airport names and codes
                origin_airport = f"{departure_airport.get('name', 'N/A')} ({departure_airport.get('id', 'N/A')})"
                destination_airport = f"{arrival_airport.get('name', 'N/A')} ({arrival_airport.get('id', 'N/A')})"
            else:
                departure_time = 'N/A'
                arrival_time = 'N/A'
                origin_airport = 'N/A'
                destination_airport = 'N/A'

            # Extract layover information
            layovers = []
            for layover in flight.get('layovers', []):
                layover_info = f"{layover.get('name', 'Unknown')} ({layover.get('id', 'N/A')}) - {layover.get('duration', 0) // 60}h {layover.get('duration', 0) % 60}m"
                layovers.append(layover_info)

            # Create formatted flight entry with price focus
            formatted_flight = {
                'airline': airline,
                'price': price,
                'price_level': price_level if price == lowest_price else None,
                'typical_price_range': typical_price_range if typical_price_range else None,
                'duration': duration_formatted,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'origin_airport': origin_airport,
                'destination_airport': destination_airport,
                'layovers': layovers,
                'is_best_flight': True
            }

            formatted_flights.append(formatted_flight)

    # Process other flights if available
    other_flights = serpapi_data.get('other_flights', [])
    for flight in other_flights:
        # Extract basic flight information
        airline = flight.get('airline', 'Unknown')
        price = flight.get('price', 'N/A')
        total_duration = flight.get('total_duration', 0)

        # Format duration in hours and minutes
        duration_formatted = f"{total_duration // 60}h {total_duration % 60}m" if total_duration else 'N/A'

        # Extract departure and arrival information from the first flight segment
        flight_segments = flight.get('flights', [])
        if flight_segments:
            first_segment = flight_segments[0]
            departure_airport = first_segment.get('departure_airport', {})
            arrival_airport = first_segment.get('arrival_airport', {})

            # Extract departure and arrival times
            departure_time = departure_airport.get('time', 'N/A')
            arrival_time = arrival_airport.get('time', 'N/A')

            # Extract airport names and codes
            origin_airport = f"{departure_airport.get('name', 'N/A')} ({departure_airport.get('id', 'N/A')})"
            destination_airport = f"{arrival_airport.get('name', 'N/A')} ({arrival_airport.get('id', 'N/A')})"
        else:
            departure_time = 'N/A'
            arrival_time = 'N/A'
            origin_airport = 'N/A'
            destination_airport = 'N/A'

        # Extract layover information
        layovers = []
        for layover in flight.get('layovers', []):
            layover_info = f"{layover.get('name', 'Unknown')} ({layover.get('id', 'N/A')}) - {layover.get('duration', 0) // 60}h {layover.get('duration', 0) % 60}m"
            layovers.append(layover_info)

        # Create formatted flight entry with price focus
        formatted_flight = {
            'airline': airline,
            'price': price,
            'price_level': price_level if price == lowest_price else None,
            'typical_price_range': typical_price_range if typical_price_range else None,
            'duration': duration_formatted,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'origin_airport': origin_airport,
            'destination_airport': destination_airport,
            'layovers': layovers,
            'is_best_flight': False
        }

        formatted_flights.append(formatted_flight)

    # Sort flights by price (lowest first)
    formatted_flights.sort(key=lambda x: float(str(x['price']).replace('$', '').replace(',', '')) if isinstance(
        x['price'], (int, float, str)) and str(x['price']).replace('$', '').replace(',', '').isdigit() else float('inf'))

    return formatted_flights


def save_serpapi_flights_to_csv(flights, filename="serpapi_flights.csv"):
    """
    Save SerpAPI flight data to a CSV file and return flight details.

    Args:
        flights (list): List of formatted flight dictionaries from SerpAPI
        filename (str, optional): Output filename. Defaults to "serpapi_flights.csv".

    Returns:
        list: List of flight details (airline, price, date)
    """
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "outputs", "raw_data")
    os.makedirs(output_dir, exist_ok=True)

    # Create full file path
    file_path = os.path.join(output_dir, filename)

    headers = ['Airline', 'Price', 'Duration', 'Departure Date', 'Departure Time',
               'Arrival Date', 'Arrival Time', 'Origin Airport', 'Destination Airport', 'Layovers']

    file_exists = os.path.exists(file_path)
    flight_details = []

    with open(file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)

        for flight in flights:
            # Extract price as a numeric value
            price_str = flight.get('price', 'N/A')
            if price_str != 'N/A':
                try:
                    price = float(price_str.replace('$', '').replace(',', ''))
                except ValueError:
                    price = float('inf')
            else:
                price = float('inf')

            # Format layovers as a single string
            layovers = ', '.join(flight.get('layovers', []))

            # Write flight data to CSV
            writer.writerow([
                flight.get('airline', 'Unknown'),
                price_str,
                flight.get('duration', 'N/A'),
                flight.get('departure_date', 'N/A'),
                flight.get('departure_time', 'N/A'),
                flight.get('arrival_date', 'N/A'),
                flight.get('arrival_time', 'N/A'),
                flight.get('origin_airport', 'N/A'),
                flight.get('destination_airport', 'N/A'),
                layovers
            ])

            # Add to flight details for return
            flight_details.append({
                'airline': flight.get('airline', 'Unknown'),
                'price': price,
                'date': flight.get('departure_date', 'N/A')
            })

    return flight_details


def save_serpapi_response_to_csv(serpapi_data, filename="serpapi_raw_response.csv"):
    """
    Save the raw SerpAPI response data to a CSV file for further analysis.
    Focus on price and flight details for comparison.

    Args:
        serpapi_data (dict): Raw API response from SerpAPI
        filename (str, optional): Output filename. Defaults to "serpapi_raw_response.csv".

    Returns:
        str: Path to the saved CSV file
    """
    if not serpapi_data:
        print("No data to save")
        return None

    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "outputs", "raw_data")
    os.makedirs(output_dir, exist_ok=True)

    # Create full file path
    file_path = os.path.join(output_dir, filename)

    # Prepare data for CSV
    rows = []

    # Extract price insights if available
    price_insights = serpapi_data.get("price_insights", {})
    lowest_price = price_insights.get("lowest_price")
    price_level = price_insights.get("price_level")
    typical_price_range = price_insights.get("typical_price_range", [])

    # Process best flights
    best_flights = serpapi_data.get("best_flights", [])
    for flight in best_flights:
        # Get airline from first flight segment if available
        airline = "Unknown"
        flight_segments = flight.get('flights', [])
        if flight_segments and len(flight_segments) > 0:
            airline = flight_segments[0].get('airline', 'Unknown')

        row = {
            'flight_type': 'best_flight',
            'airline': airline,
            'price': flight.get('price', 'N/A'),
            'is_lowest_price': 'Yes' if flight.get('price') == lowest_price else 'No',
            'price_level': price_level if flight.get('price') == lowest_price else 'N/A',
            'typical_price_min': typical_price_range[0] if typical_price_range else 'N/A',
            'typical_price_max': typical_price_range[1] if typical_price_range else 'N/A',
            'total_duration_minutes': flight.get('total_duration', 0),
            'num_layovers': len(flight.get('layovers', [])),
            'booking_token': flight.get('booking_token', 'N/A'),
            'departure_token': flight.get('departure_token', 'N/A'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Add flight segments info
        flight_segments = flight.get('flights', [])
        if flight_segments:
            first_segment = flight_segments[0]
            departure_airport = first_segment.get('departure_airport', {})
            arrival_airport = first_segment.get('arrival_airport', {})

            row.update({
                'departure_airport': departure_airport.get('name', 'N/A'),
                'departure_airport_code': departure_airport.get('id', 'N/A'),
                'departure_time': departure_airport.get('time', 'N/A'),
                'arrival_airport': arrival_airport.get('name', 'N/A'),
                'arrival_airport_code': arrival_airport.get('id', 'N/A'),
                'arrival_time': arrival_airport.get('time', 'N/A')
            })

        rows.append(row)

    # Process other flights
    other_flights = serpapi_data.get("other_flights", [])
    for flight in other_flights:
        # Get airline from first flight segment if available
        airline = "Unknown"
        flight_segments = flight.get('flights', [])
        if flight_segments and len(flight_segments) > 0:
            airline = flight_segments[0].get('airline', 'Unknown')

        row = {
            'flight_type': 'other_flight',
            'airline': airline,
            'price': flight.get('price', 'N/A'),
            'is_lowest_price': 'Yes' if flight.get('price') == lowest_price else 'No',
            'price_level': price_level if flight.get('price') == lowest_price else 'N/A',
            'typical_price_min': typical_price_range[0] if typical_price_range else 'N/A',
            'typical_price_max': typical_price_range[1] if typical_price_range else 'N/A',
            'total_duration_minutes': flight.get('total_duration', 0),
            'num_layovers': len(flight.get('layovers', [])),
            'booking_token': flight.get('booking_token', 'N/A'),
            'departure_token': flight.get('departure_token', 'N/A'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Add flight segments info
        flight_segments = flight.get('flights', [])
        if flight_segments:
            first_segment = flight_segments[0]
            departure_airport = first_segment.get('departure_airport', {})
            arrival_airport = first_segment.get('arrival_airport', {})

            row.update({
                'departure_airport': departure_airport.get('name', 'N/A'),
                'departure_airport_code': departure_airport.get('id', 'N/A'),
                'departure_time': departure_airport.get('time', 'N/A'),
                'arrival_airport': arrival_airport.get('name', 'N/A'),
                'arrival_airport_code': arrival_airport.get('id', 'N/A'),
                'arrival_time': arrival_airport.get('time', 'N/A')
            })

        rows.append(row)

    # Create DataFrame and save to CSV
    try:
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False)
        print(f"Saved {len(rows)} flights to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")
        return None

# --- Main Flight Search Functions ---


def search_flights(origin, destination, departure_date, return_date=None):
    """
    Search for flights using SerpAPI Google Flights.

    Args:
        origin (str): IATA code of origin airport
        destination (str): IATA code of destination airport
        departure_date (str or datetime): Departure date
        return_date (str or datetime, optional): Return date for round trips

    Returns:
        dict: Raw API response with flight data
    """
    print(f"Searching flights from {origin} to {destination}")

    return fetch_flights_serpapi(origin, destination, departure_date, return_date)


def format_flight_results(api_response):
    """
    Format flight search results from SerpAPI into a standardized format.

    Args:
        api_response (dict): Raw API response

    Returns:
        list: List of formatted flight dictionaries
    """
    # Always use SerpAPI formatting
    return format_serpapi_results(api_response)


def fetch_flights(origin_code, dest_code, depart_date, return_date=None):
    """
    Fetch flight data and return formatted results using SerpAPI.

    Args:
        origin_code (str): IATA code of origin airport
        dest_code (str): IATA code of destination airport
        depart_date (str or datetime): Departure date
        return_date (str or datetime, optional): Return date for round trips

    Returns:
        list: List of formatted flight dictionaries
    """
    # Search for flights using SerpAPI
    api_response = search_flights(
        origin_code, dest_code, depart_date, return_date)

    # Format the results
    formatted_flights = format_flight_results(api_response)

    return formatted_flights

# --- Date Sampling and Cheapest Flights ---


def generate_sample_dates(start_date, months=6, samples_per_month=8):
    """Generate 8 sample dates per month for the next 6 months."""
    dates = []
    current_date = start_date
    for _ in range(months):
        year = current_date.year
        month = current_date.month
        next_month = current_date.replace(day=28) + timedelta(days=4)
        last_day = (next_month - timedelta(days=next_month.day)).day
        sample_days = [4, 8, 12, 16, 20, 24, 28, last_day]
        for day in sample_days:
            if day <= last_day:
                sample_date = datetime(year, month, day)
                if sample_date >= start_date:
                    dates.append(sample_date.strftime('%Y-%m-%d'))
        current_date = current_date.replace(day=1) + timedelta(days=32)
        current_date = current_date.replace(day=1)
    return dates


def get_cheapest_dates(flight_details, num_dates=5):
    """Identify the 5 cheapest dates from flight data."""
    date_prices = {}
    for detail in flight_details:
        date = detail['date']
        price = detail['price']
        if date not in date_prices or price < date_prices[date]:
            date_prices[date] = price
    sorted_dates = sorted(date_prices.items(), key=lambda x: x[1])
    return [date for date, _ in sorted_dates[:num_dates]]

# --- Main Function ---


def main():
    """Main function to scrape flights and price trends for cheapest dates."""
    print("Flight Scraper and Price Trends Checker Starting...")
    print("=" * 50)

    origin_iata = input(
        "Enter origin airport IATA code (e.g., JFK): ").strip().upper()
    destination_iata = input(
        "Enter destination airport IATA code (e.g., LAX): ").strip().upper()

    start_date = datetime.today()
    sample_dates = generate_sample_dates(start_date)

    print(
        f"Fetching flights from {origin_iata} to {destination_iata} for {len(sample_dates)} sample dates...")

    all_flight_details = []
    all_flights = []

    for dept_date in sample_dates:
        print(
            f"Fetching flights for {origin_iata} to {destination_iata} on {dept_date}...")
        flights = fetch_flights(origin_iata, destination_iata, dept_date)
        if flights:
            # Save raw response to CSV
            save_serpapi_response_to_csv(
                flights,
                filename=f"serpapi_raw_{origin_iata}_{destination_iata}_{dept_date}.csv"
            )

            # Save formatted flights to CSV and get details
            flight_details = save_serpapi_flights_to_csv(
                flights,
                filename=f"serpapi_flights_{origin_iata}_{destination_iata}_{dept_date}.csv"
            )

            all_flight_details.extend(flight_details)
            all_flights.extend(flights)

    # Get cheapest dates
    cheapest_dates = get_cheapest_dates(all_flight_details)

    if cheapest_dates and all_flights:
        print("\nSaving the 3 cheapest flights...")

        # Filter flights for the cheapest dates
        cheapest_flights = [flight for flight in all_flights
                            if any(date in flight.get('departure_date', '') for date in cheapest_dates)]

        # Save cheapest flights to JSON
        save_cheapest_flights_to_json(
            cheapest_flights,
            origin_iata,
            destination_iata,
            start_date.strftime('%Y-%m-%d')
        )

    print("\nDone! Check the outputs directory for results.")


def save_cheapest_flights_to_json(flights, origin, destination, departure_date, return_date=None, num_flights=3):
    """
    Save the cheapest flights to a JSON file in the cheapest_flights directory.

    Args:
        flights (list): List of formatted flight dictionaries
        origin (str): Origin airport code
        destination (str): Destination airport code
        departure_date (str): Departure date in YYYY-MM-DD format
        return_date (str, optional): Return date in YYYY-MM-DD format
        num_flights (int, optional): Number of cheapest flights to save. Defaults to 3.

    Returns:
        str: Path to the saved JSON file
    """
    if not flights:
        print("No flights to save")
        return None

    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "outputs", "cheapest_flights")
    os.makedirs(output_dir, exist_ok=True)

    # Sort flights by price
    sorted_flights = sorted(flights, key=lambda x: float(str(x.get('price', 'inf')).replace('$', '').replace(',', ''))
                            if isinstance(x.get('price'), (str)) and str(x.get('price', 'inf')).replace('$', '').replace(',', '').replace('.', '', 1).isdigit()
                            else float('inf'))

    # Get the cheapest flights
    cheapest_flights = sorted_flights[:num_flights]

    # Create timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create filename
    if return_date:
        filename = f"cheapest_flights_{origin}_{destination}_{departure_date}_to_{return_date}_{timestamp}.json"
    else:
        filename = f"cheapest_flights_{origin}_{destination}_{departure_date}_{timestamp}.json"

    # Create full file path
    file_path = os.path.join(output_dir, filename)

    # Create JSON data structure
    json_data = {
        "search_info": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "timestamp": timestamp
        },
        "cheapest_flights": []
    }

    # Add flight details
    for flight in cheapest_flights:
        flight_data = {
            "airline": flight.get('airline', 'Unknown'),
            "price": flight.get('price', 'N/A'),
            "duration": flight.get('duration', 'N/A'),
            "departure_time": flight.get('departure_time', 'N/A'),
            "arrival_time": flight.get('arrival_time', 'N/A'),
            "origin_airport": flight.get('origin_airport', 'N/A'),
            "destination_airport": flight.get('destination_airport', 'N/A'),
            "layovers": flight.get('layovers', []),
            "is_best_flight": flight.get('is_best_flight', False)
        }

        json_data["cheapest_flights"].append(flight_data)

    # Save to JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(cheapest_flights)} cheapest flights to {file_path}")

        # Also save a copy with a fixed name for easy access
        fixed_name_path = os.path.join(output_dir, "cheapest_flights.json")
        with open(fixed_name_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return file_path
    except Exception as e:
        print(f"Error saving cheapest flights to JSON: {str(e)}")
        return None


if __name__ == "__main__":
    main()
