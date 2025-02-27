# Flight Search Interface with Streamlit

This application provides a user interface for flight search, built with Streamlit.

## Features

- **Airport Selection**: Autocomplete dropdowns for origin and destination airports
- **Date Selection**: Date selectors for departure and return flights
- **Input Validation**: Verification of valid airports and consistent dates

## Project Structure

```
DSF_flight/
├── app.py                  # Main Streamlit application
├── components/             # Reusable interface components
│   ├── __init__.py
│   ├── airport_selector.py # Airport selection component
│   └── date_selector.py    # Date selection component
├── utils/                  # Utilities and helper functions
│   ├── __init__.py
│   └── data_loader.py      # Data loading functions
└── docs/                   # Data files
    └── airports.csv        # Airport database
```

## How to Run

1. Make sure you have Streamlit installed:
   ```
   pip install streamlit pandas
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

## Components

### AirportSelector

Component for airport selection with autocomplete functionality:
- Allows searching by IATA code, airport name, city, or country
- Dynamically filters results as the user types
- Displays detailed information for each airport

### DateSelector

Component for date selection:
- Allows selecting dates within a valid range
- Implements validations to ensure the return date is after the departure date
- Offers default dates to facilitate selection

## Next Steps

- Integration with flight search APIs
- Display of available flight results
- Additional filters (price, time, airlines)
- Price trend visualizations
