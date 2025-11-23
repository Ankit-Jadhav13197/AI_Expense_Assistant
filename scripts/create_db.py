# # scripts/create_db.py
# from api.db.session import engine
# from api.db import models

# if __name__ == "__main__":
#     print("Creating database tables...")
#     models.Base.metadata.create_all(bind=engine)
#     print("Done.")

import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.db.session import engine
from api.db import models

if __name__ == "__main__":
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Done.")
