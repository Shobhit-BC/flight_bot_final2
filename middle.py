from flask import Flask, request
import json
from hiting import hit2
from mongo_db_s import db_ses_fetch,bd_ses_append_user,db_ses_response


app = Flask(__name__)

# middle.py is the intermidator between ui and akshay api 
# it sends a request to akshay api with all the previous details from the database
#it fetches annd update data in mongodb

@app.route("/", methods=["POST","GET"])
def index():
  print(request.method)

  # checking if request is of POST type
  if request.method == "POST":
    content_type = request.headers.get('Content-Type')

    # checking if request recieved is of json type
    if (content_type == 'application/json'):

      #extracting all the data from json recieved from ui
      data = json.loads(request.data)
      session_id=data['session_id']
      prompt=data['prompt']

      #fetching all the details from database using session id
      i2=db_ses_fetch(session_id)

      #preparing last 2 chat history
      last2=(i2[1])+[{"role": "user", "content": prompt}]
      mandatory_extracted_json=i2[0]
      non_mandatory_extracted_json=i2[2]

      #calling akshay api
      response=hit2(session_id,prompt,last2,mandatory_extracted_json,non_mandatory_extracted_json)

      #extracting all the data from json recieved from akshay api
      json_obj = json.loads(response)
      response=json_obj["response"]
      greet=json_obj["greet"]
      mandatory_extracted_json1=json_obj["mandatory_extracted_json"]
      non_mandatory_extracted_json1=json_obj["non_mandatory_extracted_json"]
      # initializing non_mandatory_extracted_json2 to store final non-mandatory json
      non_mandatory_extracted_json2={}

      # checking if existing details in json is not removed by akshay api
      if (mandatory_extracted_json["Departure City"]!="" and mandatory_extracted_json1["Departure City"]==""):
        mandatory_extracted_json1["Departure City"]=mandatory_extracted_json["Departure City"]
      if(mandatory_extracted_json["Destination City"]!="" and mandatory_extracted_json1["Destination City"]==""):
        mandatory_extracted_json1["Destination City"]=mandatory_extracted_json["Destination City"]
      
      # checking if no extra info is added in json
      for key,value in non_mandatory_extracted_json1.items():
          if key in non_mandatory_extracted_json:
              non_mandatory_extracted_json2[key]=value
      session_id=json_obj["session_id"]

      #checking if user prompt was for greet bot or fight bot
      if(greet==False):
        bd_ses_append_user(session_id,prompt)
        db_ses_response(mandatory_extracted_json1,non_mandatory_extracted_json2,response,session_id)
      
      return (
        {
          "response":response
        }
      )


if __name__ == "__main__":
     app.run(debug=True,port=5002)

