import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class EmailClassification(BaseModel):
    category: Literal[
        "spam",
        "sales",
        "discounts",
        "billing",
        "info"
    ]

    confidence: float = Field(ge=0, le=1)

    reason: str


def classify_email(email: str) -> EmailClassification:
    if not email.strip():
        raise ValueError("Email content cannot be empty")

    prompt = f"""
Classify the following email.

Allowed categories:
- spam
- sales
- discounts
- billing
- info

Return ONLY valid JSON with this structure:

{{
    "category": "...",
    "confidence": 0.0,
    "reason": "..."
}}

Email:
{email}
"""

    gemini_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    parsed_json = json.loads(gemini_response.text)

    validated_response = EmailClassification(**parsed_json)

    return validated_response


test_email = """
Hi team,

I would like to know your pricing for enterprise plans.

Best regards,
John
"""

result = classify_email(test_email)

print(result)