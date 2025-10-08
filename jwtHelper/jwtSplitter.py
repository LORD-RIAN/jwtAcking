## Split JWTs and read alg, kid etc
import base64
import json

class jwtReader:
    def __init__(self):
        pass

    def split_jwt(self, jwt):
        lines  = len(jwt.split("."))
        if lines != 3:
            print("NOT A VALID JWT")
            quit()
        header = jwt.split(".")[0]

        body = jwt.split(".")[1]

        return header, body
    
    def _b64url_decode(self, segment):
        segment += "=" * (-len(segment) % 4)

        return base64.urlsafe_b64decode(segment)

    def get_jwt_alg(self, jwt):

        header, _ = self.split_jwt(jwt)

        header = json.loads(self._b64url_decode(header))

        alg = header.get("alg").upper()


        return alg

jwt_reader = jwtReader()

if __name__ == "__main__":
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.ZDcyqtoxXmPegYh_8rA9r4F95LRNJGGhI5RpHmUsJjo"

    header = jwt_reader.split_jwt(jwt)

    alg = jwt_reader.get_jwt_alg(header)

    print(alg)