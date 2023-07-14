import os
import cloudinary
from cloudinary import uploader
# from cloudinary.uploader import upload
# from cloudinary.utils import cloudinary_url


from dotenv import load_dotenv

project_folder = os.path.expanduser('~/pdhs-server')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

cloudinary.config(
    cloud_name =  os.getenv('CLOUD_NAME'),   
    api_key = os.getenv('API_KEY'),   
    api_secret = os.getenv('API_SECRET') 
)

def upload_file(file_to_upload):
  if file_to_upload:
    try:
      upload_result = uploader.upload(file_to_upload)
    except:
      return {"msg":"Error uploading file"}
    
    return upload_result.get("url")
    
  

