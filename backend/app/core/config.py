import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL no está configurada")

SUPABASE_URL = os.getenv("SUPABASE_URL")
if SUPABASE_URL is None:
    raise RuntimeError("SUPABASE_URL no está configurada")

SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
if SUPABASE_ANON_KEY is None:
    raise RuntimeError("SUPABASE_ANON_KEY no está configurada")

SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if SUPABASE_SERVICE_ROLE_KEY is None:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY no está configurada")

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
if SUPABASE_JWT_SECRET is None:
    raise RuntimeError("SUPABASE_JWT_SECRET no está configurada")
