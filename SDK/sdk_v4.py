



import os









from typing import TYPE_CHECKING , Dict , List

from proto.metrics_and_reprots import metrics_and_reprots

import time

import threading

from proto.starters import starters

import httpx

from starlette.middleware.base import BaseHTTPMiddleware

from proto import host_and_port

import queue

from copy import deepcopy


if TYPE_CHECKING:

    from fastapi import FastAPI






class Latency_histogram:

    buckets_ms = (0,1,5,10,25,50,100,250,500,1000,2500,5000)

    def __init__(self):

        self.empty_h = {k:0 for k in Latency_histogram.buckets_ms}

        self.empty_h[-1] = 0

        self.latnecy_histogram = deepcopy(self.empty_h)

    def add_latency(self , latency_s: float) -> None:

        latency = latency_s*1000

        i = 0

        for l in Latency_histogram.buckets_ms:

            if latency > l:

                i += 1

        if i > len(Latency_histogram.buckets_ms):

            self.latnecy_histogram[-1] += 1

        else:

            self.latnecy_histogram[Latency_histogram.buckets_ms[i]] += 1

    def get_latency_histogram(self) -> dict:

        a = self.latnecy_histogram

        self.latnecy_histogram = deepcopy(self.empty_h)

        return a





class RED_Middleware(BaseHTTPMiddleware):

    def __init__(self , service_app):  # finished

        super().__init__(app=service_app)

        self.latency_histogrm = Latency_histogram()

        self.error_count = 0

        self.req_count = 0

    async def dispatch(self, request, call_next):  # finished

        try:

            start = time.perf_counter()

            response = await call_next(request)

            return response

        except Exception:

            self.error_count += 1

            raise

        finally:

            latency = time.perf_counter() - start

            self.latency_histogrm.add_latency(latency_s=latency)

            self.req_count += 1

    def reset_parameter(self):  # finished

        self.error_count = 0

        self.req_count = 0





