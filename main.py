## jwt hacking main, tests all JWT hacking activities

from jwtAlgos.HS_algos import hs_algos
from jwtHelper.jwtSplitter import jwt_reader
from jwtHelper.sendRequest import send_request
from jwtHelper.interpretCurl import curl_interpreter
from jwtAlgos.delegateJWTs import jwt_delegater
import requests
import sys



data = sys.stdin.read()
print("1")

request_data = curl_interpreter.convert_data(data=data)

print("x")
print(request_data.get("jwts"))
print(request_data.get("headers"))
print(request_data.get("cookies"))
print("---")
print(request_data.get("url"))
print(request_data.get("method"))

print("start")
jwt_secret = jwt_delegater.hs_algo(request_data.get("jwts"), request_data=request_data)


print(jwt_secret)

"""

Add module to remove all unused auth. So all JWTs that could be removed while still returning 200 gets removed <-

"""

print("Done!")
