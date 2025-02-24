import requests
import pandas as pd
from datetime import datetime, timedelta
import csv
import time
import os

# FlightLabs API configuration
FLIGHTLABS_API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiZjFmY2ZlMDBmYjQ3MWNkZDA0ZTQ0ODE5MTdjMzcwMDMzZmIyYWU1MTBlNzY2ZmU2Y2VmNzBhMWFlYmRhMmNkOGZhNGU5MGQzZTEzNmI0MzMiLCJpYXQiOjE3NDA0MDgwNjMsIm5iZiI6MTc0MDQwODA2MywiZXhwIjoxNzcxOTQ0MDYzLCJzdWIiOiIyNDM4NiIsInNjb3BlcyI6W119.jGEdcsPiqHgA7crqZRZJ7bzKPaAbSAZply8toDccHIb9a8k_ewPHuq0f0d38eMgwXdHkGOEfu-j23X_gcDyhcw'
AIRPORT_URL = 'https://www.goflightlabs.com/retrieveAirport'
FLIGHTS_URL = 'https://www.goflightlabs.com/retrieveFlights'

# Amadeus API configuration
AMADEUS_API_KEY = "0ZgZJGkDTdlGQnHGewinTQZdtqLj12Jt"
AMADEUS_API_SECRET = "RQhQWfh4tZfYuTOC"
AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_API_URL = "https://test.api.amadeus.com/v1/analytics/itinerary-price-metrics"

