from supabase import create_client, Client
from .config import settings

_SUPABASE_URL = settings.SUPABASE_URL
_SUPABASE_KEY = settings.SUPABASE_KEY

supabase: Client = create_client(_SUPABASE_URL, _SUPABASE_KEY)

def get_supabase():
    return supabase
