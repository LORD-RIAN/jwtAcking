## Delegate the JWT + Request to the script handling the JWT algo
from jwtAlgos.HS_algos import hs_algos
import os
from dotenv import load_dotenv

load_dotenv()
brute_force_wordlist = os.getenv("BRUTE-FORCE-LIST-PATH")

with open(brute_force_wordlist, "r", encoding="utf-8") as f:
    wordlist = [line.strip() for line in f if line.strip()]

class jwtDelegater:
    def __init__(self):
        pass


    def hs_algo(self, jwts, request_data):
        print(jwts)
        for jwt in jwts:
            print("s")
            
            jwt_secret = hs_algos.brute_force_secret(jwt, secret_list=wordlist)
        
        return jwt_secret
    



jwt_delegater = jwtDelegater()