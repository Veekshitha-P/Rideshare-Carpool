# ================================================================
#  Carpooling Coordinator — FastAPI Backend
#  File: backend/main.py
# ================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DB_CONFIG

app = FastAPI(title="Carpooling Coordinator API", version="1.0.0")

# ----------------------------------------------------------------
# CORS
# ----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
#  Database helper
# ================================================================
def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {e}")


# ================================================================
#  Pydantic Models
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
    departure_time:  str
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

# ── NEW: Booking model ──────────────────────────────────────
class BookingRequest(BaseModel):
    ride_id:      int
    rider_id:     int
    seats_booked: int = 1


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
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM drivers ORDER BY created_at DESC")
    drivers = cursor.fetchall()
    cursor.close(); conn.close()
    return drivers

@app.post("/drivers", status_code=201)
def create_driver(driver: DriverCreate):
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
#  RIDES
# ================================================================

@app.get("/rides")
def get_all_rides():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT
            r.id, r.pickup_point, r.dropoff_point, r.departure_time,
            r.total_seats, r.seats_available, r.fare_per_seat, r.status,
            r.created_at, r.updated_at,
            d.id   AS driver_id,   d.name    AS driver_name,
            d.vehicle,             d.phone   AS driver_phone,
            ri.id  AS rider_id,    ri.name   AS rider_name,
            ri.phone AS rider_phone
        FROM rides r
        JOIN      drivers d  ON r.driver_id = d.id
        LEFT JOIN riders  ri ON r.rider_id  = ri.id
        ORDER BY r.created_at DESC
    """
    cursor.execute(sql)
    rides = cursor.fetchall()
    for ride in rides:
        for key, val in ride.items():
            if isinstance(val, datetime):
                ride[key] = val.strftime("%Y-%m-%d %H:%M")
    cursor.close(); conn.close()
    return rides

@app.post("/rides", status_code=201)
def create_ride(ride: RideCreate):
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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rides WHERE id = %s", (ride_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close(); conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Ride not found")
    return {"message": "Ride deleted"}


# ================================================================
#  BOOKINGS
# ================================================================

@app.post("/bookings", status_code=201)
def book_ride(req: BookingRequest):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Fetch ride + driver details
        # NOTE: uses correct column names: pickup_point, dropoff_point,
        #       seats_available, fare_per_seat, vehicle, license_no
        cursor.execute("""
            SELECT r.id, r.pickup_point, r.dropoff_point,
                   r.seats_available, r.total_seats,
                   r.fare_per_seat, r.departure_time, r.status,
                   d.id         AS driver_id,
                   d.name       AS driver_name,
                   d.phone      AS driver_phone,
                   d.vehicle    AS vehicle,
                   d.license_no AS license_no
            FROM rides r
            JOIN drivers d ON r.driver_id = d.id
            WHERE r.id = %s AND r.status = 'available'
        """, (req.ride_id,))
        ride = cursor.fetchone()

        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found or not available")

        if req.seats_booked > ride['seats_available']:
            raise HTTPException(
                status_code=400,
                detail=f"Only {ride['seats_available']} seat(s) left"
            )

        # 2. Fetch rider details
        cursor.execute("SELECT * FROM riders WHERE id = %s", (req.rider_id,))
        rider = cursor.fetchone()
        if not rider:
            raise HTTPException(status_code=404, detail="Rider not found")

        # 3. Insert into bookings table
        total_fare = ride['fare_per_seat'] * req.seats_booked
        cursor.execute("""
            INSERT INTO bookings
              (ride_id, rider_id, driver_id,
               pickup_location, dropoff_location,
               fare, seats_booked)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            req.ride_id, req.rider_id, ride['driver_id'],
            ride['pickup_point'], ride['dropoff_point'],
            total_fare, req.seats_booked
        ))
        booking_id = cursor.lastrowid

        # 4. Update seats_available on the ride; mark full if needed
        new_available = ride['seats_available'] - req.seats_booked
        new_status    = 'full' if new_available <= 0 else 'available'
        cursor.execute("""
            UPDATE rides
            SET seats_available = %s, status = %s, rider_id = %s
            WHERE id = %s
        """, (new_available, new_status, req.rider_id, req.ride_id))

        conn.commit()

        dep = ride['departure_time']
        if isinstance(dep, datetime):
            dep = dep.strftime("%Y-%m-%d %H:%M")

        return {
            "message": "Ride booked successfully!",
            "booking": {
                "booking_id":   booking_id,
                "ride_id":      req.ride_id,
                "driver_name":  ride['driver_name'],
                "driver_phone": ride['driver_phone'],
                "vehicle":      ride['vehicle'],
                "license_plate": ride['license_no'],
                "rider_name":   rider['name'],
                "rider_phone":  rider['phone'],
                "pickup":       ride['pickup_point'],
                "dropoff":      ride['dropoff_point'],
                "departure_time": dep,
                "fare":         float(total_fare),
                "seats_booked": req.seats_booked,
                "status":       "confirmed"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Find the confirmed booking + current ride seats
        cursor.execute("""
            SELECT b.booking_id, b.ride_id, b.seats_booked,
                   r.seats_available, r.total_seats
            FROM bookings b
            JOIN rides r ON b.ride_id = r.id
            WHERE b.booking_id = %s AND b.booking_status = 'confirmed'
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found or already cancelled"
            )

        # 2. Restore seats on the ride
        restored_seats = booking['seats_available'] + booking['seats_booked']
        cursor.execute("""
            UPDATE rides
            SET seats_available = %s, status = 'available'
            WHERE id = %s
        """, (restored_seats, booking['ride_id']))

        # 3. Mark booking as cancelled (row stays for audit/history)
        cursor.execute("""
            UPDATE bookings
            SET booking_status = 'cancelled'
            WHERE booking_id = %s
        """, (booking_id,))

        conn.commit()
        return {"message": f"Booking #{booking_id} cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.get("/bookings")
def get_all_bookings():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # NOTE: uses correct column names from schema:
        #   drivers.vehicle (not vehicle_model/vehicle_color)
        #   drivers.license_no (not license_plate)
        #   rides.pickup_point / dropoff_point (not pickup_location)
        cursor.execute("""
            SELECT
                b.booking_id,
                b.booking_status,
                b.booked_at,
                b.seats_booked,
                b.fare,
                ri.name       AS rider_name,
                ri.phone      AS rider_phone,
                ri.email      AS rider_email,
                d.name        AS driver_name,
                d.phone       AS driver_phone,
                d.vehicle     AS vehicle_model,
                d.license_no  AS vehicle_color,
                r.pickup_point    AS pickup_location,
                r.dropoff_point   AS dropoff_location,
                r.departure_time
            FROM bookings b
            JOIN riders  ri ON b.rider_id  = ri.id
            JOIN drivers d  ON b.driver_id = d.id
            JOIN rides   r  ON b.ride_id   = r.id
            ORDER BY b.booked_at DESC
        """)
        rows = cursor.fetchall()
        # Convert datetime to string
        for row in rows:
            for key, val in row.items():
                if isinstance(val, datetime):
                    row[key] = val.strftime("%Y-%m-%d %H:%M")
        return rows
    finally:
        cursor.close()
        conn.close()