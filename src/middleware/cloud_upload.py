import os
import cloudinary
from cloudinary import uploader
# from cloudinary.uploader import upload
# from cloudinary.utils import cloudinary_url


cloudinary.config(
    cloud_name = "thehivecloudstorage",    #os.getenv('CLOUD_NAME'),   
    api_key = "134419777876826",    #os.getenv('API_KEY'),   
    api_secret = "ZBzzFoC0br9z2jCKiHRxA_EkRQ0"    #os.getenv('API_SECRET') 
)

def upload_file(file_to_upload):
  if file_to_upload:
    try:
      upload_result = uploader.upload(file_to_upload)
    except:
      return {"msg":"Error uploading file"}
    
    return upload_result.get("url")
    
  

