# Flight Price Trends ✈️

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

A powerful Python tool to scrape and analyze flight prices, built by **Ario**, **Myrthe**, and **Floriano**. This project fetches flight data and price trends for user-specified routes over a 6-month period, leveraging the **FlightLabs** and **Amadeus** APIs.

---

## Project Overview

**Flight Price Scraper** helps travelers and analysts explore flight pricing trends by:
1. Collecting detailed flight information (flight number, carrier, date, times, price) from FlightLabs for 48 sample dates across 6 months.
2. Identifying the 5 cheapest travel dates based on FlightLabs data.
3. Fetching price trend statistics (minimum, Q1, median, Q3, maximum) from Amadeus for those 5 dates.

The results are saved in two CSV files:
- **`flights.csv`**: All FlightLabs flight data.
- **`price_trends.csv`**: Amadeus price trends for the 5 cheapest dates.

---

## Features

- **Customizable Routes**: Input any origin and destination airport (IATA codes).
- **Comprehensive Date Sampling**: Analyzes 8 dates per month (early, mid, late) for 6 months.
- **Cost Optimization**: Highlights the 5 cheapest travel dates.
- **Price Trends**: Provides statistical price insights for budget planning.
- **CSV Output**: Easy-to-use data files for further analysis.

---

## Prerequisites

- **Python 3.8+**
- **Dependencies**: Install via `pip install requests pandas`
- **API Keys**:
  - **FlightLabs**: Get your key from [goflightlabs.com](https://goflightlabs.com).
  - **Amadeus**: Register at [developers.amadeus.com](https://developers.amadeus.com) and set environment variables (`AMADEUS_API_KEY`, `AMADEUS_API_SECRET`) or use defaults in the script.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/flight-price-scraper.git
   cd flight-price-scraper

---

## Migration to SerpAPI Google Flights

The project has been updated to use SerpAPI Google Flights as the primary flight data provider. This change allows for more comprehensive and accurate flight data.

---

## Recent Updates

- **API Migration**: Transitioned to SerpAPI Google Flights as the primary flight data provider
- **Enhanced UI**: Improved result display with better formatting and details
- **Modular Architecture**: Refactored code for easier maintenance and API switching
- **Search History**: Added tracking of previous searches

---

## Contributors

- **Ario**
- **Myrthe**
- **Floriano**

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
