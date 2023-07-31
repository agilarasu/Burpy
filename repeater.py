import requests
import sys
import argparse
import socket
import json

#parse command line arguments
def get_args():
    parser = argparse.ArgumentParser(description="Command-line arguments for repeater.py")
    
    parser.add_argument("-m", "--method", required=True, help="HTTP method (e.g., GET, POST, etc.)")
    parser.add_argument("-u", "--url", required=True, help="URL for the HTTP request")
    parser.add_argument("-p", "--payload", required=False, help="Path to the payload file")
    parser.add_argument("-H", "--headers", nargs='*', help="Optional headers (key:value pairs)")
    parser.add_argument("-o", "--output", required=False, help="Path to the Output file")
    parser.add_argument("-b", "--body", required=False, help="Body of the request")

    
    args = parser.parse_args()
    
    return args.method, args.url, args.payload, args.headers, args.output, args.body


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
            n=0
            responses = []
            if var=="body":
                for line in payload:
                    response=(requests.request(method, url, data=line.replace("!FUZZ",body), headers=headers))
                    responses.append(response)
                    n+=1
                    print(n,'->',response.status_code)
                    
            elif var=="url":
                for line in payload:
                    response=(requests.request(method, url.replace("!FUZZ",line), data=body, headers=headers))
                    responses.append(response)
                    n+=1
                    print(n,'->',response.status_code)
                    
            elif var.startswith("headers"):
                for line in payload:
                    response=(requests.request(method, url, data=body, headers=headers.replace("!FUZZ",line)))
                    responses.append(response)
                    n+=1
                    print(n,'->',response.status_code)
            else:
                pass
                    
    else:
        response = requests.request(method, url, data=body, headers=headers)
        return response


def main():
    method, url, payload_path, headers,output,body = get_args()
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
    print("Output Path:", output)

    response = send_request(method, url, payload_path, headers,body,var)
    print(response.status_code)

if __name__ == "__main__":
    main()