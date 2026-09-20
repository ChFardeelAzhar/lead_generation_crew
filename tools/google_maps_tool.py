import os
import json
import requests
from typing import List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# 1. Domain Model: Strict schema for our leads
class BusinessLead(BaseModel):
    company_name: str = Field(..., description="The official name of the business")
    address: str = Field(..., description="The physical address of the location")
    contact_number: Optional[str] = Field(default="N/A", description="Phone number for contact")
    website_url: Optional[str] = Field(default="N/A", description="Official website URL")

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

        url = "https://google.serper.dev/places"
        payload = json.dumps({"q": search_query})
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
            
            validated_leads = []
            for place in places:
                # 2. Validation: Passing data through the Pydantic model
                lead = BusinessLead(
                    company_name=place.get("title", "Unknown"),
                    address=place.get("address", "Unknown"),
                    contact_number=place.get("phoneNumber", "N/A"),
                    website_url=place.get("website", "N/A")
                )
                # Storing the validated dump
                validated_leads.append(lead.model_dump())
            
            return json.dumps(validated_leads, indent=2)
            
        except Exception as e:
            return f"An error occurred while fetching data: {str(e)}"