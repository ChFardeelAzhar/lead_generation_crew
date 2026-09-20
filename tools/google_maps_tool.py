import os
import json
import requests
from crewai.tools import BaseTool
from pydantic import Field

class GoogleMapsScraperTool(BaseTool):
    name: str = "Google Maps Scraper"
    description: str = (
        "Useful for searching Google Maps to find local businesses, their addresses, "
        "phone numbers, and websites based on a search query like 'hair salons in bradford'."
    )

    def _run(self, search_query: str) -> str:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY is missing in .env file."

        # Using the specific 'places' endpoint for Google Maps data
        url = "https://google.serper.dev/places"
        payload = json.dumps({
            "q": search_query
        })
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            results = response.json()
            
            places = results.get("places", [])
            if not places:
                return f"No businesses found for query: {search_query}"
            
            # Extracting only the relevant structured data
            extracted_data = []
            for place in places:
                business = {
                    "Company Name": place.get("title", ""),
                    "Address": place.get("address", ""),
                    "Contact number": place.get("phoneNumber", "N/A"),
                    "Website URL": place.get("website", "N/A"),
                }
                extracted_data.append(business)
            
            # Returning as a formatted JSON string so the Agent can read it easily
            return json.dumps(extracted_data, indent=2)
            
        except Exception as e:
            return f"An error occurred while fetching data: {str(e)}"