from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List, Tuple
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path, status
from typing import Optional

from models.user import UserCreate, UserRead, UserUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.preference import PreferenceCreate, PreferenceRead, PreferenceUpdate
from models.user_address import UserAddressCreate, UserAddressRead

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
users: Dict[UUID, UserRead] = {}
preference: Dict[UUID, PreferenceRead] = {}
addresses: Dict[UUID, AddressRead] = {}
user_addresses: Dict[Tuple[UUID, UUID], UserAddressRead] = {}

app = FastAPI(
    title="User Microservice",
    description="Handles user accounts, preferences, and addresses. All routes return NOT IMPLEMENTED for Sprint 1.",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# User endpoints
# -----------------------------------------------------------------------------

@app.post("/users", response_model=UserRead, status_code=201)
def create_user(user: UserCreate):
    """Create a new user."""
    user_read = UserRead(**user.model_dump())
    users[user_read.user_id] = user_read
    return user_read

@app.get("/users", response_model=List[UserRead])
def list_users(
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
    """List users with optional filters."""
    results = list(users.values())
    if first_name:
        results = [u for u in results if u.first_name == first_name]
    if last_name:
        results = [u for u in results if u.last_name == last_name]
    if email:
        results = [u for u in results if u.email == email]
    return results

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: UUID = Path(..., description="User ID to retrieve")):
    """Get a specific user by ID."""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: UUID, update: UserUpdate):
    """Partially update user fields."""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    stored = users[user_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    users[user_id] = UserRead(**stored)
    return users[user_id]

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID):
    """Delete a user by ID."""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]
    return None

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------
@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.addr_id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.addr_id] = AddressRead(**address.model_dump())
    return addresses[address.addr_id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

@app.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    del addresses[address_id]
    return None

# -----------------------------------------------------------------------------
# Preference Endpoints
# -----------------------------------------------------------------------------
@app.post("/preferences", response_model=PreferenceRead, status_code=201)
def create_preference(pref: PreferenceCreate):
    if pref.user_id in preference:
        raise HTTPException(status_code=400, detail="Preference for this user already exists")
    preference[pref.user_id] = PreferenceRead(**pref.model_dump())
    return preference[pref.user_id]

@app.get("/preferences", response_model=List[PreferenceRead])
def list_preferences(
    language: Optional[str] = Query(None, description="Filter by preferred language"), 
    currency: Optional[str] = Query(None, description="Filter by preferred currency"),
):
    results = list(preference.values())
    if language:
        results = [p for p in results if p.language == language]
    if currency:
        results = [p for p in results if p.currency == currency]
    return results

@app.get("/preferences/{user_id}", response_model=PreferenceRead)
def get_preference(user_id: UUID):
    if user_id not in preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return preference[user_id]

@app.patch("/preferences/{user_id}", response_model=PreferenceRead)
def update_preference(user_id: UUID, update: PreferenceUpdate):
    if user_id not in preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    stored = preference[user_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    preference[user_id] = PreferenceRead(**stored)
    return preference[user_id]

@app.delete("/preferences/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(user_id: UUID):
    if user_id not in preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    del preference[user_id]
    return None

# -----------------------------------------------------------------------------
# User_Address Endpoints
# -----------------------------------------------------------------------------
@app.post("/user_addresses", response_model=UserAddressRead, status_code=201)
def create_user_address(ua: UserAddressCreate):
    if ua.user_id not in users:
        raise HTTPException(status_code=400, detail="User not found")
    if ua.addr_id not in addresses:
        raise HTTPException(status_code=400, detail="Address not found")
    key = (ua.user_id, ua.addr_id)
    if key in user_addresses:
        raise HTTPException(status_code=400, detail="Mapping already exists")
    relation = UserAddressRead(**ua.model_dump())
    user_addresses[key] = relation
    return relation

@app.get("/user_addresses", response_model=List[UserAddressRead])
def list_user_addresses(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"), 
    addr_id: Optional[UUID] = Query(None, description="Filter by address ID"),
):
    results = list(user_addresses.values())
    if user_id:
        results = [ua for ua in results if ua.user_id == user_id]
    if addr_id:
        results = [ua for ua in results if ua.addr_id == addr_id]
    return results

@app.get("/user_addresses/{user_id}/{addr_id}", response_model=UserAddressRead)
def get_user_address(user_id: UUID, addr_id: UUID):
    key = (user_id, addr_id)
    if key not in user_addresses:
        raise HTTPException(status_code=404, detail="User-Address mapping not found")
    return user_addresses[key]

@app.delete("/user_addresses/{user_id}/{addr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_address(user_id: UUID, addr_id: UUID):
    key = (user_id, addr_id)
    if key not in user_addresses:
        raise HTTPException(status_code=404, detail="User-Address mapping not found")
    del user_addresses[key]
    return None

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
