import os
from typing import Union, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from enum import Enum

from openai import OpenAI, APIStatusError, APITimeoutError, RateLimitError
from tenacity import retry, stop_after_attempt, retry_if_exception_type, RetryError

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Styles(str, Enum):
    sad = "sad"
    scary = "scary"
    serious = "serious"
    adventourous = "adventourous"

class Story(BaseModel):
    topic: str
    style: Union[None, Styles]

app = FastAPI(
    title="Checko App",
    description="This is a simple Checko App ✔️",
)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

@retry(stop=stop_after_attempt(3), reraise=True, retry=retry_if_exception_type((APITimeoutError, RateLimitError)))
def generate_story(prompt: str):
    result = openai_client.chat.completions.create(
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

    return result.choices[0].message.content

@app.post("/write_story")
def write_story(data: Story):
    try:
        prompt = f"write a story under 500 words about {data.topic}"
        if data.style:
            prompt += f" in the style of {data.style}"
            
        story = generate_story(prompt)

        if story:
            rewrite_prompt = f"Rewrite this story in a funny way: {story}"
            funny_story = generate_story(rewrite_prompt)
            if funny_story:
                return {
                    "topic": data.topic,
                    "style": data.style,
                    "original_story": story,
                    "funny_story": funny_story
                }
        
        else:
            return {"error": "Failed to generate story."}
        
    except APITimeoutError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=e.message)
    
    except RateLimitError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message)

    except APIStatusError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
# @app.post("/write_story")
# def write_story(topic: Annotated[str, Form()], style: Annotated[Styles, Form()]):
#     try:
#         prompt = f"write a story under 500 words about {topic}"
#         if style:
#             prompt += f" in the style of {style}"
            
#         story = generate_story(prompt)

#         if story:
#             rewrite_prompt = f"Rewrite this story in a funny way: {story}"
#             funny_story = generate_story(rewrite_prompt)
#             if funny_story:
#                 return {
#                     "topic": topic,
#                     "style": style,
#                     "original_story": story,
#                     "funny_story": funny_story
#                 }
        
#         else:
#             return {"error": "Failed to generate story."}
        
#     except APITimeoutError as e:
#         raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=e.message)
    
#     except RateLimitError as e:
#         raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message)

#     except APIStatusError as e:
#         raise HTTPException(status_code=e.status_code, detail=e.message)
