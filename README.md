# AI-Powered Travel Planning System using LangChain

An AI-powered travel planning application that helps users create personalized itineraries based on their source city, destination(s), travel dates, trip duration, budget, and travel preferences.

The project combines a Streamlit interface, LangChain, a Groq-hosted language model, JSON datasets, and the Open-Meteo weather API to generate travel recommendations and export itineraries as PDF files.

## Features

- **Multi-destination planning** — plan trips that include multiple destinations.
- **Flight search** — retrieve flight options from a JSON dataset.
- **Hotel recommendations** — suggest accommodation using the available hotel dataset.
- **Places of interest** — recommend attractions from the places dataset.
- **Weather information** — retrieve weather data using the Open-Meteo API.
- **Budget estimation** — estimate trip expenses and help assess budget suitability.
- **AI-generated itinerary** — produce a day-wise travel plan with recommendations.
- **PDF export** — download the generated itinerary.
- **Streamlit interface** — enter trip details through a web-based dashboard.

## Technology Stack

- Python
- Streamlit
- LangChain
- Groq LLM
- Open-Meteo API
- JSON datasets
- Requests
- ReportLab

## Project Structure

```text
travel_ai_agent/
├── app.py
├── agent.py
├── data/
│   ├── flights.json
│   ├── hotels.json
│   └── places.json
├── tools/
│   ├── flight_tool.py
│   ├── hotel_tool.py
│   ├── places_tool.py
│   ├── weather_tool.py
│   └── budget_tool.py
├── utils/
│   └── helpers.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

*This is the intended project layout; adjust filenames if your local files differ.*

## Prerequisites

- Python 3.10 or a compatible version supported by your installed dependencies
- A Groq API key
- Internet access for the LLM and weather API

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd travel_ai_agent
```

Replace `<YOUR_REPOSITORY_URL>` with your GitHub repository URL.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If ReportLab is not listed in `requirements.txt`, install it with:

```bash
pip install reportlab
```

### 4. Configure the API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Keep your real API key private. Do not commit `.env` to GitHub. Ensure `.gitignore` contains:

```gitignore
.venv/
venv/
.env
__pycache__/
*.py[cod]
```

## Run the Application

From the project root, run:

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open it in your browser.

## How to Use

1. Select your source city.
2. Choose one or more destinations supported by the datasets.
3. Select the trip start date and duration.
4. Enter your estimated total budget.
5. Choose a travel preference.
6. Generate and review the itinerary.
7. Download the itinerary as a PDF if needed.

## Project Workflow

```text
User Inputs
    |
    v
Streamlit Dashboard
    |
    v
Travel Planning Workflow
    |
    +--> Flight Search (JSON)
    +--> Hotel Recommendations (JSON)
    +--> Places of Interest (JSON)
    +--> Weather Lookup (Open-Meteo API)
    +--> Budget Estimation
    |
    v
LLM-assisted Itinerary Generation
    |
    v
Itinerary Display and PDF Export
```

## Data and Accuracy Notes

- Flight, hotel, and attraction recommendations depend on the supplied JSON datasets.
- Sample data may not reflect current real-world prices, availability, or schedules.
- Weather information depends on the location lookup and forecast period supported by the weather integration.
- Budget estimates are indicative, not confirmed quotes.
- Verify travel details with official providers before booking.

## Troubleshooting

- **Missing API key:** Check that `.env` exists in the project root and contains `GROQ_API_KEY`.
- **Missing package:** Activate the virtual environment and install dependencies from `requirements.txt`.
- **No cities in dropdown:** Check that the expected JSON files exist in `data/` and contain city fields.
- **Weather lookup fails:** Check your internet connection and the weather tool's location lookup.
- **PDF export fails:** Install ReportLab with `pip install reportlab`.

## Future Improvements

- Interactive maps and route visualization
- Persistent trip history
- Conversational memory
- Expanded and refreshed travel datasets
- More robust budget optimization
- Automated tests and deployment

## License

This project is intended for educational and portfolio use. Add a license file if you plan to distribute it publicly.
