# Amadeus API configuration
AMADEUS_API_KEY = "0ZgZJGkDTdlGQnHGewinTQZdtqLj12Jt"
AMADEUS_API_SECRET = "RQhQWfh4tZfYuTOC"
AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_API_URL = "https://test.api.amadeus.com/v1/analytics/itinerary-price-metrics"

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
