

from typing import TYPE_CHECKING

from schemas.agent.buffer import i_buffer

import threading

import time

from proto.metrics_and_reprots import metrics_and_reprots



if TYPE_CHECKING:

    from proto.starters import starters

    from schemas.agent.system_data_getter import test_01

    from agent.agregater import agregater













def difference(a: float,b:float) -> float:

    if a >= b:

        c = a -b

    else:

        c = b - a

    return c




class Buffer:

    def __init__(self , service_name: str):

        self.service_name = service_name

        self.l_metric_500ms = []

        self.l_SDK_shemas = []

        self.running = False

        self.last_sdg_10s_timestamp = -1

        self.last_sdg_500ms_timestamp = -1
        
        self.last_sdk_timestamp = -1

        t = time.time()

        self.last_processed_sdk_time = t

        self.last_processed_sdg_10s_time = t

        self.last_processed_sdg_500ms_time = t

    def get_metric_10s(self , metric_10s: "test_01.Metric_10s") -> None:  # Finished

        self.metric_10s = metric_10s

        self.last_sdg_10s_timestamp = metric_10s.timestamp

    def get_metric_500ms(self , metric_500ms: "test_01.Metric_500ms") -> None:  # Finished

        self.l_metric_500ms.append(metric_500ms)

        if len(self.l_metric_500ms) == 1:

            self.last_sdg_500ms_timestamp = metric_500ms.timestamp

    def get_SDK_shema(self , SDK_shema: "metrics_and_reprots.SDK_reprot_shema") -> None:  # Finished

        # # debug

        # print(f"buffer get sdk shema:\n{SDK_shema}")

        # # -----

        self.l_SDK_shemas.append(SDK_shema)

        if type(SDK_shema.bound_type) == metrics_and_reprots.Inbound:

            self.last_sdk_timestamp = SDK_shema.timestamp


    def process(self , agregater: "agregater.Agregater") -> None:  # Finished

        system_datas = i_buffer.System_datas(metric_10s=self.metric_10s , metrics_500ms=self.l_metric_500ms)

        buffer_output = i_buffer.Buffer_output(time.time(),system_datas=system_datas , sdk_shemas=self.l_SDK_shemas)

        agregater.get_buffer_output(buffer_output=buffer_output)

        self.l_metric_500ms = []

        self.l_SDK_shemas = []

        # debug

        print("\nbuffer_output : ")

        print(f"{buffer_output.__dict__}\n")

        # -----


    def main(self) -> None:  # Finished

        while self.running:

            new_sdg = (self.last_sdg_10s_timestamp > self.last_processed_sdg_10s_time) and (self.last_sdg_500ms_timestamp > self.last_processed_sdg_500ms_time)

            new_sdk =  self.last_sdk_timestamp > self.last_processed_sdk_time

            if new_sdg and new_sdk:

                self.process(agregater=self.agent_components.a)

                self.last_processed_sdg_10s_time = self.last_sdg_10s_timestamp

                self.last_processed_sdg_500ms_time = self.last_sdg_500ms_timestamp

                self.last_processed_sdk_time = self.last_sdk_timestamp

            sdk_stale = (time.time() - self.last_sdk_timestamp) > 12

            if new_sdg and sdk_stale:

                self.process(agregater=self.agent_components.a)

                self.last_processed_sdg_10s_time = self.last_sdg_10s_timestamp
                
                self.last_processed_sdg_500ms_time = self.last_sdg_500ms_timestamp


            time.sleep(0.2)


    def start_run(self,agent_components: "starters.Agent_components"):

        self.agent_components = agent_components

        self.running = True

        self.thread = threading.Thread(target=self.main)

        self.thread.start()

    def stop_run(self):

        self.running = False

        self.thread.join(timeout=30)

        if self.thread.is_alive():

            raise TimeoutError("buffer in agent cant be stopped")







