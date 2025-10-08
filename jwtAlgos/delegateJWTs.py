## Delegate the JWT + Request to the script handling the JWT algo
from jwtAlgos.HS_algos import hs_algos
from jwtAlgos.ALL_algos import generic_algos
from jwtHelper.jwtSplitter import jwt_reader
import os
from dotenv import load_dotenv

load_dotenv()
brute_force_wordlist = os.getenv("BRUTE-FORCE-LIST-PATH")

with open(brute_force_wordlist, "r", encoding="utf-8") as f:
    wordlist = [line.strip() for line in f if line.strip()]

class jwtDelegater:
    def __init__(self):
        pass

    def run_attacks(self, request_data):
        results = {}
        print("start: run_attacks")

        if request_data.get("jwts"):
            for i, jwt in enumerate(request_data.get("jwts"), start=1):
                
                result = self.run_attack(jwt=jwt, request_data=request_data)
                

                results[str(i)] = result

                            
            
        return results
    
    def run_attack(self, jwt, request_data):

        result = {}

        alg = jwt_reader.get_jwt_alg(jwt=jwt)

        jwt_secret = None
        if alg.upper().startswith("HS"):
            jwt_secret = self.hs_algo(jwt=jwt, request_data=request_data)

        failed_to_read_secret = generic_algos.fail_to_read_secret(request_data=request_data, jwt=jwt)

        result = {
            "url": request_data.get("url"),
            "method": request_data.get("method"),
            "jwt_secret": jwt_secret,
            "fail_to_read_jwt_secret": failed_to_read_secret.get("fail_to_read_jwt_secret"),
            "alg": alg
        }


        return result


    def hs_algo(self, jwt, request_data):
            
        jwt_secret = hs_algos.brute_force_secret(jwt, secret_list=wordlist)
        
        return jwt_secret
    



jwt_delegater = jwtDelegater()