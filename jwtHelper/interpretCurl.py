### Helper script to interperate and structure CURL requests

import argparse
import re


class curlInterpreter:
    def __init__(self):
        pass


    def headers_from_curl(self, curl_request: str):

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
        pattern = re.compile(r'[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+')

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
    


curl_interpreter = curlInterpreter()

if __name__ == "__main__":

    p = argparse.ArgumentParser()

    p.add_argument("-curl", "--curl", help="full curl command", required=True)

    args = p.parse_args()

    curl_request = """curl 'https://example.com/' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'cache-control: max-age=0' \
  -H 'if-modified-since: Mon, 13 Jan 2025 20:11:20 GMT' \
  -H 'if-none-match: "84238dfc8092e5d9c0dac8ef93371a07:1736799080.121134"' \
  -H 'priority: u=0, i' \
  -H 'sec-ch-ua: "Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: none' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'"""
    
    curl_request = args.curl
    
    print(curl_request)