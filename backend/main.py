# ================================================================
#  Carpooling Coordinator — FastAPI Backend
#  File: backend/main.py
#
#  Endpoints:
#    Drivers  : GET/POST /drivers  |  PUT/DELETE /drivers/{id}
#    Riders   : GET/POST /riders   |  PUT/DELETE /riders/{id}
#    Rides    : GET/POST /rides    |  PUT/DELETE /rides/{id}
# ================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DB_CONFIG          # ← database credentials

app = FastAPI(title="Carpooling Coordinator API", version="1.0.0")

# ----------------------------------------------------------------
# CORS — allow the frontend (any origin during dev) to call this API
# ----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, replace * with your domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
#  Database helper — returns a fresh connection each time
# ================================================================
def get_db():
    """Create and return a MySQL connection using config.py settings."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {e}")


# ================================================================
#  Pydantic Models — define the shape of request/response data
# ================================================================

class DriverCreate(BaseModel):
    name:       str
    phone:      str
    email:      str
    vehicle:    str
    license_no: str

class DriverUpdate(BaseModel):
    name:       Optional[str] = None
    phone:      Optional[str] = None
    email:      Optional[str] = None
    vehicle:    Optional[str] = None
    license_no: Optional[str] = None

class RiderCreate(BaseModel):
    name:  str
    phone: str
    email: str

class RiderUpdate(BaseModel):
    name:  Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class RideCreate(BaseModel):
    driver_id:       int
    rider_id:        Optional[int] = None
    pickup_point:    str
    dropoff_point:   str
    departure_time:  str          # "YYYY-MM-DD HH:MM"
    total_seats:     int = 3
    seats_available: int = 3
    fare_per_seat:   float
    status:          str = "available"

class RideUpdate(BaseModel):
    driver_id:       Optional[int]   = None
    rider_id:        Optional[int]   = None
    pickup_point:    Optional[str]   = None
    dropoff_point:   Optional[str]   = None
    departure_time:  Optional[str]   = None
    total_seats:     Optional[int]   = None
    seats_available: Optional[int]   = None
    fare_per_seat:   Optional[float] = None
    status:          Optional[str]   = None


# ================================================================
#  ROOT — health check
# ================================================================
@app.get("/")
def root():
    return {"message": "Carpooling Coordinator API is running 🚗"}


# ================================================================
#  DRIVERS
# ================================================================

@app.get("/drivers")
def get_all_drivers():
    """Fetch all drivers — SELECT * FROM drivers"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)       # returns rows as dicts
    cursor.execute("SELECT * FROM drivers ORDER BY created_at DESC")
    drivers = cursor.fetchall()
    cursor.close(); conn.close()
    return drivers

@app.post("/drivers", status_code=201)
def create_driver(driver: DriverCreate):
    """Add a new driver — INSERT INTO drivers"""
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO drivers (name, phone, email, vehicle, license_no)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, (driver.name, driver.phone, driver.email,
                             driver.vehicle, driver.license_no))
        conn.commit()
        new_id = cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close(); conn.close()
    return {"message": "Driver added", "id": new_id}

@app.put("/drivers/{driver_id}")
def update_driver(driver_id: int, data: DriverUpdate):
    """Update driver fields — UPDATE drivers SET ... WHERE id = ?"""
    # Build dynamic SET clause from only the fields that were sent
    fields = {k: v for k, v in data.dict().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [driver_id]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE drivers SET {set_clause} WHERE id = %s", values)
    conn.commit()
    affected = cursor.rowcount
    cursor.close(); conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": "Driver updated"}

@app.delete("/drivers/{driver_id}")
def delete_driver(driver_id: int):
    """Remove a driver — DELETE FROM drivers WHERE id = ?"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM drivers WHERE id = %s", (driver_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close(); conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": "Driver deleted"}


# ================================================================
#  RIDERS
# ================================================================

@app.get("/riders")
def get_all_riders():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM riders ORDER BY created_at DESC")
    riders = cursor.fetchall()
    cursor.close(); conn.close()
    return riders

@app.post("/riders", status_code=201)
def create_rider(rider: RiderCreate):
    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO riders (name, phone, email) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (rider.name, rider.phone, rider.email))
        conn.commit()
        new_id = cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close(); conn.close()
    return {"message": "Rider added", "id": new_id}

@app.put("/riders/{rider_id}")
def update_rider(rider_id: int, data: RiderUpdate):
    fields = {k: v for k, v in data.dict().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [rider_id]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE riders SET {set_clause} WHERE id = %s", values)
    conn.commit()
    affected = cursor.rowcount
    cursor.close(); conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Rider not found")
    return {"message": "Rider updated"}

@app.delete("/riders/{rider_id}")
def delete_rider(rider_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM riders WHERE id = %s", (rider_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close(); conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Rider not found")
    return {"message": "Rider deleted"}


# ================================================================
#  RIDES  (main table — JOIN with drivers & riders)
# ================================================================

@app.get("/rides")
def get_all_rides():
    """Fetch all rides with driver & rider names via JOIN"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT
            r.id, r.pickup_point, r.dropoff_point, r.departure_time,
            r.total_seats, r.seats_available, r.fare_per_seat, r.status,
            r.created_at, r.updated_at,
            d.id   AS driver_id,   d.name AS driver_name,
            d.vehicle,             d.phone AS driver_phone,
            ri.id  AS rider_id,    ri.name AS rider_name,
            ri.phone AS rider_phone
        FROM rides r
        JOIN  drivers d  ON r.driver_id = d.id
        LEFT JOIN riders ri ON r.rider_id  = ri.id
        ORDER BY r.created_at DESC
    """
    cursor.execute(sql)
    rides = cursor.fetchall()
    # Convert datetime objects to strings for JSON serialisation
    for ride in rides:
        for key, val in ride.items():
            if isinstance(val, datetime):
                ride[key] = val.strftime("%Y-%m-%d %H:%M")
    cursor.close(); conn.close()
    return rides

@app.post("/rides", status_code=201)
def create_ride(ride: RideCreate):
    """Post a new ride — INSERT INTO rides"""
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO rides
          (driver_id, rider_id, pickup_point, dropoff_point,
           departure_time, total_seats, seats_available, fare_per_seat, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, (
            ride.driver_id, ride.rider_id, ride.pickup_point,
            ride.dropoff_point, ride.departure_time,
            ride.total_seats, ride.seats_available,
            ride.fare_per_seat, ride.status
        ))
        conn.commit()
        new_id = cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close(); conn.close()
    return {"message": "Ride created", "id": new_id}

@app.put("/rides/{ride_id}")
def update_ride(ride_id: int, data: RideUpdate):
    """Update ride details — UPDATE rides SET ... WHERE id = ?"""
    fields = {k: v for k, v in data.dict().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [ride_id]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE rides SET {set_clause} WHERE id = %s", values)
    conn.commit()
    affected = cursor.rowcount
    cursor.close(); conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Ride not found")
    return {"message": "Ride updated"}

@app.delete("/rides/{ride_id}")
def delete_ride(ride_id: int):
    """Cancel a ride — DELETE FROM rides WHERE id = ?"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rides WHERE id = %s", (ride_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close(); conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Ride not found")
    return {"message": "Ride deleted"}
