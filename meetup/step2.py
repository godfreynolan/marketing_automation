import requests
import config 
from openai import OpenAI
from datetime import datetime
from ln_oauth import auth, headers

# get the data from meetup.com (just one group for now)
ACCESS_TOKEN = config.MEETUP_ACCESS_TOKEN
# GraphQL query
query = 'query { groupByUrlname(urlname: "practical-chatgpt-api-programming") { name id upcomingEvents(input: {first: 1}) { pageInfo { hasNextPage hasPreviousPage startCursor endCursor } count edges { cursor node { id title eventUrl images { id baseUrl preview } venue { name } dateTime duration timezone endTime isOnline shortUrl } } } } }'
url = 'https://api.meetup.com/gql'
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
}

payload = {
    'query': query
}
response = requests.post(url, json=payload, headers=headers)

# Extracting required data
def parse_meetup_data(data):
    parsed_data = []
    group = data.get('data', {}).get('groupByUrlname', {})
    name = group.get('name', 'N/A')
    upcoming_events = group.get('upcomingEvents', {}).get('edges', [])

    for event in upcoming_events:
        node = event.get('node', {})
        title = node.get('title', 'N/A')
        short_url = node.get('shortUrl', 'N/A')
        date_time = node.get('dateTime', 'N/A')

        # Format the dateTime
        formatted_date_time = "N/A"
        if date_time != 'N/A':
            dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M%z")
            formatted_date_time = dt.strftime("%B %d").replace(" 0", " ") + ", at " + dt.strftime("%I%p").lstrip("0").lower()

        images = node.get('images', [])
        image_data = [
            {
                'image_id': img.get('id', 'N/A'),
                'base_url': img.get('baseUrl', 'N/A')
            } 
            for img in images
        ]

        parsed_data.append({
            'name': name,
            'title': title,
            'shortUrl': short_url,
            'dateTime': formatted_date_time,
            'images': image_data
        })

    return parsed_data

# Parsing and displaying the data
parsed_data = parse_meetup_data(response.json())
openai_user_message = "Create a LinkedIn post for the upcoming meetup event with the following information:"
for event in parsed_data:
    openai_user_message += f"Group Name: {event['name']}\n"
    openai_user_message += f"Event Title: {event['title']}\n"
    openai_user_message += f"Short URL: {event['shortUrl']}\n"
    openai_user_message += f"DateTime: {event['dateTime']}\n"
    for img in event['images']:
        # openai_user_message += f"Img: {img['base_url']}{img['image_id']}\n"
        url = f"{img['base_url']}{img['image_id']}"
        try:
            # Send a GET request to the URL
            response = requests.get(url, stream=True)
            # Check if the request was successful
            if response.status_code == 200:
                # Open the file in write-binary mode and write the content
                with open("image.png", "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"Image successfully downloaded")
            else:
                print(f"Failed to retrieve the image. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")

print(openai_user_message)


# get ChatGPT to generate a linkedin post
client = OpenAI(api_key=config.OPENAI_API_KEY)
openai_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful marketing assistant. Use hashtags. Use any image URLs provided for context."},
        {"role": "user", "content": openai_user_message},
    ]
)
print(openai_response.choices[0].message.content)

with open('linkedin_post.txt', 'w', encoding='utf-8') as file:
    file.write(openai_response.choices[0].message.content)
# post it to linkedin - step6.py






