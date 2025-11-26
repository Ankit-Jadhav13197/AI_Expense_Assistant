# api/db/init_db.py
from api.db.database import Base, engine
from api.db import models

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done!")
