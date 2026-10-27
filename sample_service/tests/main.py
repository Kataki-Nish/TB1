

from fastapi import FastAPI

import uvicorn

import httpx

from typing import List , Dict

from random import randint

import threading

import time




class SDK:

    def __init__(self,service_name):

        self.service_name = service_name

        self.latency_d: Dict[str,List[float]] = {}

    def service_setup(self) -> None:

        orginal = httpx.Client.send

        def tracker(req: "httpx.Request"):

            try:

                start = time.time()

                a = orginal(request=req)

                return a

            finally:

                latency = time.time() - start

                host = req.url.host

                port = req.url.port

                scheme = req.url.scheme  # http , https , ...

                if port not in [80,443]:

                    dependency_name = f"{host}:{port}"

                else:

                    dependency_name = host

                if dependency_name not in self.latency_d.keys():

                    self.latency_d[dependency_name] = [latency]

                else:

                    self.latency_d[dependency_name].append(latency)

        
        httpx.Client.send = tracker


    def agregater(self) -> List[float]:

        for k in self.latency_d.keys():

            if k == self.service_name:

                inbound_latencies = self.latency_d[k]

        return inbound_latencies


















class Service:

    port = 8000

    def __init__(self,service_name: str,paths:List[str]):

        self.app = FastAPI()

        self.name = service_name

        self.paths = []

        for p in paths:

            if not p.startswith("/"):

                p = "/" + p

                p = p.lower().strip()

            self.paths.append(p)

        self.host = "127.0.0.1"

        self.port = Service.port

        self.server = uvicorn.Server(config=uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port
        ))

        Service.port += 1

        @self.app.get("/")
        def server_is_running():

            return {"status":"running"}

        for p in self.paths:

            self.add_route(path=p,return_msg=randint(0,9))


    def add_route(self,path: str,return_msg: str | int):

        def handler():

            print(f"handler of service {self.name} {path}  called")

            return {"msg":return_msg}

        self.app.add_api_route(
            path=path,
            endpoint=handler,
            methods=["GET"]
        )

    def start_run(self):

        self.thread = threading.Thread(target=self.server.run)

        self.thread.start()

        print(f"starting server of service {self.name} ...")

        while True:

            try:

                httpx.get(f"http://{self.host}:{self.port}/")

                break

            except  httpx.ConnectError:

                pass

        print(f"server of service {self.name} started")


    def stop_run(self):

        print(f"stopping server of service {self.name} ...")

        self.server.should_exit = True

        self.thread.join(timeout=10)

        if self.thread.is_alive():

            raise TimeoutError(f"server of service {self.name} cant be stopped")

        print(f"server of service {self.name} stopped")

    def call(self,path: str):

        if not path.startswith("/"):

            path = "/" + path

        path = path.lower().strip()

        if path in self.paths:

            try:

                answer = httpx.get(f"http://{self.host}:{self.port}{path}")

                return answer

            except httpx.ConnectError:

                print(f"server of service {self.name} is disconect.")
        
        else:

            raise ValueError(f"there is no path named {path} in service {self.name} paths\n service {self.name} paths:{self.paths}")



s_A = Service(service_name="A",paths=["health","main","check"])


# should write after creating service

sdk = SDK(service_name="A")

sdk.service_setup()




s_A.call(path="main")


s_A.start_run()

print(s_A.call(path="health").json())

for p in s_A.paths:

    print(p)

s_A.stop_run()


print(sdk.latency_d)






        


