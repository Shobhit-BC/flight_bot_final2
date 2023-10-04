import openai
import datetime
from dateutil import parser
from datetime import date
import os
import json
from flask import Flask, request, render_template

openai.api_key = os.getenv("OPENAI_API_KEY")
def get_todays_date():
    today = date.today()
    return today.strftime("%Y-%m-%d")

live_date = get_todays_date()

flight_booking_prompt = "You are now chatting with the Flight Booking Assistant. Please provide your flight booking details or ask questions related to flight booking."



def chat_with_flight_booking_bot(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

def chat_with_bot_non_mandatory(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

def get_travel_date(user_input):
    today = datetime.date.today()
    # tomorrow = today + datetime.timedelta(days=1)

    try:
        date_obj = parser.parse(user_input, fuzzy=False)

        if (date_obj.year < today.year) or (date_obj.year == today.year and date_obj.month < today.month) or (date_obj.year == today.year and date_obj.month == today.month and date_obj.day < today.day):

            date_obj = date_obj.replace(year=today.year + 1)  # Adjust the year to the next year

        return date_obj.strftime("%Y/%m/%d")
    except ValueError:
        return None

#function to combine both the bots JSON response
def extract_dictionary_from_string(s):
    start_index = s.find('{')
    end_index = s.rfind('}') + 1
    dictionary_string = s[start_index:end_index]
    return dictionary_string
def extract_resp(s):
    if(s.find('Here is your updated JSON:')!=-1):
      start_index = s.find('Here is your')
      end_index = s.rfind('}') + 1
      dictionary_string1 = s[0:start_index] 
      dictionary_string2=s[end_index:]
      dictionary_string=dictionary_string1+dictionary_string2
      return dictionary_string
    else:
        return s

intent_bot_instructions = '''You're working as a intent classifier. Your duty is to understand the intent of user's input and carry forward the conversation according to following rules:
Rule - 1: There are two different bots for 2 different intents which will be working based on your response, one of the bot handles all flight bookings related query and second bot handles all other types of query.
Rule - 2: If you find the intent of the user's input as flight related query or anything related to flight, then just return a single word "flight", nothing other than that.
Rule - 3: If you find the intent of the user's input as anything other than flight related, then juist return a single word "non-flight", nothing other than that.
'''


def mand_prompt(extracted_mandatory_json):
  additional_instructions = f'''Remember, as a Flight Booking Assistant, your primary focus is to assist with flight booking and flight booking-related questions. If the user asks non-flight booking-related questions, kindly ask them to rephrase the query to be flight booking-related.
  Today's date is ```{live_date}```.

  Tomorrow's date is just the next date of ```{live_date}```.

  

  - To accomplish this task, follow the following steps sequentially:
  - Make sure you already provide a json.

  

  ```
  
  Step 1: Check for keys with missing values in ```{extracted_mandatory_json}``` and ask the user for that value. \

  Step 2: Next, analyze the user input and extract features for the keys mentioned in ```{extracted_mandatory_json}``` and update it in ```{extracted_mandatory_json}```.\

  Step 3: Respond the user with query to provide the value for keys having missing values in ```{extracted_mandatory_json}```\
  Along with the query also provide this updated JSON. \

  Step 4: From the user input extract the features required to fill the corresponding values of ```{extracted_mandatory_json}```, and update the JSON with information provided by user.\

  Step 5: Again check the updated JSON for missing values and respond with the query to ask for value of remaining keys, along with the updated JSON.\

  ```

  

  - Don't ask for any other information/features from the user. Extract the information (departure city, destination city and travel date only) from user input and update the JSON with extracted feature every time.\

  

  - Remeber to always respond with the updated JSON and query.\

  

  - If the user provides any extra information like class, trip type, price, no. of passengers, airlines etc. ignore all the other informations and strictly focus on only the 3 values (departure city, destination city and travel date) required to fill JSON.\

  

  - Never ask the user for values that are already filled in ```{extracted_mandatory_json}```. You must refer and check ```{extracted_mandatory_json}``` properly before asking user for the values and also while extracting values from user input.\

  

  - Please perform the feature extraction properly with 100% efficiency. For getting departure city and destination city focus on "to" and "from" and also analyze properly with your intelligence in all possible manners. Don't dissapoint user by asking again the already provided information.\

  

  - Please refer the examples below for better understanding:

  

  ```

  example 1:

  

  ```

  <User>: Book a flight to Delhi

  

  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:

  

  1. Departure city?

  2. Travel date?

  

  Here is your updated JSON:

  {{

    'Departure City': ' ',

    'Destination City': 'Delhi',

    'Travel Date': ' '

  }}

  

  <User>: From Mumbai on 9th June

  

  <Flight Booking Assistant>: Thank you for providing the information. Here is your updated JSON:

  

  {{

    'Departure City': 'Mumbai',

    'Destination City': 'Delhi',

    'Travel Date': '2024-06-09'

  }}

  ```

  example-2:

  ```

  <User>: Book a flight 

  

  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:

  1. Departure city?

  2. Destination city?

  3. Travel date?

  

  Here is your updated JSON:

  {{

    "Departure City": "",

    "Destination City": "",

    "Travel Date": ""

  }}

  
  <User>: From bangkok

  

  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:

  1. Destination city?

  2. Travel date? 
  
  Here is your updated information:

  {{

    "Departure City": "Bangkok",

    "Destination City": "",

    "Travel Date": ""

  }}

  <User>: To goa

  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:

  1. Travel date? 
  
  Here is your updated information:

  {{

    "Departure City": "Bangkok",

    "Destination City": "Goa",

    "Travel Date": ""

  }}

  <User>: on 25 dec

  <Flight Booking Assistant>: Thank you for providing the information. 

  Here is your updated JSON:

  {{

    "Departure City": "Bangkok",

    "Destination City": "Goa",

    "Travel Date": "2023-12-25"

  }}



  ```

  example-3:

  ```

  <User>: Book a flight to Delhi for tomorrow

  

  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:

  
  

  Here is your updated JSON:

  {{

      "Departure City": "",

      "Destination City": "Delhi",

      "Travel Date": "2023-09-14"

  }}

  

  <User>: From London

  

  <Flight Booking Assistant>: Thank you for providing the information. Here is your updated JSON:

  

  Here is your updated JSON:

  {{

    "Departure City": "London",

    "Destination City": "Delhi",

    "Travel Date": "2023-09-14"

  }}

  ```

  example-4:

  ```

  <User>: Book a flight from London to Mumbai on 11th June

  

  <Flight Booking Assistant>: Thank you for providing the information. Here is your updated JSON:

  

  {{

    "Departure City": "London",

    "Destination City": "Mumbai",

    "Travel Date": "2024-06-11"

  }}

  ```

  

  If you have all the details already present in {extracted_mandatory_json} then just thank the user.
  

  '''

  return additional_instructions

def non_mand_prompt(non_mandatory_extracted_json):
  instructions_non_mand = f'''
  - As a Flight Booking Assistant, your only job is to extract the key features mentioned in ```{non_mandatory_extracted_json}```  from user input and update in ```{non_mandatory_extracted_json}``` and return the updated JSON to user.

  - Never ask anything from the user. Only return the updated JSON every time.

  - In ```{non_mandatory_extracted_json}```, for keys with no value, just return ```{""}``` value for that key, don't use any default value.

  - Never miss responding with the updated JSON, don't loose values for the already provided json.

  '''

  return instructions_non_mand

flight_booking_prompt = "You are now chatting with the Flight Booking Assistant. Please provide your flight booking details or ask questions related to flight booking."


   

 
#intent classifier bot
def intent_bot(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

intent_bot_msg = [
        {"role": "system", "content": intent_bot_instructions}
    ]

greetings_bot_instructions = "Your task is to keep the user engaged in a small talk"

#small talk/greetings bot
def greetings_bot(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

greetings_bot_msg = [
        {"role": "system", "content": greetings_bot_instructions}
    ]

def main(user_input,last2,mandatory_extracted_json,non_mandatory_extracted_json,session_id):
  if user_input.lower() in ["exit", "quit", "bye"]:     
    return ({"response":"Have a happy and calm Journey!",
          "mandatory_json":mandatory_extracted_json
          })
  intent_bot_response = intent_bot(intent_bot_msg + last2)


  if intent_bot_response == "non-flight":
    print("non f")
      
    greetings_bot_response = greetings_bot(greetings_bot_msg + last2+[{"role": "user", "content": user_input}])

    return (        {
        "response":greetings_bot_response,
        "session_id":session_id,
        "mandatory_extracted_json":mandatory_extracted_json,
        "non_mandatory_extracted_json":non_mandatory_extracted_json,
        "greet":True

        })
  

  else:
    print("flight")
    conversation1 = [{"role": "system", "content": non_mand_prompt(non_mandatory_extracted_json)}]
    conversation = [{"role": "system", "content": flight_booking_prompt},{"role": "system", "content": mand_prompt(mandatory_extracted_json)}]

    travel_date = None

    if travel_date == None:

      travel_date = get_travel_date(user_input)

    if travel_date:

      conversation.append({"role": "user", "content": user_input + f"Travel Date: {travel_date}"})

    else:

      conversation.append({"role": "user", "content": user_input})

    bot_response = chat_with_flight_booking_bot(conversation)
    bot_response1 = chat_with_bot_non_mandatory(conversation1 +[{"role": "user", "content": user_input}])


    if "{" and "}" in bot_response:
      print(f"extraced_json:{bot_response}")
      extracted_json = (extract_dictionary_from_string(bot_response))
      valid_json_string2 = extracted_json.replace("'", "\"")
      extracted_json_mandatory = json.loads(valid_json_string2)
      response=extract_resp(bot_response)
    else:
      extracted_json_mandatory=mandatory_extracted_json
      response=extract_resp(bot_response)
    if "{" and "}" in bot_response1:
      print(f"extraced_josn_nmand:{bot_response1}")
      valid_json_string = bot_response1.replace("'", "\"")
      extracted_json_nonmandatory = json.loads(valid_json_string)

    else:
      extracted_json_nonmandatory=non_mandatory_extracted_json
      print("nomand_Json_NF")


    return (
      {
      "response":response,
      "session_id":session_id,
      "mandatory_extracted_json":extracted_json_mandatory,
      "non_mandatory_extracted_json":extracted_json_nonmandatory,
      "greet":False
      }
    )

 

app = Flask(__name__)

@app.route("/", methods=["POST","GET"])
def index():
  print(request.method)
  
  if request.method == "POST":
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
      data = json.loads(request.data)
      session_id=data['session_id']
      user_input= data['prompt']

      last2=data['last2']
      mandatory_extracted_json=data['mandatory_extracted_json']
      non_mandatory_extracted_json=data['non_mandatory_extracted_json']
      print(f"non_mandatory_extracted_json: {non_mandatory_extracted_json}") 
      print(f"last2: {last2}") 

    return main(user_input,last2,mandatory_extracted_json,non_mandatory_extracted_json,session_id)
  return render_template("index.html")

     
    

if __name__ == "__main__":
     app.run(debug=True,port=5001)
