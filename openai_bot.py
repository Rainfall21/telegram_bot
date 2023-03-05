import openai
import os


def chatting(message):
    openai.api_key = os.getenv('OPENAI_KEY')
    model_engine = "text-davinci-003"
    response = openai.Completion.create(
        model=model_engine,
        prompt=message,
        temperature=0.9,
        max_tokens=1024,
        top_p=1.0,
        frequency_penalty=0.0,
        stop=['You:']
    )
    return response['choices'][0]['text']