class Sdk:

    AGENT_HOST = host_and_port.agent_SDK_client.host

    AGENT_PORT = host_and_port.agent_SDK_client.port

    def __init__(self , service_app: "FastAPI"):  # finished

        self.start_ping = None

        self.service_name = None

        self.running = False

        self.app = service_app

        self.last_send_time = None

        self.queue = queue.Queue()


    def CP_client(self):  # it is thread

        # start_ping = get_from_CP 

        # self.get_start_ping(start_ping=start_ping)

        pass



    def get_start_ping(self , start_ping: starters.Start_ping) -> None:  # Finished

        if start_ping.starting == True:

            self.start_ping = start_ping

            if not self.running:

                self.start_run()

        else:

            self.stop_run()

            self.start_ping = None


    def sdk_starter(self , starting: bool) -> None:  # Finished

        if starting == True:

            # if operator don't set container_name in docker_compose file , then we get container_id directly

            self.service_name = os.getenv("HOSTNAME",default="unknown")

            start_msg = starters.Start_msg(
                timestamp=time.time(),
                sender="SDK",
                getters="agent",
                service_name=self.service_name,
                starting=True
            )

        else:

            # if operator don't set container_name in docker_compose file , then we get container_id directly

            self.service_name = os.getenv("HOSTNAME",default="unknown")

            start_msg = starters.Start_msg(
                timestamp=time.time(),
                sender="SDK",
                getters="agent",
                service_name=self.service_name,
                starting=False
            )

        self.queue.put(start_msg)




    def setup(self) -> None:  # finished

        self.red_middleware = RED_Middleware(self.app)  # for inbound RED metrics

        self.app.add_middleware(BaseHTTPMiddleware,dispatch=self.red_middleware.dispatch)


        self.outbound_latency_d2: Dict[str,Latency_histogram] = {}

        self.outbound_error_d: Dict[str,int] = {}

        self.outbound_req_d: Dict[str,int] = {}


        orginal = httpx.Client.send

        def tracker(instance_client: httpx.Client , req: httpx.Request,*args,**kwargs):  # finished

            try:

                start = time.perf_counter()

                result = orginal(self=instance_client,request=req,*args,**kwargs)

                return result

            except Exception:

                host = req.url.host

                port = req.url.port

                dependency_name = f"{host}:{port}"

                if not dependency_name in self.outbound_error_d:

                    self.outbound_error_d[dependency_name] = 0

                self.outbound_error_d[dependency_name] += 1

                raise

            finally:

                latency = time.perf_counter() - start

                host = req.url.host

                port = req.url.port

                dependency_name = f"{host}:{port}"

                scheme = req.url.scheme  # http , https , ...

                if not dependency_name in self.outbound_req_d:

                    self.outbound_req_d[dependency_name] = 0

                if not dependency_name in self.outbound_error_d:

                    self.outbound_error_d[dependency_name] = 0

                self.outbound_req_d[dependency_name] += 1

                if not dependency_name in self.outbound_latency_d2:

                    self.outbound_latency_d2[dependency_name] = Latency_histogram()

                self.outbound_latency_d2[dependency_name].add_latency(latency_s=latency)

        httpx.Client.send = tracker

        # start_run() should be here , be cause when CP send start_ping to SDK ,
        # if SDk don't start_run() before CP sending , we don't have any CP_client to get start_ping . 

        self.start_run()



    @property
    def inbound_latency_h(self) -> Latency_histogram:  # finished

        if self.red_middleware is None:

            raise ValueError("service_name or red_middleware is not defined yet , and for that , this property cant calculate inbound_latency_d")

        else:

            return self.red_middleware.latency_histogrm

    @property
    def inbound_error_c(self) -> int:  # finished

        if self.red_middleware is None:

            raise ValueError("service_name or red_middleware is not defined yet , and for that , this property cant calculate inbound_latency_d")

        else:

            return self.red_middleware.error_count

    @property
    def inbound_req_c(self) -> int:  # finished

        if self.red_middleware is None:

            raise ValueError("service_name or red_middleware is not defined yet , and for that , this property cant calculate inbound_latency_d")

        else:

            return self.red_middleware.req_count



    def reset_outbound_parameter(self,dependency_name):  # finished

        self.outbound_error_d[dependency_name] = 0

        self.outbound_req_d[dependency_name] = 0




    def agent_client(self):

        while (not self.queue.empty()) or self.running:

            try:

                a = self.queue.get(timeout=1)

                # debug

                print(a)

                # -----

                # send to agent

                pass
            
            except (TimeoutError, queue.Empty):

                pass



    def agregater(self):  # finished

        a = self.build_report(bound_t=True)

        self.queue.put(a)

        for dn in self.outbound_req_d:

            a = self.build_report(bound_t=False,dependency_name=dn)

            self.queue.put(a)



    def build_report(self , bound_t: bool , dependency_name: str | None =None) -> metrics_and_reprots.SDK_reprot_shema:  # finished

        if self.last_send_time is None:

            window = None

        else:

            window = time.time() - self.last_send_time

        self.last_send_time = time.time()


        if bound_t == True:

            red = metrics_and_reprots.RED(
                window=window,
                request_count=self.inbound_req_c,
                error_count=self.inbound_error_c,
                latency_histogram=self.inbound_latency_h.get_latency_histogram()
            )

            self.red_middleware.reset_parameter()

            bound_type = metrics_and_reprots.Inbound(red=red)


        else:  # bound_type == False

            if dependency_name == None:

                raise KeyError("if bound_type == False , dependency_name should be feilded")

            red = metrics_and_reprots.RED(
                window=window,
                request_count=self.outbound_req_d[dependency_name],
                error_count=self.outbound_error_d[dependency_name],
                latency_histogram=self.outbound_latency_d2[dependency_name].get_latency_histogram()
            )

            self.reset_outbound_parameter(dependency_name)

            bound_type = metrics_and_reprots.Outbound(dependency_name=dependency_name,red=red)


        sdk_reprot_shema = metrics_and_reprots.SDK_reprot_shema(
            timestamp=time.time(),
            service_name=self.service_name,
            instance_id=1,
            bound_type=bound_type
        )

        return sdk_reprot_shema



    def main(self):  # Finished


        while True:

            if self.start_ping != None:

                break

            time.sleep(0.2)

        self.sdk_starter(starting=True)

        while self.running:

            time.sleep(10)

            self.agregater()



    def start_run(self):  # Finished

        self.thread_CP_client = threading.Thread(target=self.CP_client)

        self.thread = threading.Thread(target=self.main)

        self.thread_a_client = threading.Thread(target=self.agent_client)

        self.running = True

        self.thread_a_client.start()

        self.thread.start()

        self.thread_CP_client.start()

    def stop_run(self):  # Finished

        print("stopping SDK ...")

        self.sdk_starter(starting=False)

        self.running = False


        self.thread_CP_client.join(timeout=15)

        if self.thread_CP_client.is_alive():

            raise TimeoutError("CP_client cant be stopped")

        # debug

        print("CP_client stopped")

        # -----


        self.thread.join(timeout=30)

        if self.thread.is_alive():

            raise TimeoutError("SDK cant be stopped")

        self.thread_a_client.join(timeout=15)

        print("SDK stopped")


        if self.thread_a_client.is_alive():

            raise TimeoutError("agent_client cant be stopped")

        # debug

        print("agent_client stopped")

        # -----














