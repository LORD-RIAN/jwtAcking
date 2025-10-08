## Brute forcing JWT secrets
import hmac
import hashlib
import base64
from jwtHelper.jwtSplitter import jwt_reader

class hsAlgos:
    def __init__(self):
        pass


    def hash_secret(self, alg, jwt, secret):
        alg = alg.upper()
        jwt_nosecret = jwt.split(".")[0] + "." + jwt.split(".")[1]

        jwt_nosecret = jwt_nosecret.encode()

        if alg == "HS256":
            secret_bytes = hmac.new(secret.encode(), jwt_nosecret, hashlib.sha256).digest()
        elif alg == "HS384":
            secret_bytes = hmac.new(secret.encode(), jwt_nosecret, hashlib.sha384).digest()
        elif alg == "HS512":
            secret_bytes = hmac.new(secret.encode(), jwt_nosecret, hashlib.sha512).digest()


        jwt_secret = base64.urlsafe_b64encode(secret_bytes).rstrip(b"=").decode()

        return jwt_secret
    
    def brute_force_secret(self, jwt, secret_list):
        
        jwt_secret = jwt.split(".")[2]
        

        alg = jwt_reader.get_jwt_alg(jwt=jwt)

        for secret in secret_list:
            
            jwt_test_secret = self.hash_secret(alg=alg, jwt=jwt, secret=secret)

            if jwt_test_secret == jwt_secret:
                return secret
            
        return None
    

hs_algos = hsAlgos()

if __name__ == "__main__":
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.ZDcyqtoxXmPegYh_8rA9r4F95LRNJGGhI5RpHmUsJjo"
    jwt_nosecret = hs_algos.hash_secret("Hs256", jwt)

    print(jwt_nosecret)