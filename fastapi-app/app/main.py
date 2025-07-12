from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

if not POSTGRES_USER or not POSTGRES_PASSWORD:
    raise RuntimeError(
        "Environment variables POSTGRES_USER and POSTGRES_PASSWORD must be set"
    )


async def create_database_if_not_exists():
    """
    Connect to the default 'postgres' database and create the target database if it does not exist.
    """
    try:
        print("Connecting to the default 'postgres' database...")
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database="postgres",
        )
        conn.autocommit = True  # Enable autocommit for database creation
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_NAME,)
        )
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{POSTGRES_NAME}' does not exist. Creating it...")
            cursor.execute(f"CREATE DATABASE {POSTGRES_NAME}")
            print(f"Database '{POSTGRES_NAME}' created successfully.")
        else:
            print(f"Database '{POSTGRES_NAME}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error while checking or creating the database:", e)
        raise HTTPException(status_code=500, detail="Error creating the database")



async def create_table_if_not_exists():
    """
    Connect to the target database and create the 'users' table if it does not exist.
    """
    try:
        print("Connecting to the target database to check/create the 'users' table...")
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_NAME,  # Target database
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the 'users' table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        print("Table 'users' is ready.")

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error while checking or creating the 'users' table:", e)
        raise HTTPException(status_code=500, detail="Error creating the 'users' table")


def get_db_connection():
    """
    Connect to the target database.
    """

    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database="postgres",
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            cursor_factory=RealDictCursor,
        )
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        raise HTTPException(status_code=500, detail="Database connection error")


class User(BaseModel):
    name: str
    email: str


@app.on_event("startup")
async def on_startup():
    """
    FastAPI startup event to ensure the database exists before the app starts.
    """
    await create_database_if_not_exists()
    await create_table_if_not_exists()


@app.post("/users/")
async def create_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email",
            (user.name, user.email),
        )
        res = cursor.fetchone()
        conn.commit()
        return {"id": res["id"], "name": res["name"], "email": res["email"]}
    except Exception as e:
        conn.rollback()
        print("Error inserting user:", e)
        raise HTTPException(status_code=500, detail="Error inserting user")
    finally:
        cursor.close()
        conn.close()


@app.get("/users/{name}")
async def get_user_email(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM users WHERE name = %s", (name,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return {"name": name, "email": result["email"]}
    except Exception as e:
        print("Error retrieving user:", e)
        raise HTTPException(status_code=500, detail="Error retrieving user")
    finally:
        cursor.close()
        conn.close()
