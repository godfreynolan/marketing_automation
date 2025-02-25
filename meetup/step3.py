import requests
import config
from ln_oauth import auth, headers

creds = {
    "client_id": config.LINKEDIN_CLIENT_ID,
    "client_secret": config.LINKEDIN_CLIENT_SECRET,
    "redirect_uri": "http://127.0.0.1:8080",
    "access_token": config.LINKEDIN_ACCESS_TOKEN
}
access_token = auth(creds) # Authenticate the API
headers = headers(access_token) # Make the headers to attach to the API call.
print(headers)

def user_info(headers):
    '''
    Get user information from Linkedin
    '''
    response = requests.get('https://api.linkedin.com/v2/userinfo', headers = headers)
    user_info = response.json()
    return user_info
 
# Get user id to make a UGC post
user_info = user_info(headers)
print(user_info)
urn = user_info['sub']
author = f'urn:li:person:{urn}'


# Replace with your LinkedIn API credentials
ACCESS_TOKEN = config.LINKEDIN_ACCESS_TOKEN
API_BASE_URL = "https://api.linkedin.com/v2"

def upload_image_to_linkedin(image_path, text):
    # Step 1: Register the upload
    register_upload_url = f"{API_BASE_URL}/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    upload_data = {
        "registerUploadRequest": {
            "owner": author,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [
                {
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER",
                }
            ],
            "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"],
        }
    }

    response = requests.post(register_upload_url, json=upload_data, headers=headers)
    response.raise_for_status()
    upload_info = response.json()
    print(upload_info)

    upload_url = upload_info["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = upload_info["value"]["asset"]

    # Step 2: Upload the image
    with open(image_path, "rb") as image_file:
        upload_response = requests.put(upload_url, data=image_file)
        upload_response.raise_for_status()

    # Step 3: Create a post with the uploaded image
    post_url = f"{API_BASE_URL}/ugcPosts"
    post_data = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE",
                "media": [{"status": "READY", "description": {"text": text}, "media": asset}],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    post_response = requests.post(post_url, json=post_data, headers=headers)
    post_response.raise_for_status()

    print("Image uploaded and post created successfully!")

# Read in the text from linkedin_post.txt
with open("linkedin_post.txt", "r", encoding='utf-8') as file:
    post_text = file.read().strip()

# Usage
upload_image_to_linkedin("image.png", post_text)
# upload_image_to_linkedin("image.png", "Sign up for Intro to Agentic Programming meetup on Jan 22nd at 7pm EST. Register here: https://meetu.ps/e/NKsDL/QJYgJ/i")
