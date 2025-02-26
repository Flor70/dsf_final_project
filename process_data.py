import pandas as pd
from datetime import datetime, timezone
import pytz
import numpy as np
import datetime 

airport_timezones = {
    "JFK": "America/New_York",
    "LAX": "America/Los_Angeles",
    "ORD": "America/Chicago",
    "DFW": "America/Chicago",
    "MIA": "America/New_York",
    "ATL": "America/New_York",
    "SEA": "America/Los_Angeles",
    "DEN": "America/Denver",
    "PHX": "America/Phoenix",
}

def get_utc_offset(airport_code):
    """Returns UTC offset in hours for a given airport code."""
    tz_name = airport_timezones.get(airport_code)
    if tz_name:
        timezone_obj = pytz.timezone(tz_name)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local = now_utc.astimezone(timezone_obj) 
        utc_offset = now_local.utcoffset().total_seconds() / 3600
        return utc_offset
    return None  

def drop_duplicates(df):
    """
    Drop duplicates from a DataFrame
    """
    return df.drop_duplicates().reset_index(drop=True)

def convert_time_flights(df):
    """
    Convert time strings to proper datetime objects and calculate duration
    """    
    df['Departure Time'] = pd.to_datetime(df['Date'] + ' ' + df['Departure Time'])
    df['Arrival Time'] = pd.to_datetime(df['Date'] + ' ' + df['Arrival Time'])
    
    mask = df['Arrival Time'] < df['Departure Time']
    df.loc[mask, 'Arrival Time'] = df.loc[mask, 'Arrival Time'] + pd.Timedelta(days=1)
    
    return df


def add_time_of_day_departure(df):
    """
    Add time of day for departure
    """
    departure_hour = df['Departure Time'].apply(lambda x: x.hour)
    
    conditions = [
        (departure_hour < 6),
        (departure_hour < 12),
        (departure_hour < 18),
        (departure_hour >= 18)
    ]
    
    choices = ['Night', 'Morning', 'Afternoon', 'Evening']
    
    df['Time of Day Departure'] = np.select(conditions, choices, default='Unknown')
    
    return df

def check_day_and_type(date):
    """
    Check the day of the week and if it's a weekday or weekend  
    """
    given_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    day_name = given_date.strftime('%A')
    
    day_type = 'weekday' if given_date.weekday() < 5 else 'weekend'
    
    return day_name, day_type

def strap_dollar_signs(df, column_name):
    """
    Strap dollar signs to the price column
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")
    
    df[column_name] = df[column_name].str.replace('$', '', regex=False).astype(int)
    df = df.rename(columns={column_name: f"{column_name} ($)"})

    return df

def extract_origin_destination(df):
    """
    Extract origin and destination from the flight route
    """
    df[['Origin', 'Destination']] = df['Flight Route'].str.split(' to ', expand=True)
    df.drop(columns=['Flight Route'], inplace=True)
    return df

def date_to_datetime(df):
    """
    Convert date string to datetime object
    """
    df['Departure Date'] = pd.to_datetime(df['Departure Date'])
    return df

def split_price_metric(df, column_name):
    """
    Splits a column containing price metrics into separate columns.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")
    
    df_extracted = df[column_name].str.extractall(r'(\w+): ([\d.]+)')
    
    df_extracted = df_extracted.reset_index().pivot(index='level_0', columns=0, values=1)
    
    df_extracted.columns.name = None  
    df_extracted = df_extracted.astype(float)  
    
    df = df.drop(columns=[column_name]).join(df_extracted)
    
    return df

def add_origin_destination_from_route(flights_df, routes_df):
    """
    Extracts origin and destination from the 'Flight Route' column in routes_df 
    and adds them to every row in flights_df.
    """
    flights_df['Origin'] = routes_df.iloc[0]['Origin']
    flights_df['Destination'] = routes_df.iloc[0]['Destination']
    
    return flights_df

def duration_flights(df):
    """
    Calculate the duration of the flight
    The duration is calculated as the difference between the arrival and departure times
    plus the difference between the destination and origin UTC offsets.
    """
    df['Duration (min)'] = (df['Arrival Time'] - df['Departure Time']).dt.total_seconds() / 60 + abs(df['Destination UTC Offset'] - df['Origin UTC Offset'])
    df['Duration (hours)'] = (df['Arrival Time'] - df['Departure Time']).dt.total_seconds() / 3600 + abs(df['Destination UTC Offset'] - df['Origin UTC Offset'])
    return df


def main():
    # Load price trends data
    df_price_trends = pd.read_csv("price_trends.csv")
    df_price_trends = drop_duplicates(df_price_trends)
    df_price_trends = split_price_metric(df_price_trends, 'Price Metric')
    df_price_trends = date_to_datetime(df_price_trends)
    df_price_trends = extract_origin_destination(df_price_trends)
    print(df_price_trends)

    # Load flight data
    df_flights = pd.read_csv("flights.csv")
    df_flights = drop_duplicates(df_flights)
    df_flights = convert_time_flights(df_flights)
    df_flights = add_time_of_day_departure(df_flights)
    df_flights[['Day Name', 'Weekday or Weekend']] = df_flights['Date'].apply(lambda x: pd.Series(check_day_and_type(x)))
    df_flights = strap_dollar_signs(df_flights, column_name='Price')

    df_flights = add_origin_destination_from_route(df_flights, df_price_trends)
    df_flights['Origin UTC Offset'] = df_flights['Origin'].apply(get_utc_offset)
    df_flights['Destination UTC Offset'] = df_flights['Destination'].apply(get_utc_offset)
    df_flights = duration_flights(df_flights)
    print(df_flights)

    # Save processed data
    df_price_trends.to_csv("processed_price_trends.csv", index=False)
    df_flights.to_csv("processed_flights.csv", index=False)

if __name__ == "__main__":
    main()

