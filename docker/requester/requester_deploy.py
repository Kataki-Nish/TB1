

import signal

import httpx

from proto.host_and_port import service_A

from typing import TYPE_CHECKING

from time import sleep

import threading

if TYPE_CHECKING:

    from proto.host_and_port import Protocol_data


class Requester:

    def __init__(self,instanece_id: int):

        self.running = False

        self.instance_id = instanece_id

        self.client = httpx.Client()

        self.target_service_protocol = None

    def http_call(self , component: str , host: str , port: int):

        try:

            url = f"http://{host}:{port}"

            a = self.client.get(url=f"{url}/check" , timeout=10)

            b = self.client.get(url=f"{url}/call_B",timeout=10)

            c1 = self.client.get(url=f"{url}/call_C1",timeout=10)

            c2 = self.client.get(url=f"{url}/call_C2",timeout=10)

            return [a,b,c1,c2]

        except httpx.ConnectError:

            print(f"http://{host}:{port}/check is doisconect yet .")

            pass

        except httpx.Timeout:

            print(f"Timeout Error: calling {url} is don't get response for {component} component.")

            raise

    def main(self):

        if self.target_service_protocol is None:

            raise TypeError("self.target_service_protocol is not parameterization")

        component = self.target_service_protocol.component

        host = self.target_service_protocol.host

        port = self.target_service_protocol.port

        print("requester started .")

        while self.running:

            self.http_call(component=component,host=host,port=port)

            sleep(0.2)


    def start_run(self , service_protocol: "Protocol_data"):

        self.target_service_protocol = service_protocol

        self.running = True

        self.thread = threading.Thread(target=self.main)

        print("starting of requester ...")

        self.thread.start()

    def stop_run(self):

        print("stopping of requester ...")

        self.running = False

        self.thread.join(timeout=10)

        if self.thread.is_alive():

            raise ValueError("requester cant be stopped")

        print("requester stopped .")




req = Requester(instanece_id=0)





def shutdwon(signum , frame):

    print("docker is stopping container ...")

    req.stop_run()

    print("docker desktop stopped")


signal.signal(signal.SIGTERM , handler=shutdwon)


req.start_run(service_A)

