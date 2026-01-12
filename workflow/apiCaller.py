import random
import time

from openai import OpenAI
from openai import AsyncOpenAI

client = OpenAI()

async_client = AsyncOpenAI()


async def call_llm_async(prompt, system_prompt="You are a helpful, respectful and honest assistant."):
    completion = await async_client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        top_p=1,
        max_completion_tokens=2048,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": system_prompt}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    )

    return completion.choices[0].message.content


def call_api(prompt, system_prompt="You are a helpful, respectful and honest assistant."):
    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        top_p=1,
        max_completion_tokens=2048,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "text"
        },
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt
                    }
                ]
            },
        ]
    )

    return completion.choices[0].message.content
    # return random.choice(["Yes", "No"])
