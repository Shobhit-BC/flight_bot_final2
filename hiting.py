import requests
from requests.structures import CaseInsensitiveDict

url = "http://127.0.0.1:5000"
# url = "https://api-flight-46lp.onrender.com"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"

#calling middle api using requests
def hit(prompt,session_id):
    url = "http://127.0.0.1:5002"

    json1={
        "prompt":prompt,
        "session_id":session_id,
    }

    resp = requests.post(url, headers=headers,json=json1,allow_redirects=False)
    return(resp.text)

#calling akshay api using requests
def hit2(session_id,prompt,last2,mandatory_extracted_json,non_mandatory_extracted_json):
    
    url = "http://127.0.0.1:5001"

    json1={
        "prompt":prompt,
        "session_id":session_id,
        "last2":last2,
        "mandatory_extracted_json":mandatory_extracted_json,
        "non_mandatory_extracted_json":non_mandatory_extracted_json
    }

    resp = requests.post(url, headers=headers,json=json1,allow_redirects=False)
    return(resp.text)
