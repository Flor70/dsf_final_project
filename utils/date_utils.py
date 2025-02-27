"""
Date utility functions for the flight search application.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional


def get_weekends_between_dates(start_date: Union[str, datetime], 
                              end_date: Union[str, datetime]) -> List[Dict[str, str]]:
    """
    Calculate all weekends between two dates.
    
    A weekend is defined as starting on Friday and ending on Sunday.
    
    Args:
        start_date (str or datetime): The start date of the range
        end_date (str or datetime): The end date of the range
        
    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing:
            - 'departure_date': Friday date in 'YYYY-MM-DD' format
            - 'return_date': Sunday date in 'YYYY-MM-DD' format
    
    Example:
        >>> get_weekends_between_dates('2025-03-01', '2025-03-20')
        [
            {'departure_date': '2025-03-07', 'return_date': '2025-03-09'},
            {'departure_date': '2025-03-14', 'return_date': '2025-03-16'}
        ]
    """
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Ensure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Find the first Friday after or on the start date
    days_until_friday = (4 - start_date.weekday()) % 7
    first_friday = start_date + timedelta(days=days_until_friday)
    
    # If the first Friday is after the end date, there are no weekends in the range
    if first_friday > end_date:
        return []
    
    weekends = []
    current_friday = first_friday
    
    # Iterate through all Fridays until we pass the end date
    while current_friday <= end_date:
        # Calculate the corresponding Sunday (Friday + 2 days)
        current_sunday = current_friday + timedelta(days=2)
        
        # Only include complete weekends (if Sunday is within or on the end date)
        if current_sunday <= end_date:
            weekends.append({
                'departure_date': current_friday.strftime('%Y-%m-%d'),
                'return_date': current_sunday.strftime('%Y-%m-%d')
            })
        
        # Move to the next Friday (7 days later)
        current_friday += timedelta(days=7)
    
    return weekends


def get_long_weekends_between_dates(start_date: Union[str, datetime], 
                                   end_date: Union[str, datetime],
                                   thursday_included: bool = True,
                                   monday_included: bool = True) -> List[Dict[str, str]]:
    """
    Calculate all long weekends between two dates.
    
    A long weekend can optionally include Thursday and/or Monday.
    
    Args:
        start_date (str or datetime): The start date of the range
        end_date (str or datetime): The end date of the range
        thursday_included (bool): Whether to include Thursday in the long weekend
        monday_included (bool): Whether to include Monday in the long weekend
        
    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing:
            - 'departure_date': Thursday/Friday date in 'YYYY-MM-DD' format
            - 'return_date': Sunday/Monday date in 'YYYY-MM-DD' format
    
    Example:
        >>> get_long_weekends_between_dates('2025-03-01', '2025-03-20')
        [
            {'departure_date': '2025-03-06', 'return_date': '2025-03-10'},
            {'departure_date': '2025-03-13', 'return_date': '2025-03-17'}
        ]
    """
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Ensure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Find the first Thursday or Friday after or on the start date
    start_weekday = start_date.weekday()
    days_until_weekend_start = 0
    
    if thursday_included:
        # Find the first Thursday (3 is Thursday in Python's weekday system)
        days_until_weekend_start = (3 - start_weekday) % 7
    else:
        # Find the first Friday (4 is Friday in Python's weekday system)
        days_until_weekend_start = (4 - start_weekday) % 7
    
    first_weekend_start = start_date + timedelta(days=days_until_weekend_start)
    
    # If the first weekend start is after the end date, there are no weekends in the range
    if first_weekend_start > end_date:
        return []
    
    long_weekends = []
    current_weekend_start = first_weekend_start
    
    # Iterate through all weekend starts until we pass the end date
    while current_weekend_start <= end_date:
        # Calculate the corresponding weekend end (Sunday or Monday)
        weekend_end_offset = 3 if monday_included else 2
        current_weekend_end = current_weekend_start + timedelta(days=weekend_end_offset)
        
        # Only include complete weekends (if weekend end is within or on the end date)
        if current_weekend_end <= end_date:
            long_weekends.append({
                'departure_date': current_weekend_start.strftime('%Y-%m-%d'),
                'return_date': current_weekend_end.strftime('%Y-%m-%d')
            })
        
        # Move to the next weekend start (7 days later)
        current_weekend_start += timedelta(days=7)
    
    return long_weekends


def get_custom_duration_trips(start_date: Union[str, datetime],
                             end_date: Union[str, datetime],
                             trip_duration: int = 3,
                             interval_days: int = 7) -> List[Dict[str, str]]:
    """
    Calculate potential trips of a specific duration at regular intervals.
    
    Args:
        start_date (str or datetime): The start date of the range
        end_date (str or datetime): The end date of the range
        trip_duration (int): The duration of each trip in days
        interval_days (int): The interval between trip start dates in days
        
    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing:
            - 'departure_date': Trip start date in 'YYYY-MM-DD' format
            - 'return_date': Trip end date in 'YYYY-MM-DD' format
    
    Example:
        >>> get_custom_duration_trips('2025-03-01', '2025-03-20', trip_duration=4, interval_days=5)
        [
            {'departure_date': '2025-03-01', 'return_date': '2025-03-05'},
            {'departure_date': '2025-03-06', 'return_date': '2025-03-10'},
            {'departure_date': '2025-03-11', 'return_date': '2025-03-15'},
            {'departure_date': '2025-03-16', 'return_date': '2025-03-20'}
        ]
    """
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Ensure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Ensure trip_duration and interval_days are positive
    trip_duration = max(1, trip_duration)
    interval_days = max(1, interval_days)
    
    trips = []
    current_start = start_date
    
    # Iterate through all possible trip start dates
    while current_start <= end_date:
        # Calculate the corresponding trip end date
        current_end = current_start + timedelta(days=trip_duration)
        
        # Only include trips that end on or before the end date
        if current_end <= end_date:
            trips.append({
                'departure_date': current_start.strftime('%Y-%m-%d'),
                'return_date': current_end.strftime('%Y-%m-%d')
            })
        
        # Move to the next potential trip start date
        current_start += timedelta(days=interval_days)
    
    return trips


if __name__ == "__main__":
    start = input("Enter start date (YYYY-MM-DD): ")
    end = input("Enter end date (YYYY-MM-DD): ")
    
    print("Regular weekends:")
    weekends = get_weekends_between_dates(start, end)
    for weekend in weekends:
        print(f"Departure: {weekend['departure_date']} (Fri), Return: {weekend['return_date']} (Sun)")
    
    print("\nLong weekends (Thu-Mon):")
    long_weekends = get_long_weekends_between_dates(start, end)
    for weekend in long_weekends:
        print(f"Departure: {weekend['departure_date']} (Thu), Return: {weekend['return_date']} (Mon)")
    
    print("\n5-day trips every 10 days:")
    custom_trips = get_custom_duration_trips(start, end, trip_duration=5, interval_days=10)
    for trip in custom_trips:
        print(f"Departure: {trip['departure_date']}, Return: {trip['return_date']}")
