import json
import requests
import os
import config

# Define the API endpoint URL and the authorization token
url = "https://api.openai.com/v1/images/generations"
token = os.environ['OPENAI_API_KEY']

# Define the input prompt that will guide the image generation
prompt = "Generate a picture of a happy kitten playing with a ball of yarn."

# Define the parameters for the image generation
data = {
    "model": "image-alpha-001",
    "prompt": prompt,
    "num_images": 1,
    "size": "256x256",
    "response_format": "url"
}

# Set the headers for the request, including the authorization token
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# Send the POST request to the API endpoint with the input data and headers
response = requests.post(url, data=json.dumps(data), headers=headers)

# Get the URL of the generated image from the response
if response.status_code == 200:
    result = response.json()
    image_url = result["data"][0]["url"]
    print("Generated image URL:", image_url)
else:
    print("Error:", response.status_code)


