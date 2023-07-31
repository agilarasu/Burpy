import requests
import sys
import argparse
import socket
import json
from pymongo import MongoClient
import tabulate
#connect to the database
client = MongoClient('localhost', 27017)
db = client['repeater']
collection = db['responses']

#parse command line arguments
def get_args():
    parser = argparse.ArgumentParser(description="Command-line arguments for repeater.py")
    
    parser.add_argument("-m", "--method", required=True, help="HTTP method (e.g., GET, POST, etc.)")
    parser.add_argument("-u", "--url", required=True, help="URL for the HTTP request")
    parser.add_argument("-p", "--payload", required=False, help="Path to the payload file")
    parser.add_argument("-H", "--headers", nargs='*', help="Optional headers (key:value pairs)")
    parser.add_argument("-b", "--body", required=False, help="Body of the request")

    
    args = parser.parse_args()
    
    return args.method, args.url, args.payload, args.headers, args.body


def check_fuzz(body,headers,url):
    if body:
        if "!FUZZ" in body:
            return "body"
    if headers:
        for header in headers:
            if "!FUZZ" in header:
                return "headers["+header+"]"
    if url:
        if "!FUZZ" in url:
            return "url"
    print("Error: !FUZZ not found in body, headers or url")
    sys.exit(1)
#send request to the url with the method and traverse through all payload with 'while True' if given
def send_request(method, url, payload_path, headers, body,var):
    #check if the url is valid
    try:
        socket.gethostbyname(url.split("//")[1].split("/")[0])
    except socket.gaierror:
        print(f"Error: Cannot resolve host '{url}'")
        sys.exit(1)

    if payload_path:
        with open(payload_path, "r") as payload_file:
            payload = payload_file.read().splitlines()
            if var=="body":
                for line in payload:
                    r=(requests.request(method, url, data=body.replace("!FUZZ",line), headers=headers))
                    print(line,"-->",r.status_code)
                    collection.insert_one({"payload":line,"status":r.status_code,"headers":r.headers,"length":len(r.text),"body":r.text})
                    
            elif var=="url":
                for line in payload:
                    r=(requests.request(method, url.replace("!FUZZ",line), data=body, headers=headers))
                    print(line,"-->",r.status_code)
                    collection.insert_one({"payload":line,"status":r.status_code,"headers":r.headers,"length":len(r.text),"body":r.text})
                    
            elif var.startswith("headers"):
                for line in payload:
                    r=(requests.request(method, url, data=body, headers=headers.replace("!FUZZ",line)))
                    print(line,"-->",r.status_code)
                    collection.insert_one({"payload":line,"status":r.status_code,"headers":r.headers,"length":len(r.text),"body":r.text})
            else:
                pass
        return 0
                    
    else:
        r = requests.request(method, url, data=body, headers=headers)
        collection.insert_one({"payload":None,"status":r.status_code,"headers":r.headers,"length":len(r.text),"body":r.text})
        return 0


def main():
    method, url, payload_path, headers,body = get_args()
    if payload_path:
        with open("index.json", "r") as index_file:
            index = json.load(index_file)
            if payload_path in index["payloads"]:
                payload_path = index["payloads"][payload_path]

    if body==None:
        body=""
    #check if the payload contains !FUZZ
    if payload_path:
        var = check_fuzz(body,headers,url)
    else:
        var=""

    print("Method:", method)
    print("URL:", url)
    print("Headers:", headers)
    print("Body:", body)
    print("Payload Path:", payload_path)
    
    print("Do you want to continue? (y/n)")
    if input() != "y":
        sys.exit(0)

    response = send_request(method, url, payload_path, headers,body,var)
    
    
    myjson=[]
    for doc in collection.find({},{"body":0}):
        myjson.append(doc)
    table=tabulate.tabulate(myjson,headers="keys",tablefmt="github")
    print(table)
if __name__ == "__main__":
    main()