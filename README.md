# Flight Search & Weather Analysis ✈️☀️

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

A powerful Python application to search for flights and analyze historical weather data, built by **Ario**, **Myrthe**, and **Floriano**. This project helps travelers find the cheapest flights for their desired routes and provides historical weather information for better trip planning.

---

## Project Overview

**Flight Search & Weather Analysis** helps travelers plan their trips by:
1. Finding the cheapest flights between selected origin and destination airports
2. Automatically searching for flights on weekends between selected dates
3. Providing detailed flight information (price, airline, times, duration, layovers)
4. Displaying historical weather data for the destination city
5. Offering downloadable data for further analysis

The application saves data in organized directories:
- **`outputs/raw_data/`**: Raw flight search data from SerpAPI
- **`outputs/cheapest_flights/`**: Processed data with the cheapest flights
- **`outputs/weather_data/`**: Historical weather data for destination cities

---

## Features

### Flight Search
- **Customizable Routes**: Input any origin and destination airport (IATA codes)
- **Date Selection**: Choose departure and return dates
- **Weekend Focus**: Automatically searches for flights on weekends
- **Cheapest Options**: Displays the three cheapest flights found
- **Detailed Information**: Shows price, airline, times, duration, and layovers
- **Comparison Table**: Easy-to-use table for comparing flight options
- **Search History**: Tracks previous searches

### Weather Analysis
- **Historical Data**: Retrieves weather data for the destination city
- **Temperature Statistics**: Shows average high and low temperatures
- **Precipitation Data**: Displays rainfall patterns
- **Monthly Breakdown**: Visualizes monthly weather patterns
- **Year-by-Year Comparison**: Compares weather data across years
- **Downloadable Data**: Offers raw and aggregated weather data for download

### User Interface
- **Clean Design**: Intuitive Streamlit interface
- **Responsive Layout**: Well-organized sections
- **Interactive Elements**: Enhanced user experience
- **Data Visualization**: Charts and graphs for better understanding
- **Clear Instructions**: English interface with helpful labels

---

## Prerequisites

- **Python 3.8+**
- **Dependencies**: Install via `pip install -r requirements.txt`
- **API Keys**:
  - **SerpAPI**: Get your key from [serpapi.com](https://serpapi.com)
  - **Weather API**: Register at [weatherapi.com](https://www.weatherapi.com)
  - **Amadeus** (optional): Register at [developers.amadeus.com](https://developers.amadeus.com)

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

3. **Set Up API Keys**:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     SERPAPI_KEY=your_serpapi_key
     WEATHER_API_KEY=your_weather_api_key
     AMADEUS_API_KEY=your_amadeus_key
     AMADEUS_API_SECRET=your_amadeus_secret
     ```

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

---

## Recent Updates

- **Weather Data Integration**: Added historical weather data for destination cities
- **Enhanced UI**: Improved result display with better formatting and details
- **Cheapest Flights Display**: New visualization for the cheapest flight options
- **Modular Architecture**: Refactored code for easier maintenance
- **Data Export**: Added options to download flight and weather data

---

## Pending Improvements

As detailed in our [Project Status](project_status.md) document, we're working on:

1. **Enhanced Weather Data Visualization**: Improving charts and adding weekend-specific weather information
2. **Flight Search API Integration**: Ensuring proper round-trip flight data retrieval
3. **Amadeus API Integration**: Implementing historical price trends display
4. **Additional Enhancements**: Better error handling, caching, and more filtering options

---

## Contributors

- **Ario**
- **Myrthe**
- **Floriano**

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
