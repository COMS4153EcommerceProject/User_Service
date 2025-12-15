from __future__ import annotations

import os
from datetime import datetime

from typing import Dict, List, Tuple
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path, status
from typing import Optional

from models.user import UserCreate, UserRead, UserUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.preference import PreferenceCreate, PreferenceRead, PreferenceUpdate
from models.user_address import UserAddressCreate, UserAddressRead

import pymysql
from pymysql.cursors import DictCursor

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Configuration for Cloud SQL + Local Development
# -----------------------------------------------------------------------------
def get_db_connection():
    """
    Connect to MySQL using either:
    - Cloud SQL Unix socket (Cloud Run)
    - TCP host (Local dev)
    """

    # Cloud Run socket path
    db_socket = os.getenv("DB_SOCKET")  # e.g. "/cloudsql/project:region:instance"
    db_host = os.getenv("DB_HOST")      # e.g. "127.0.0.1" for local dev
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    if db_socket:
        # Cloud Run connection
        return pymysql.connect(
            unix_socket=db_socket,
            user=db_user,
            password=db_pass,
            database=db_name,
            cursorclass=DictCursor,
        )
    else:
        # Local development over TCP/IP
        return pymysql.connect(
            host=db_host or "127.0.0.1",
            port=3306,
            user=db_user,
            password=db_pass,
            database=db_name,
            cursorclass=DictCursor,
        )


app = FastAPI(
    title="User Microservice",
    description="FastAPI Microservice backed by Cloud SQL.",
    version="0.3.0",
)

# -----------------------------------------------------------------------------
# User endpoints
# -----------------------------------------------------------------------------
@app.post("/users", response_model=UserRead, status_code=201)
def create_user(user: UserCreate):
    conn = get_db_connection()
    user_id = str(uuid4())
    now = datetime.utcnow()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users
                (user_id, first_name, last_name, email, phone, password, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user.phone,
                    user.password,
                    now,
                    now,
                ),
            )
        conn.commit()
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()

    return UserRead(
        user_id=user_id,
        created_at=now,
        updated_at=now,
        **user.dict()
    )

@app.get("/users", response_model=List[UserRead])
def list_users(
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
    conn = get_db_connection()
    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if first_name:
        query += " AND first_name=%s"
        params.append(first_name)
    if last_name:
        query += " AND last_name=%s"
        params.append(last_name)
    if email:
        query += " AND email=%s"
        params.append(email)

    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    conn.close()
    return rows


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: UUID):
    conn = get_db_connection()

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_id=%s", (str(user_id),))
        user = cur.fetchone()

    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: UUID, update: UserUpdate):
    updates = {k: v for k, v in update.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    conn = get_db_connection()
    set_clause = ", ".join([f"{k}=%s" for k in updates])
    values = list(updates.values())
    values.append(datetime.utcnow())
    values.append(str(user_id))

    with conn.cursor() as cur:
        cur.execute(
            f"""
            UPDATE users
            SET {set_clause}, updated_at=%s
            WHERE user_id=%s
            """,
            values,
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        cur.execute("SELECT * FROM users WHERE user_id=%s", (str(user_id),))
        user = cur.fetchone()

    conn.commit()
    conn.close()
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID):
    conn = get_db_connection()

    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE user_id=%s", (str(user_id),))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------
@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: UUID):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

# -----------------------------------------------------------------------------
# Preference Endpoints
# -----------------------------------------------------------------------------
@app.post("/preferences", response_model=PreferenceRead, status_code=201)
def create_preference(pref: PreferenceCreate):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/preferences", response_model=List[PreferenceRead])
def list_preferences(
    language: Optional[str] = Query(None, description="Filter by preferred language"), 
    currency: Optional[str] = Query(None, description="Filter by preferred currency"),
):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/preferences/{user_id}", response_model=PreferenceRead)
def get_preference(user_id: UUID):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.patch("/preferences/{user_id}", response_model=PreferenceRead)
def update_preference(user_id: UUID, update: PreferenceUpdate):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.delete("/preferences/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(user_id: UUID):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

# -----------------------------------------------------------------------------
# User_Address Endpoints
# -----------------------------------------------------------------------------
@app.post("/user_addresses", response_model=UserAddressRead, status_code=201)
def create_user_address(ua: UserAddressCreate):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/user_addresses", response_model=List[UserAddressRead])
def list_user_addresses(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"), 
    addr_id: Optional[UUID] = Query(None, description="Filter by address ID"),
):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/user_addresses/{user_id}/{addr_id}", response_model=UserAddressRead)
def get_user_address(user_id: UUID, addr_id: UUID):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

@app.delete("/user_addresses/{user_id}/{addr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_address(user_id: UUID, addr_id: UUID):
    conn = get_db_connection()
    conn.close()
    raise HTTPException(status_code=501, detail="Not implemented")

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
