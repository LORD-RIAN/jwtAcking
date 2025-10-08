## jwt hacking main, tests all JWT hacking activities

from jwtHelper.interpretCurl import curl_interpreter
from jwtAlgos.delegateJWTs import jwt_delegater
import sys



data = sys.stdin.read()
print("1")

request_data = curl_interpreter.convert_data(data=data)

print("Initial Data From Curl: \n")
print(request_data.get("jwts"))
print(request_data.get("headers"))
print(request_data.get("cookies"))
print(request_data.get("url"))
print(request_data.get("method"))

print("\nStart!\n\n\n\n")


results = jwt_delegater.run_attacks(request_data=request_data)


"""

Add module to remove all unused auth. So all JWTs that could be removed while still returning 200 gets removed <-

"""

"""
Note to self, if fail to verify secret -  Algorithm confusion is useless ( still run it ??? ) 

"""

print(f"\n\nResults: {results}")
print("Done!")
