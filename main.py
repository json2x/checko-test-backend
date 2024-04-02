from typing import Union, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from enum import Enum
import uvicorn

from openai import OpenAI, APIStatusError, APITimeoutError, RateLimitError
from tenacity import retry, stop_after_attempt, retry_if_exception_type

OPENAI_API_KEY = ""

class Styles(str, Enum):
    sad = "sad"
    scary = "scary"
    serious = "serious"
    adventourous = "adventourous"

class Story(BaseModel):
    topic: str
    style: Union[None, Styles]
    story: Optional[str] = None

app = FastAPI(
    title="Checko App",
    description="This is a simple Checko App ✔️",
)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

@retry(stop=stop_after_attempt(3), retry=retry_if_exception_type((APITimeoutError, RateLimitError)))
def generate_story(prompt: str):
    result = openai_client.chat.completions(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an excellent writer and you have been tasked with writing a story about a topic base from the style requested by the user."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return result.choices[0].message["content"]

@app.post("/write_story")
def write_story(data: Story):
    try:
        prompt = f"write a story under 500 words about {data.topic}"
        if data.style:
            prompt += f" in the style of {data.style}"
            
        story = generate_story(prompt)

        if story:
            return {"story": story}
        
        else:
            return {"error": "Failed to generate story."}
    except APIStatusError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    
@app.get("/test")
def test():
    return {"message": "Checko App is working fine."}
