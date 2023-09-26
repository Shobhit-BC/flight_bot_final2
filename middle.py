from flask import Flask, request
import json
from hiting import hit2
from mongo_db_s import db_ses_fetch,bd_ses_append_user,db_ses_response


app = Flask(__name__)

@app.route("/", methods=["POST","GET"])
def index():
  print(request.method)
  
  if request.method == "POST":
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
      data = json.loads(request.data)
      session_id=data['session_id']
      prompt=data['prompt']
      i=db_ses_fetch(session_id)
      bd_ses_append_user(session_id,prompt)
      last2=i[1]
      mandatory_extracted_json=i[0]
      non_mandatory_extracted_json=i[2]
      response=hit2(session_id,prompt,last2,mandatory_extracted_json,non_mandatory_extracted_json)
      json_obj = json.loads(response)
      response=json_obj["response"]
      mandatory_extracted_json=json_obj["mandatory_extracted_json"]
      non_mandatory_extracted_json=json_obj["non_mandatory_extracted_json"]
      session_id=json_obj["session_id"]
      db_ses_response(mandatory_extracted_json,non_mandatory_extracted_json,response,session_id)
      return (
        {
          "response":response
        }
      )


if __name__ == "__main__":
     app.run(debug=True,port=5002)

