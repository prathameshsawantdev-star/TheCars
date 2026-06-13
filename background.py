import json
import logging

from beanie import PydanticObjectId
from google import genai
import resend 

from config import BaseConfig
from models.cars import Car

settings = BaseConfig()
resend.api_key = settings.RESEND_API_KEY 

client = genai.Client(api_key=settings.GEMINI_API_KEY)

logger = logging.getLogger(__name__)


def generate_prompt(brand: str, make: str, year: int) -> str:
    return f"""
You are a helpful car sales assistant.

Describe the {brand} {make} from {year} in a playful but realistic manner.

Return ONLY valid JSON in the following format:

{{
    "description": "string",
    "pros": ["string"],
    "cons": ["string"]
}}

Requirements:
- description should be informative and engaging
- pros should sound positive
- cons should sound mildly negative
- return JSON only
"""


async def generate_ai_opinion(car_id: str) -> None:
    try:
        car = await Car.get(PydanticObjectId(car_id))

        if car is None:
            logger.warning("Car not found: %s", car_id)
            return

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=generate_prompt(
                car.brand,
                car.make,
                car.year,
            ),
        )
        
        text = response.text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        car_info = json.loads(text)
        print(car_info)

        car.description = car_info.get("description", "")

        car.pros = car_info.get("pros", [])

        car.cons = car_info.get("cons", [])

        await car.save()

        def generate_email():
            pros_list = "<br>".join([f"- {pro}" for pro in car_info["pros"]])
            cons_list = "<br>".join([f"- {con}" for con in car_info["cons"]])
            return f"""
                Hello,
                We have a new car for you: {car.brand} {car.make} from {car.year}.
                <p><img src="{car.picture_url}"/></p>{car_info['description']}
                <h3>Pros</h3>
                {pros_list}
                <h3>Cons</h3>
                {cons_list}
                """

        params: resend.Emails.SendParams = {
            "from": "TheCars <onboarding@resend.dev>",
            "to": ["phyttron6626@gmail.com"],
            "subject": "New car on Sail!",
            "html": generate_email()
            }
        
        try: 
            resend.Emails.send(params)
        except Exception as e: 
            print(e)

        logger.info(
            "Successfully generated AI opinion for %s",
            car_id, 
        )

    except Exception:
        logger.exception(
            "Failed to generate AI opinion for %s",
            car_id,
        )
        raise