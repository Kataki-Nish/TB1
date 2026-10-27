

from fastapi import FastAPI

import uvicorn

import threading

import httpx

from time import sleep

import socket


class Service:

    def __init__(self,service_name: str,port: int,host: str | None = None):

        # dubug

        self.running = False

        # -----

        self.name = service_name

        self.app = FastAPI()

        self.client = httpx.Client()

        if host is None:

            self.host = "127.0.0.1"

        else:

            self.host = host

        self.port = port

        self.server = uvicorn.Server(config=uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port
        ))

        @self.app.get("/")
        def server_online_check():

            return {"online":True}

    def add_route(self , path: str , handler: "function" , methods: list[str]):

        if not path.startswith("/"):

            path = "/" + path

        path = path.lower().strip()

        self.app.add_api_route(
            path=path,
            endpoint=handler,
            methods=methods
        )


    # debug

    def health_check(self):

        print(f"running of service {self.name} started .")

        while self.running:

            print(f"service {self.name} is running ...")

            sleep(1)
    
    # -----


    def start_run(self):

        self.running = True

        self.thread = threading.Thread(target=self.server.run)

        print(f"starting server of service {self.name} ...")

        self.thread.start()

        while True:

            try:

                socket.create_connection(address=(self.host,self.port),timeout=1)

                break

            except OSError :

                pass

        print(f"server of service {self.name} started .")

        # debug

        self.thread2 = threading.Thread(target=self.health_check)

        print(f"starting of running of service {self.name} ...")

        self.thread2.start()

        # -----


    def stop_run(self):

        # debug

        self.running = False

        print(f"stopping running of service {self.name} ...")

        self.thread2.join(timeout=10)

        if self.thread2.is_alive():

            raise TimeoutError(f"running of service {self.name} cant be stopped")

        print(f"running of service {self.name} stopped .")

        # -----

        self.server.should_exit = True

        print(f"stopping server of service {self.name} ...")

        self.thread.join(timeout=10)

        if self.thread.is_alive():

            raise TimeoutError(f"server of service {self.name} cant be stopped")

        print(f"server of service {self.name} stopped .")
                





def return_response(res: "httpx.Response") -> dict:

    d = {
        "status_code":res.status_code,
        "data":res.json(),
        "headers":res.headers
    }

    return d

