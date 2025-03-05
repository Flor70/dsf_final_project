# Flight Search & Weather Analysis ✈️☀️

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

A powerful Python application for searching flights and analyzing historical weather data, developed by **Ario**, **Myrthe**, and **Floriano**. This project helps travelers find the cheapest flights for their desired routes and provides historical weather information for better trip planning.

---

## Project Overview

**Flight Search & Weather Analysis** helps travelers plan their trips by:
1. Finding the cheapest flights between selected origin and destination airports
2. Automatically searching for flights on weekends between selected dates
3. Providing detailed flight information (price, airline, times, duration, layovers)
4. Displaying historical weather data for the destination city
5. Showing historical price trends for the selected route
6. Offering an integrated visualization of flight, weather, and price data

The application saves data in organized directories:
- **`outputs/raw_data/`**: Raw flight search data from SerpAPI
- **`outputs/cheapest_flights/`**: Processed data with the cheapest flights
- **`outputs/weather_data/`**: Historical weather data for destination cities
- **`outputs/amadeus_data/`**: Historical price data from the Amadeus API

---

## Features

### Flight Search
- **Customizable Routes**: Enter any origin and destination airport (IATA codes)
- **Date Selection**: Choose departure and return dates
- **Weekend Focus**: Automatically searches for flights on weekends
- **Cheapest Options**: Displays the three cheapest flights found
- **Detailed Information**: Shows price, airline, times, duration, and layovers
- **Comparison Table**: Easy-to-use table for comparing flight options

### Weather Analysis
- **Historical Data**: Retrieves weather data for the destination city
- **Temperature Statistics**: Shows average high and low temperatures
- **Precipitation Data**: Displays rainfall patterns
- **Monthly Breakdown**: Visualizes monthly weather patterns
- **Year-by-Year Comparison**: Compares weather data across years

### Price Analysis
- **Historical Trends**: Shows how prices vary over time
- **Price Metrics**: Displays minimum, median, and maximum prices for the route
- **Price Evaluation**: Assesses whether the current price is good compared to historical data
- **Amadeus Data**: Uses the Amadeus API to obtain reliable price data

### Integrated Visualization
- **Unified Dashboard**: Combines flight, weather, and price data in a single view
- **Weekend Organization**: Groups flights by weekend for easy comparison
- **Weather Summary by Weekend**: Displays weather data once per weekend
- **Historical Charts**: Shows weather trends for specific dates
- **Visual Price Assessment**: Uses color coding to indicate whether prices are good or bad

### User Interface
- **Clean Design**: Intuitive Streamlit interface
- **Responsive Layout**: Well-organized sections
- **Interactive Elements**: Enhanced user experience
- **Data Visualization**: Charts and tables for better understanding
- **Clear Instructions**: English interface with helpful labels

---

## Project Architecture

The project follows a modular architecture with the following main components:

### Main Modules
- **`app.py`**: Main entry point and Streamlit interface
- **`flights.py`**: Functions for fetching flight data from SerpAPI
- **`amadeus.py`**: Integration with the Amadeus API for historical price data

### Utilities
- **`utils/flight_data_processor.py`**: Processing and analysis of flight data
- **`utils/weather_data_processor.py`**: Retrieval and processing of weather data
- **`utils/weather_display.py`**: Utility for clearing the weather data directory
- **`utils/integrated_view.py`**: Integrated dashboard combining all data

### Components
- **`components/airport_selector.py`**: Custom component for selecting airports with search functionality
- **`components/date_selector.py`**: Custom component for selecting dates with validation and range constraints

### Documentation and Data
- **`docs/airports.csv`**: Database of airports with IATA codes, names, locations, and other metadata

### Data Flow
1. The user enters search parameters (origin, destination, dates)
2. The application searches for flights using SerpAPI
3. Flight data is processed to find the cheapest flights
4. Historical weather data is retrieved for the destination
5. Historical price data is obtained from the Amadeus API
6. All data is combined in an integrated visualization

---

## Technical Details

### APIs Used
- **SerpAPI**: For fetching flight data from various sources
- **Open-Meteo**: For historical weather data
- **Amadeus**: For historical price trends

### Data Processing
- **Pandas**: Extensively used for data manipulation and analysis
- **Matplotlib/Seaborn**: For data visualizations
- **JSON/CSV**: For data storage and exchange

### Visualization
- **Streamlit**: Main framework for the user interface
- **Custom Components**: Cards, tables, and charts for data display
- **Responsive Layout**: Adaptable to different screen sizes

---

## Prerequisites

- **Python 3.8+**
- **Dependencies**: Install via `pip install -r requirements.txt`
- **API Keys**:
  - **SerpAPI**: Get your key at [serpapi.com](https://serpapi.com)
  - **Amadeus**: Register at [developers.amadeus.com](https://developers.amadeus.com)

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Flor70/dsf_final_project.git
   cd dsf_final_project
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     SERPAPI_KEY=your_serpapi_key
     AMADEUS_API_KEY=your_amadeus_key
     AMADEUS_API_SECRET=your_amadeus_secret
     ```

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```


## Contributors

- **Ario**
- **Myrthe**
- **Floriano**

---
