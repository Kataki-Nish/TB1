

from fastapi import FastAPI

import httpx

from time import time , sleep

from dataclasses import dataclass

from typing import Literal , Dict , List

from random import choice , randint

import threading

import uvicorn



@dataclass
class Health_endpoint_output:
    timestamp: float
    status: Literal["healthy","degraded","bad"]
    httpx.get()



app = FastAPI()


server = uvicorn.Server(config=uvicorn.Config(
    app=app,
    host="127.0.0.1",
    port=8000
    ))




# @app.get("/users/{user_id}")
# def hello(user_id: str):
#     print("hello() called")
#     return {f"hello user {user_id}"}



h_l = ["healthy","degraded","bad"]



@app.get("/health")
def health_endpoint():
    print("health endpoint called")
    a = Health_endpoint_output(
        timestamp=time(),
        status=choice(h_l)
    )
    return a


def health_loop():

    t = time()

    while time() < t + 50:

        response = httpx.get("http://127.0.0.1:8000/health")

        print(f"status code: {response.status_code}")

        print(f"answer: {response.json()}")

        sleep(5)

    print("health loop ended")



server_thread = threading.Thread(target=server.run)


server_thread.start()

health_loop()


server.should_exit = True

server_thread.join()

print("server stopped")






class Sample_service:

    port = 8000

    def __init__(self,routes: Dict[int,str]):

        self.app = FastAPI()

        self.routes = routes

        self.server = uvicorn.Server(config=uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=Sample_service.port
        ))

        Sample_service.port += 1

    def creat_route(self , path: str , route_response: str , methods: List[str]):  # finished

        def route_funtion():

            print(f"{path.lower()} route called")

            return route_response

        # path = path

        # methods = methods

        # handler = route_funtion

        self.app.add_api_route(
            path=path,
            endpoint=route_funtion,
            methods=methods
        )

    def creat_all_routes(self):  # NOT finished

        for k , v in self.routes.items():

            if k == 0:

                methods = ["GET"]

            elif k == 1:

                methods = ["POST"]

            elif k == 2:

                methods = ["GET" , "POST"]

            else:

                raise KeyError("routes.keys() should be 0 , 1 , 2")


            self.creat_route(path=v,route_response=randint(),methods=methods)





class Endpoint:

    def __init__(self,operation: Literal["get","post"],name: str):

        self.operation = operation

        self.name = name
        



    








