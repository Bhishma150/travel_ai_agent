from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from tools.flight_tool import FlightSearchTool
from tools.hotel_tool import HotelRecommendationTool
from tools.places_tool import PlacesDiscoveryTool
from tools.weather_tool import WeatherTool

load_dotenv()

# ── Tool instances ────────────────────────────────────────────────────────────
flight_tool  = FlightSearchTool()
hotel_tool   = HotelRecommendationTool()
places_tool  = PlacesDiscoveryTool()
weather_tool = WeatherTool()

SUPPORTED_CITIES = [
    "Delhi", "Mumbai", "Goa", "Bangalore",
    "Chennai", "Hyderabad", "Kolkata", "Jaipur",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_cities(text: str) -> list[str]:
    """Return every supported city mentioned in *text* (case-insensitive)."""
    found = []
    lower = text.lower()
    for city in SUPPORTED_CITIES:
        if city.lower() in lower and city not in found:
            found.append(city)
    return found


def _fetch_city_data(city: str, source: str | None = None) -> dict:
    """Fetch hotels, places, weather (and optionally flights) for one city."""
    data: dict = {"city": city}

    try:
        data["hotels"] = hotel_tool.search_hotels(city)
    except Exception as e:
        data["hotels"] = f"Unavailable ({e})"

    try:
        raw_places = places_tool.search_places(city)
        data["places"] = places_tool.top_places(raw_places)
    except Exception as e:
        data["places"] = f"Unavailable ({e})"

    try:
        data["weather"] = weather_tool.get_weather(city)
    except Exception as e:
        data["weather"] = f"Unavailable ({e})"

    if source:
        try:
            data["flights"] = flight_tool.search_flights(source, city)
        except Exception as e:
            data["flights"] = f"Unavailable ({e})"

    return data


def get_trip_information(query: str) -> dict:
    """
    Parse *query* for source + destination cities, then fetch real-time data
    for every destination found.  Returns a dict keyed by city name.
    """
    cities = _extract_cities(query)
    if not cities:
        return {}

    # Heuristic: first city in query is likely the source if multiple found
    source = cities[0] if len(cities) > 1 else None
    destinations = cities[1:] if len(cities) > 1 else cities

    return {
        city: _fetch_city_data(city, source=source)
        for city in destinations
    }


# ── LLM ───────────────────────────────────────────────────────────────────────

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.4)

SYSTEM_PROMPT = """You are an expert AI Travel Planner specialising in Indian destinations.
You create concise, visually structured travel plans using Markdown.
Always use bullet points, bold headers, and emojis for readability.
Be specific — mention real hotel names, places, and local tips from the data provided.
Never make up information; if data is unavailable say so briefly."""


def travel_agent(query: str) -> str:
    """
    Main entry point.  Fetches live tool data then calls the LLM to produce
    a polished, Markdown-formatted travel plan.
    """
    data = get_trip_information(query)

    data_section = ""
    if data:
        for city, info in data.items():
            data_section += f"\n### {city}\n"
            for key, value in info.items():
                if key == "city":
                    continue
                data_section += f"**{key.title()}:** {value}\n"
    else:
        data_section = "No specific city data retrieved — use general knowledge."

    user_prompt = f"""
**User Request:**
{query}

**Live Travel Data:**
{data_section}

---
Produce a structured travel plan using this exact format:

## ✈️ Trip Summary
(2–3 sentence overview)

## 🏨 Hotel Recommendations
(bullet list per destination)

## 🗺️ Top Places to Visit
(bullet list per destination with one-line descriptions)

## ☁️ Weather Overview
(brief per destination)

## 💰 Budget Estimate
| Category | Estimated Cost (₹) |
|----------|-------------------|
| Flights  | …                 |
| Hotels   | …                 |
| Food     | …                 |
| Activities | …               |
| **Total** | **…**            |

## 📅 Day-wise Itinerary
(one short paragraph or 3–4 bullets per day — keep tight)

## 💡 Travel Tips
(3–5 quick tips relevant to the destination/preference)

Keep the total response under 600 words.  Use Markdown only.
"""

    result = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    return result.content


# ── CLI entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🌍  AI Travel Planner — type 'exit' to quit\n")
    while True:
        query = input("Ask: ").strip()
        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue
        print("\n" + "─" * 60)
        print(travel_agent(query))
        print("─" * 60 + "\n")
