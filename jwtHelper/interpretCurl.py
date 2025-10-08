### Helper script to interperate and structure CURL requests

import argparse
import re


class curlInterpreter:
    def __init__(self):
        pass

    def convert_data(self, data):
        lines = data.split("\n")
        request_data = {}

        headers = self.headers_from_curl(lines)

        headers_dict = self.headers_to_dict(headers=headers)
        cookies_dict = self.extract_cookies(headers=headers)
        jwts = self.find_jwt(headers=headers)

        method = self.extract_method(curl_request=data)
        url = self.extract_url(curl_request=data)

        request_data = {
            "url": url,
            "method": method,
            "headers": headers_dict,
            "cookies": cookies_dict,
            "jwts": jwts
        }

        return request_data


    def headers_from_curl(self, curl_request):

        headers = []
        for line in curl_request:
            line = line.strip()

            if line.startswith("-H"):
                header = line[2:].strip()

                if header.endswith("\\"):
                    header = header[:-1].strip()

                if header.startswith(("'", '"')) and header.endswith(("'", '"')):
                    header = header[1:-1]


                headers.append(header)

        return headers
    
    def find_jwt(self, headers):
        jwts = []
        pattern = re.compile(r'(?<![\w-])(?:[A-Za-z0-9_-]{10,}\.){2}[A-Za-z0-9_-]{10,}(?![\w-])')

        for header in headers:
            match = pattern.search(header)
            if match:
                jwts.append(match.group())

        return jwts
    
    def headers_to_dict(self, headers):
        headers_dict = {}
        for h in headers:
            if ":" in h:
                key, value = h.split(":", 1)
                headers_dict[key.strip()] = value.strip()
        return headers_dict

    def extract_cookies(self, headers):
        cookies = {}
        for h in headers:
            if h.lower().startswith("cookie:"):
                cookie_str = h.split(":", 1)[1].strip()
                for pair in cookie_str.split(";"):
                    if "=" in pair:
                        key, value = pair.strip().split("=", 1)
                        cookies[key] = value
        return cookies
    
    def extract_url(self, curl_request: str):
        match = re.search(r"curl\s+'([^']+)'", curl_request)
        if not match:
            match = re.search(r'curl\s+"([^"]+)"', curl_request)
        return match.group(1) if match else None
    
    def extract_method(self, curl_request: str):

        for line in curl_request.splitlines():
            if "-X" in line or "--request" in line:
                parts = line.strip().split()
                for p in parts:
                    if p.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]:
                        return p.upper()

        return "GET"

    


curl_interpreter = curlInterpreter()

