### Generic Testing

from jwtHelper.sendRequest import send_request

class genericAlgos:
    def __init__(self):
        pass


    def fail_to_read_secret(self, request_data, jwt):
        results = {}
        normal_response = send_request.send_request(request_data=request_data)
        nr_code = str(normal_response.status_code)



        jwt_without_secret = jwt.split(".")[0] + "." + jwt.split(".")[1] + "."

        request_data = send_request.replace_jwt_in_headers(request_data=request_data, old_jwt=jwt, new_jwt=jwt_without_secret)
        request_data = send_request.replace_jwt_in_cookies(request_data=request_data, old_jwt=jwt, new_jwt=jwt_without_secret)

        response = send_request.send_request(request_data=request_data)
        r_code = str(response.status_code)


        if nr_code == r_code:
            results = {
                "fail_to_read_jwt_secret": True
            }

        elif r_code != nr_code and nr_code.startswith("2"):
            results = {
                "fail_to_read_jwt_secret": "2xx Response - Not Identical"
            }

        else: 
            results = {
            "fail_to_read_jwt_secret": False
        }

        

        return results
    
    def algorithm_confusion(self, request_data):
        results = {}
        normal_response = send_request.send_request(request_data=request_data)
        nr_code = normal_response.status_code





        return results
    


generic_algos = genericAlgos()