import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

assert SUPABASE_URL and SUPABASE_KEY, "Set SUPABASE_URL and SUPABASE_KEY in your environment."

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    try:
        response = supabase.table("users").select("*").limit(1).execute()
        # Print the full response object for debugging
        print("Raw response:", response)
        # Try to access data
        if hasattr(response, "data") and isinstance(response.data, list):
            print("Connection successful! Example row:", response.data)
        else:
            print("Unexpected response structure. Dump:", getattr(response, "model_dump_json", lambda: str(response))())
    except Exception as e:
        print("Failed to connect to Supabase:", e)

if __name__ == "__main__":
    test_connection()