## Helper for sending Requests

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class sendRequest:
    def __init__(self):
        pass

    def send_request(self, request_data):

        if request_data.get("method").upper() == "GET":
            response = self.send_get_request(request_data)

        return response

    def replace_jwt_in_headers(self, request_data, old_jwt, new_jwt):
        headers = request_data.get("headers")
        if not headers:
            return request_data
        
        for key, value in headers.items():
            if value == old_jwt:
                headers[key] = new_jwt

        return request_data  
    
    def replace_jwt_in_cookies(self, request_data, old_jwt, new_jwt):
        cookies = request_data.get("cookies")
        if not cookies:
            return request_data
        
        for key, value in cookies.items():
            if value == f"Bearer {old_jwt}":
                cookies[key] = f"Bearer {new_jwt}"

            if value == f"{old_jwt}":
                cookies[key] = f"{new_jwt}"

            
        return request_data


    def send_get_request(self, request_data):
        headers = request_data.get("headers")
        cookies = request_data.get("cookies")
        url = request_data.get("url")

        response = requests.get(url, headers=headers, cookies=cookies, verify=False)

        return response
    

send_request = sendRequest()