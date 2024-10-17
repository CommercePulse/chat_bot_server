import os
from config import constants
 
from dotenv import load_dotenv
 
load_dotenv()
 
# return self.botNamespaceQueries.get_all_tables()

def save_uploaded_file(uploaded_file, namespace_id):
    upload_dir: str = os.path.join(constants.UPLOAD_DIR, namespace_id, constants.PRIMARY_FOLDER)

   # Create directories if they don't exist
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, uploaded_file.filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())
    return file_path

