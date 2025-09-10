from fastapi import APIRouter
import os
import requests

router = APIRouter()

@router.get("/nfl_events")
def nfl_events():
    ODDS_API_KEY = os.getenv("ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/events?apiKey={ODDS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "status_code": response.status_code,
            "error": response.text
        }
    
    