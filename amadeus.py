# Import necessary libraries
import requests
import csv
import os
import json
from datetime import datetime, timedelta

# Amadeus API configuration
AMADEUS_API_KEY = "0ZgZJGkDTdlGQnHGewinTQZdtqLj12Jt"
AMADEUS_API_SECRET = "RQhQWfh4tZfYuTOC"
AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_API_URL = "https://test.api.amadeus.com/v1/analytics/itinerary-price-metrics"

# --- Amadeus Functions ---


def get_amadeus_access_token():
    """Get access token from Amadeus API."""
    payload = {'grant_type': 'client_credentials',
               'client_id': AMADEUS_API_KEY, 'client_secret': AMADEUS_API_SECRET}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(
            AMADEUS_TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting Amadeus access token: {e}")
        return None


def get_price_metrics(access_token, origin, destination, departure_date, currency='USD', one_way=False):
    """Fetch price metrics from Amadeus API."""
    params = {
        'originIataCode': origin, 'destinationIataCode': destination, 'departureDate': departure_date,
        'currencyCode': currency, 'oneWay': str(one_way).lower()
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(
            AMADEUS_API_URL, headers=headers, params=params)
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

    headers = ["Flight Route", "Departure Date",
               "Price Metric", f"Price ({currency})"]
    row = [
        f"{origin} to {destination}", departure_date,
        f"Minimum: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'MINIMUM')}, "
        f"Q1: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'FIRST')}, "
        f"Median: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'MEDIUM')}, "
        f"Q3: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'THIRD')}, "
        f"Maximum: {next(m['amount'] for m in metrics if m['quartileRanking'] == 'MAXIMUM')}"
    ]

    file_exists = os.path.exists(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow([row[0], row[1], row[2]])


def save_price_trends_to_json(data, filename="price_trends.json"):
    """Save Amadeus price metrics to a JSON file."""
    if not data or 'data' not in data or not data['data']:
        print("No price trend data to export.")
        return

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename) if os.path.dirname(
        filename) else '.', exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(f"Price trends saved to {filename}")
    return filename


def get_price_trends_for_dates(origin, destination, dates, currency='EUR'):
    """Get price trends for multiple dates."""
    access_token = get_amadeus_access_token()
    if not access_token:
        print("Failed to get Amadeus access token.")
        return []

    results = []
    for date in dates:
        print(f"Fetching price metrics for {date}...")
        data = get_price_metrics(access_token, origin,
                                 destination, date, currency)
        if data and 'data' in data and data['data']:
            results.append(data)
        else:
            print(f"No data available for {date}")

    return results

def clear_amadeus_data_directory():
    """Clear all files in the amadeus_data directory."""
    amadeus_data_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "outputs", "amadeus_data")

    # Create directory if it doesn't exist
    os.makedirs(amadeus_data_dir, exist_ok=True)

    # Remove all files in the directory
    for file in os.listdir(amadeus_data_dir):
        file_path = os.path.join(amadeus_data_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    print(f"Cleaned directory: {amadeus_data_dir}")
    return amadeus_data_dir

def main():
    """Test the Amadeus API functionality."""
    print("Amadeus API Test")
    print("--------------")

    # Get user input
    origin = input("Enter origin airport code (e.g., BCN): ").strip().upper()
    destination = input(
        "Enter destination airport code (e.g., MAD): ").strip().upper()

    # Generate dates for the next 3 months (one date per month)
    today = datetime.now()
    dates = [(today + timedelta(days=30*i)).strftime("%Y-%m-%d")
             for i in range(1, 4)]

    print(
        f"\nFetching price trends for {origin} to {destination} on dates: {', '.join(dates)}")

    # Get access token
    access_token = get_amadeus_access_token()
    if not access_token:
        print("Failed to get access token. Check your API credentials.")
        return

    print("Access token obtained successfully.")

    # Create output directory
    output_dir = "outputs/amadeus_data"
    os.makedirs(output_dir, exist_ok=True)

    # Get price metrics for each date
    all_results = []
    for date in dates:
        print(f"\nFetching price metrics for {date}...")
        data = get_price_metrics(access_token, origin, destination, date)

        if data and 'data' in data and data['data']:
            print("Data received successfully.")
            all_results.append(data)

            # Save individual date results
            date_filename = f"{output_dir}/{origin}_{destination}_{date}.json"
            with open(date_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"Price trends saved to {date_filename}")

            # Save to CSV
            csv_filename = f"{output_dir}/price_trends.csv"
            save_price_trends_to_csv(data, csv_filename)
            print(f"Price trends saved to {csv_filename}")
        else:
            print(f"No data available for {date}")

    # Save all results to a single JSON file
    if all_results:
        combined_data = {
            "data": [item['data'][0] for item in all_results if 'data' in item and item['data']],
            "meta": all_results[0].get('meta', {}) if all_results else {}
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"{output_dir}/{origin}_{destination}_combined_{timestamp}.json"
        with open(combined_filename, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=4)
        print(f"\nAll price trends saved to {combined_filename}")
    else:
        print("\nNo price trend data was retrieved.")


if __name__ == "__main__":
    main()
