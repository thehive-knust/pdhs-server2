import os
from cloudinary.uploader import upload
import cloudinary
from cloudinary.utils import cloudinary_url


cloudinary.config(
    cloud_name =  os.getenv('CLOUD_NAME'),   
    api_key = os.getenv('API_KEY'),   
    api_secret = os.getenv('API_SECRET') 
)

def upload_file(file_to_upload):
  if file_to_upload:
    try:
      upload_result = upload(file_to_upload)
    except:
      return {"msg":"Error uploading file"}
    
    return upload_result.get("url")
    
  

