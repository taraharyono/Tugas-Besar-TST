from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
import json

SECRET_KEY = "95f9451e0d7c855350eebfc37b15a05fb50580cc52d13f251ecfe5fe00200566"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None = None

class User(BaseModel):
    username: str
    role: str = "user"

class UserInDB(User):
    hashed_password: str

class PerfumePreferences(BaseModel):
    preferences: List[str]
    dislikes: List[str]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    user_data = next((user for user in db if user["username"] == username), None)
    if user_data:
        return UserInDB(**user_data)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        user_data = next((user for user in users_data if user["username"] == username), None)
        if user_data is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = UserInDB(**user_data)
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user

# Load perfume and user data from the JSON file
with open('perfume.json', 'r') as file:
    perfumes_data = json.load(file)['perfume']

with open('user.json', 'r') as file:
    users_data = json.load(file)['user']

@app.post("/register", response_model=User)
async def register_user(username: str, password: str):
    global users_data

    # Check if the username is already taken
    if any(user["username"] == username for user in users_data):
        raise HTTPException(status_code=400, detail="Username is already taken")

    hashed_password = get_password_hash(password)
    new_user = {
        "id": len(users_data) + 1,
        "username": username,
        "hashed_password": hashed_password,
    }

    # Add the new user to the user list
    users_data.append(new_user)

    # Write the updated user data to the JSON file
    with open('user.json', 'w') as file:
        json.dump({"user": users_data}, file, indent=4)

    return new_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_data, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint to get perfume recommendations based on notes
@app.post("/get_perfume_recommendation", dependencies=[Depends(get_current_user)])
async def get_recommendation(preferences: PerfumePreferences, current_user: UserInDB = Depends(get_current_user)):
    if not preferences:
        return {"error": "No preferences provided"}

    matching_perfumes = []
    for perfume in perfumes_data:
        characteristics = perfume["Notes"].lower()
        # Check if all preferred notes are in characteristics
        has_preferred_notes = all(preference.lower() in characteristics for preference in preferences.preferences)

        # Check if no disliked notes are in characteristics
        has_no_disliked_notes = not any(dislike.lower() in characteristics for dislike in preferences.dislikes)

        if has_preferred_notes and has_no_disliked_notes:
            matching_perfumes.append(perfume)
    
    if not matching_perfumes:
        raise HTTPException(status_code=404, detail="Note(s) not found")

    return {"recommendations": matching_perfumes}

# Endpoint to get perfume notes based on perfume names
@app.get("/get_perfume_notes/{perfume_name}", dependencies=[Depends(get_current_user)])
async def get_perfume_notes(perfume_name: str):
    perfume_notes = [perfume["Notes"] for perfume in perfumes_data if perfume["Name"].lower() == perfume_name.lower()]
    if not perfume_notes:
        raise HTTPException(status_code=404, detail="Perfume not found")
    return {"perfume_name": perfume_name, "perfume_notes": perfume_notes}

# Endpoint to delete perfume based on perfume names
@app.delete("/delete_perfume/{perfume_name}", dependencies=[Depends(get_current_user)])
async def delete_perfume(perfume_name: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Admin role required.")
    
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


# New endpoint to update perfume notes for a specific perfume name
@app.put("/update_perfume_notes/{perfume_name}", dependencies=[Depends(get_current_user)])
async def update_perfume_notes(perfume_name: str, updated_note: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Admin role required.")
    
    global perfumes_data

    updated_note = updated_note.strip()  # Remove leading/trailing whitespaces

    # Loop through each entry to find the matching perfume
    for perfume in perfumes_data:
        if perfume["Name"].lower() == perfume_name.lower():
            current_notes = perfume["Notes"]
            updated_notes = f"{current_notes}, {updated_note}" if current_notes else updated_note

            perfume["Notes"] = updated_notes

            with open('perfume.json', 'w') as file:
                json.dump({"perfume": perfumes_data}, file, indent=4)

            return {"message": f"Perfume notes for '{perfume_name}' updated successfully. New perfume notes: {updated_notes}"}

    raise HTTPException(status_code=404, detail="Perfume not found")

# New endpoint to add a new perfume entry and write it to the beginning of the JSON file
@app.post("/add_new_perfume", dependencies=[Depends(get_current_user)])
async def add_new_perfume(name: str, brand: str, notes: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Admin role required.")
    
    global perfumes_data

    new_perfume = {
        "Name": name,
        "Brand": brand,
        "Notes": notes
    }

    # Add the new perfume entry to the beginning of the perfume list
    perfumes_data.insert(0, new_perfume)

    # Write the updated perfume data to the JSON file
    with open('perfume.json', 'w') as file:
        json.dump({"perfume": perfumes_data}, file, indent=4)

    return {"message": f"New perfume '{name}' added successfully"}

# pwd = get_password_hash("test123")
# print(pwd)