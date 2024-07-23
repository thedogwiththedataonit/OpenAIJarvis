from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow, task, tool


load_dotenv()
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.environ['OPENAI_API_KEY']
)

LLMObs.enable(
  ml_app="Jarvis",
  api_key= os.environ['DD_API_KEY'],
  site="datadoghq.com",
  agentless_enabled=True,
)

messages=[
    {"role": "system", "content": "You are a laid back and chill friend. You respond with casual statements and are friendly."},
  ]
functions = [
    {
        "name": "check_availability",
        "description": "Check the availability of a product in the inventory",
        "parameters": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "the product name",
                },

            },
            "required": ["product"],
        },
    }
]

@tool(name="check_availability")
def check_availability(product):
    print(f"Checking availability of {product}")
     
    return "The product is available"

@workflow
def chat_completion(functions, messages, new_message):
    messages.append(new_message)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        functions=functions, # ASSISTANT FUNCTION CALLS
        messages=messages,
        function_call="auto"
        )
    print(response.choices[0].message)
    if response.choices[0].message.function_call:
        api_response = response.choices[0].message
        # send a log to datadog
        if api_response.function_call.name == "check_availability":
            product = json.loads(api_response.function_call.arguments).get("product")
            
            response_str = check_availability(product)

    else:
        response_str = response.choices[0].message.content
    
    LLMObs.annotate(
        span=None,
        input_data=new_message['content'],
        output_data=response_str,
        tags={"host": "host_name"},
    )
    span_context = LLMObs.export_span(span=None)
    LLMObs.submit_evaluation(
        span_context,
        label="sentiment",
        metric_type="score",
        value=10,
    )
    return response_str

#new_message = {"role": "user", "content": "what the hell is your problem! You cant do anything right AI sucks!"}
new_message = {"role": "user", "content": "what is the availability of the chicken product?"}
print(chat_completion(functions, messages, new_message))
