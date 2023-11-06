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

# Endpoint to delete perfume based on perfume names
@app.delete("/delete_perfume/{perfume_name}")
async def delete_perfume(perfume_name: str):
    global perfumes_data

    index_to_remove = None

    # Loop through each entry to find the matching perfume
    for index, perfume in enumerate(perfumes_data):
        if perfume["Name"].lower() == perfume_name.lower():
            index_to_remove = index
            break  # Stop the loop when the match is found

    if index_to_remove is not None:
        deleted_perfume = perfumes_data.pop(index_to_remove)

        with open('perfume.json', 'w') as file:
            json.dump({"perfume": perfumes_data}, file, indent=4)

        return {"message": f"Perfume '{deleted_perfume['Name']}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Perfume not found")