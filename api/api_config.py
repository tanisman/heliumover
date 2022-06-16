from decouple import config

DB_URI = config("DB_URI")
API_HAS_DOWNSTREAM = config("API_HAS_DOWNSTREAM", default=True, cast=bool)
API_HAS_UPSTREAM = config("API_HAS_UPSTREAM", default=True, cast=bool)
API_HAS_HOTSPOT = config("API_HAS_HOTSPOT", default=True, cast=bool)
API_HAS_ADMIN = config("API_HAS_ADMIN", default=True, cast=bool)