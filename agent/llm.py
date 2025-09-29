import os
from groq import Groq

def calling_groq(message):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    return(chat_completion.choices[0].message.content)

def calling_groq_jenkins(message):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        messages= message,
        model="llama-3.3-70b-versatile",
    )

    return(chat_completion.choices[0].message.content)