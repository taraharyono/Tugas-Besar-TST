from fastapi import FastAPI, HTTPException
from typing import List
import json

app = FastAPI()

# Load perfume data from the JSON file
with open('perfume.json', 'r') as file:
    perfumes_data = json.load(file)['perfume']

# Endpoint to get perfume recommendations based on notes
@app.post("/get_perfume_recommendation")
async def get_recommendation(preferences: List[str]):
    if not preferences:
        return {"error": "No preferences provided"}

    matching_perfumes = []
    for perfume in perfumes_data:
        characteristics = perfume["Notes"].lower()
        if all(preference.lower() in characteristics for preference in preferences):
            matching_perfumes.append(perfume)
    
    if not matching_perfumes:
        raise HTTPException(status_code=404, detail="Note(s) not found")

    return {"recommendations": matching_perfumes}

# Endpoint to get perfume notes based on perfume names
@app.get("/get_perfume_notes/{perfume_name}")
async def get_perfume_notes(perfume_name: str):
    perfume_notes = [perfume["Notes"] for perfume in perfumes_data if perfume["Name"].lower() == perfume_name.lower()]
    if not perfume_notes:
        raise HTTPException(status_code=404, detail="Perfume not found")
    return {"perfume_name": perfume_name, "perfume_notes": perfume_notes}