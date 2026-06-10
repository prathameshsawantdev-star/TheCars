from time import sleep 
from google import genai 
import json 
from models.cars import Car
from config import BaseConfig
from beanie import PydanticObjectId
import resend

settings = BaseConfig()
resend.api_key = settings.RESEND_API_KEY

client = genai.Client(api_key=settings.GEMINI_API_KEY)
def generate_prompt(brand: str, model: str, year: int):
    return f"""
    You are a helpful car sales assistant.
    Describe the {brand} {model} from {year} in a playful but realistic manner.
    Return ONLY valid JSON.

    Schema:
    {{
    "description": "string",
    "pros": [
        "string",
        "string",
        "string",
        "string",
        "string"
    ],
    "cons": [
        "string",
        "string",
        "string",
        "string",
        "string"
    ]
    }}

    Requirements:
    - description must be at least 350 characters
    - pros must contain exactly 5 items
    - cons must contain exactly 5 items
    - each pro and con must be under 12 words
    - pros should sound positive
    - cons should sound mildly negative
    - return JSON only, no markdown, no explanations
    """
import asyncio
import json

def generate_ai_opinion(
    id: str,
    brand: str,
    make: str,
    year: int,
    picture_url: str
) -> None:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=generate_prompt(brand, make, year)
        )

        car_info = json.loads(response.text)
        print("car_info", car_info)
        asyncio.run(
            Car.find(
                Car.brand == brand,
                Car.make == make,
                Car.year == year
            ).set(
                {
                    Car.description: car_info["description"],
                    Car.pro: car_info["pros"],
                    Car.con: car_info["cons"],
                }
            )
        )

        def generate_email():
            pros_list = "<br>".join([f"- {pro}" for pro in 
            car_info["pros"]])
            cons_list = "<br>".join([f"- {con}" for con in 
            car_info["cons"]])
            return f"""
                Hello,
                We have a new car for you: {brand} {make} from 
                {year}.
                <p><img src="{picture_url}"/></p>
                {car_info['description']}
                <h3>Pros</h3>
                {pros_list}
                <h3>Cons</h3>
                {cons_list}
            """

    

    except Exception as e:
        print(e)