# --- FlightLabs Functions ---
def get_airport_ids(iata_code):
    """Fetch skyId and entityId for an airport using IATA code."""
    params = {'access_key': FLIGHTLABS_API_KEY, 'query': iata_code}
    try:
        response = requests.get(AIRPORT_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        for airport in data:
            if (airport.get('navigation', {}).get('entityType') == 'AIRPORT' and 
                airport.get('skyId') == iata_code):
                return airport.get('skyId'), airport.get('entityId')
        print(f"No matching airport found for {iata_code}")
        return None, None
    except requests.RequestException as e:
        print(f"Error fetching airport data for {iata_code}: {str(e)}")
        return None, None
    except ValueError as e:
        print(f"Invalid JSON response for {iata_code}: {str(e)}")
        return None, None

def fetch_flights(origin_sky_id, dest_sky_id, origin_entity_id, dest_entity_id, depart_date, retries=3):
    """Fetch flight data from FlightLabs retrieveFlights endpoint."""
    params = {
        'access_key': FLIGHTLABS_API_KEY, 'originSkyId': origin_sky_id, 'destinationSkyId': dest_sky_id,
        'originEntityId': origin_entity_id, 'destinationEntityId': dest_entity_id, 'date': depart_date,
        'adults': 1, 'currency': 'USD'
    }
    for attempt in range(retries):
        try:
            response = requests.get(FLIGHTS_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'itineraries' in data:
                return data['itineraries']
            else:
                print(f"No flights found for {origin_sky_id} to {dest_sky_id} on {depart_date}")
                return []
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}/{retries} failed for {depart_date}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return []

def save_flights_to_csv(flights, filename='flights.csv'):
    """Save FlightLabs flight data to a CSV file and return flight details."""
    headers = ['Flight Number', 'Carrier', 'Date', 'Departure Time', 'Arrival Time', 'Price']
    file_exists = pd.io.common.file_exists(filename)
    flight_details = []
    
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        for flight in flights:
            leg = flight['legs'][0]
            segment = leg['segments'][0]
            flight_num = segment.get('flightNumber', 'N/A')
            carrier = segment.get('marketingCarrier', {}).get('name', 'N/A')
            date = leg.get('departure', 'N/A').split('T')[0]
            dep_time = leg.get('departure', 'N/A').split('T')[1] if 'T' in leg.get('departure', 'N/A') else 'N/A'
            arr_time = leg.get('arrival', 'N/A').split('T')[1] if 'T' in leg.get('arrival', 'N/A') else 'N/A'
            price_str = flight.get('price', {}).get('formatted', 'N/A')
            price = float(price_str.replace('$', '').replace(',', '')) if price_str != 'N/A' else float('inf')
            writer.writerow([flight_num, carrier, date, dep_time, arr_time, price_str])
            flight_details.append({'date': date, 'price': price})
    return flight_details

# --- Amadeus Functions ---
def get_amadeus_access_token():
    """Get access token from Amadeus API."""
    payload = {'grant_type': 'client_credentials', 'client_id': AMADEUS_API_KEY, 'client_secret': AMADEUS_API_SECRET}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(AMADEUS_TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting Amadeus access token: {e}")
        return None

def get_price_metrics(access_token, origin, destination, departure_date, currency='EUR', one_way=False):
    """Fetch price metrics from Amadeus API."""
    params = {
        'originIataCode': origin, 'destinationIataCode': destination, 'departureDate': departure_date,
        'currencyCode': currency, 'oneWay': str(one_way).lower()
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(AMADEUS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Amadeus API Error for {departure_date}: {e}")
        return None

def save_price_trends_to_csv(data, filename="price_trends.csv"):
    """Save Amadeus price metrics to a CSV file."""
    if not data or 'data' not in data or not data['data']:
        print("No price trend data to export.")
        return
    
    metrics = data['data'][0]['priceMetrics']
    currency = data['data'][0]['currencyCode']
    origin = data['data'][0]['origin']['iataCode']
    destination = data['data'][0]['destination']['iataCode']
    departure_date = data['data'][0]['departureDate']
    
    headers = ["Flight Route", "Departure Date", "Price Metric", f"Price ({currency})"]
    row = [
        f"{origin} to {destination}", departure_date,
        f"Minimum: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'MINIMUM')}, "
        f"Q1: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'FIRST')}, "
        f"Median: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'MEDIUM')}, "
        f"Q3: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'THIRD')}, "
        f"Maximum: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'MAXIMUM')}"
    ]
    
    file_exists = pd.io.common.file_exists(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow([row[0], row[1], row[2]])

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
    """Identify the 5 cheapest dates from FlightLabs data."""
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
    
    origin_iata = input("Enter origin airport IATA code (e.g., JFK): ").strip().upper()
    destination_iata = input("Enter destination airport IATA code (e.g., LAX): ").strip().upper()
    
    start_date = datetime.today()
    sample_dates = generate_sample_dates(start_date)
    print(f"\nSampling {len(sample_dates)} dates over the next 6 months...")
    
    # --- FlightLabs Section ---
    print(f"\nFetching FlightLabs airport IDs for {origin_iata} and {destination_iata}...")
    origin_sky_id, origin_entity_id = get_airport_ids(origin_iata)
    dest_sky_id, dest_entity_id = get_airport_ids(destination_iata)
    
    if not all([origin_sky_id, origin_entity_id, dest_sky_id, dest_entity_id]):
        print("Failed to retrieve FlightLabs airport IDs. Exiting.")
        return
    
    print(f"FlightLabs Origin: {origin_sky_id} ({origin_entity_id}), Destination: {dest_sky_id} ({dest_entity_id})")
    
    all_flight_details = []
    for dept_date in sample_dates:
        print(f"Fetching FlightLabs flights for {origin_iata} to {destination_iata} on {dept_date}...")
        flights = fetch_flights(origin_sky_id, dest_sky_id, origin_entity_id, dest_entity_id, dept_date)
        if flights:
            flight_details = save_flights_to_csv(flights)
            all_flight_details.extend(flight_details)
            print(f"Saved {len(flights)} FlightLabs flights for {dept_date}")
    
    if all_flight_details:
        cheapest_dates = get_cheapest_dates(all_flight_details)
        print(f"\nCheapest dates identified: {cheapest_dates}")
    else:
        print("No flight data collected. Skipping Amadeus section.")
        return
    
    # --- Amadeus Section ---
    print("\nFetching Amadeus price trends for 5 cheapest dates...")
    access_token = get_amadeus_access_token()
    if not access_token:
        print("Failed to authenticate with Amadeus API. Skipping Amadeus data.")
    else:
        for dept_date in cheapest_dates:
            print(f"Fetching Amadeus price metrics for {origin_iata} to {destination_iata} on {dept_date}...")
            price_data = get_price_metrics(access_token, origin_iata, destination_iata, dept_date)
            if price_data:
                save_price_trends_to_csv(price_data)
                print(f"Saved Amadeus price trends for {dept_date}")

if __name__ == "__main__":
    main()