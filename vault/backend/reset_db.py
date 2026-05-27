import shutil

from backend.config import CHROMA_DIR

if CHROMA_DIR.exists():

    shutil.rmtree(CHROMA_DIR)

    print("Database deleted")

else:
    print("No database found")