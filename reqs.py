import requests
from dotenv import load_dotenv
import os
load_dotenv()
api=os.getenv("API_KEY")
quote_uri="https://quotes-api-self.vercel.app/quote"
class Req:
    def __init__(self):
        response=requests.get(url=quote_uri)
        if response.status_code!=200:
            self.error=response.raise_for_status()
            data={'quote':"Technology is best when it brings people together",
                  'author':"Matt Mullenweg"}
        else:
            data=response.json()
        self.quote=data['quote']
        self.author=data['author']
        


        