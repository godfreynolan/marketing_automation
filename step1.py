import feedparser
import requests
from openai import OpenAI
import config

def read_rss_feed(url):
    """Reads and parses an RSS feed from the given URL."""
    message = "Read our newest blog to learn about "
    try:
        feed = feedparser.parse(url)

        # Check for parsing errors
        if feed.bozo:
            print("Error parsing feed:", feed.bozo_exception)
            return

        # Loop through each entry in the feed
        for entry in feed.entries:
            message += f"{entry.title}, click here {entry.link}"
            image = entry.media_content[0]['url']
            # we just want the most recent entry
            return message, image

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # URL of the RSS feed
    rss_url = "http://fetchrss.com/rss/66309525bc0efe2a0d627e22663094e96626f23425104ec3.xml"

    # Read and parse the RSS feed
    msg, img = read_rss_feed(rss_url)
    try:
        # Send a GET request to the URL
        response = requests.get(img, stream=True)
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

    # get ChatGPT to generate a linkedin post
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    openai_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful marketing assistant. Use hashtags. Use any image URLs provided for context."},
            {"role": "user", "content": msg},
        ]
    )
    print(openai_response.choices[0].message.content)
    # print(msg)
    # print(img)

    with open('linkedin_post.txt', 'w', encoding='utf-8') as file:
        file.write(openai_response.choices[0].message.content)