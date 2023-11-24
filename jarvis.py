
from openai import OpenAI
import pyttsx3
import speech_recognition as sr
import os
from playsound import playsound
from dotenv import load_dotenv
from jarvis_functions import *
import json
import random

load_dotenv()
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.environ['OPENAI_API_KEY']
)
messages=[
    {"role": "system", "content": "You are a laid back and chill friend. You respond with casual statements and are friendly."},
    {"role": "user", "content": "Turn on my lights"},
  ]
function_descriptions = [
    {
        "name": "turn_all_lights",
        "description": "Turn on or off all the floor Govee lights via the api",
        "parameters": {
            "type": "object",
            "properties": {
                "turn": {
                    "type": "string",
                    "description": "on or off",
                },
            },
            "required": ["turn"],
        },
    },
    {
        "name": "set_color",
        "description": "Set the color of the floor Govee lights by taking a phrase or a word to describe a color and converting into three values for RGB",
        "parameters": {
            "type": "object",
            "properties": {
                "r": {
                    "type": "integer",
                    "description": "number between 0 and 255",
                },
                "g": {
                    "type": "integer",
                    "description": "number between 0 and 255",
                },
                "b": {
                    "type": "integer",
                    "description": "number between 0 and 255",
                },
            },
            "required": ["r", "g", "b"],
        },
    }
]
confirmation_phrases=[
    "Consider it done boss!",
    "Sure thing!",
    "No problem!",
    "I'm on it!",
]
engine = pyttsx3.init("dummy")

r = sr.Recognizer()
mic = sr.Microphone()


conversation = ""
user_name = "You"
bot_name = "assistant"
messages=[ #max length? say 4 messages
    {"role": "system", "content": "You are a laid back and chill friend. You respond with casual statements and are friendly."},
    
  ]



while True:
    with mic as source:
        print("\nlistening...")
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)
    print("no longer listening.\n")

    try:
        print("recognizing...")
        user_input = r.recognize_google(audio)
        print("You: " + user_input)
    except:
        continue
    
    #create a new dictionary for the user's message
    user_message = {"role": "user", "content": user_input}
    if len(messages) > 4:
        messages.pop(0)
    messages.append(user_message)
    # fetch response from open AI api
    response = client.chat.completions.create(
        model='gpt-3.5-turbo', 
        functions=function_descriptions,
        messages=messages,
        function_call="auto"
        )
    
    if response.choices[0].message.content == None:
        response_str = random.choice(confirmation_phrases)
        api_response = response.choices[0].message
        if api_response.function_call.name == "turn_all_lights":
            light_status = json.loads(api_response.function_call.arguments).get("turn")
            print("...turning lights", light_status + "...")
            turn_all_lights(light_status)
        elif api_response.function_call.name == "set_color":
            color = json.loads(api_response.function_call.arguments)
            print("...changing color...")
            change_all_lights_color(color)
    else:
        response_str = response.choices[0].message.content


    #create a new dictionary for the bot's message
    bot_message = {"role": bot_name, "content": response_str}
    if len(messages) > 4:
        messages.pop(0)
    messages.append(bot_message)
    vocal_response = client.audio.speech.create(
    model="tts-1",
    voice="fable",
    input=response_str,
    )  
    print("Jarvis" + ": " + response_str)
    vocal_response.stream_to_file("output.mp3")


    playsound("output.mp3")
    engine.runAndWait()