from pymongo import MongoClient
client = MongoClient("localhost", 27017)
 
# used to store bot response in chat history and json in database
def db_ses_response(mandatory_json,non_mandatory_json,bot_response,user_id):
    db = client["Try"]
    chat_history_co = db["user_data"]
    doc_json = chat_history_co.find_one({"_id": user_id})
    query = {"_id": user_id}  

    update = {

        "$push": {

            "conversation": {"role": "assistant", "content": bot_response}

        }

    }
    chat_history_co.update_one(query, update)
    if doc_json:
        update2 = {

            "$set": {
                "mandatory_json":mandatory_json,
                "non_mandatory_json":non_mandatory_json
            }

        }
        chat_history_co.update_one(query, update2)
    
        return "done"

    else:

        response_data2 = {
            "_id": user_id,
            "mandatory_json":mandatory_json,
            "non_mandatory_json":non_mandatory_json        
        }

        chat_history_co.insert_one(response_data2)

        return "done"

# used to store bot user-prompt in chat history and database
def bd_ses_append_user(user_id,prompt):
    db = client["Try"]
    chat_history_co = db["user_data"]
    doc_chat = chat_history_co.find_one({"_id": user_id})
    if doc_chat:
        query = {"_id": user_id}  

        update = {

            "$push": {

                "conversation": {"role": "user", "content": prompt}

            }

        }
        chat_history_co.update_one(query, update)

        return "done"

    else:
        response_data = {
            "_id": user_id,
            "conversation":[{"role": "user", "content": prompt}]
        }

        chat_history_co.insert_one(response_data)

        return "done"    

# extracting details from database
def db_ses_fetch(user_id):
    db = client["Try"] 
    chat_history_co = db["user_data"]
    doc_chat = chat_history_co.find_one({"_id": user_id})
    if doc_chat:
        mandatory_json_fetched = doc_chat.get('mandatory_json')
        extracted_non_mandatory_json=doc_chat.get('non_mandatory_json')
        entry = doc_chat.get('conversation')
        last2=  (entry[-1:])
        print(type(last2))
        return mandatory_json_fetched,last2,extracted_non_mandatory_json

    else:
        
    
        mandatory_json_fetched = {
            "Departure City":"",
            "Destination City": "",
            "Travel Date": ""
            }
        extracted_non_mandatory_json = {
            "Class": "",
            "Trip type": "",
            "Number of stops": "",
            "Airlines":"",
            "Price range":"",
            "Refundable":"",
            "Number of passengers":""
            }
        last2=[]
        return mandatory_json_fetched,last2,extracted_non_mandatory_json





