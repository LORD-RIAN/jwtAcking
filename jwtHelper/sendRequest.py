## Helper for sending Requests

import requests

class sendRequest:
    def __init__(self):
        pass

    def replace_jwt_in_headers(self, headers, old_jwt, new_jwt):
        for key, value in headers.items():
            if value == old_jwt:
                headers[key] = new_jwt
                return key 

        return None  
    
    def replace_jwt_in_cookies(self, cookies, old_jwt, new_jwt):
        for key, value in cookies.items():
            if value == f"Bearer {old_jwt}":
                cookies[key] = f"Bearer {new_jwt}"
                return key
            if value == f"{old_jwt}":
                cookies[key] = f"{new_jwt}"
                return key
            
        return None


    def send_get_request(self, host, jwt, headers={}, cookies={}):
        new_jwt = "testSUCCEED"

        print(headers)
        header_name = self.replace_jwt_in_headers(headers, jwt, new_jwt)
        print(header_name)
        print(headers)
        print(cookies)

        ### Change JWT to a JWT with a cracked secret, or one with algorithm confusion, or another KID or similar. 
        ## use all JWT hacking methods to do it.
        #### Do universal headers + cookies , and just change get and POST with body and method

        # Make outlines first, then short down

        resp = requests.get(f"https://{host}/", headers=headers, cookies=cookies)

        return resp
    

send_request = sendRequest()