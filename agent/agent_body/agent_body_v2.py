


import threading

import time

from typing import TYPE_CHECKING

from agent.agent_heart import agent_heart

from agent.system_data_getter import sdg

from agent.agregater import agregater

from agent.buffer import buffer

from proto.starters import starters

from proto.metrics_and_reprots import metrics_and_reprots

from queue import Queue , Empty





class Agent:  # Finished

    def __init__(self):  # Finished

        self.running = False

        self.start_msg = None

        self.pre_start()

    def pre_start(self):  # Finished

        # pre start

        self.sdk_c = SDK_client(self)

        self.cp_c = CP_client(self)

        self.h = agent_heart.Agent_heart(self)

        self.sdk_c.start_run()

        self.cp_c.start_run()

        self.h.start_run()


    def get_start_msg(self,start_msg: "starters.Start_msg"):  # Finished

        if start_msg.starting == True:

            self.start_msg = start_msg

            if not self.running:

                self.start_run()

        else:

            self.stop_run()

            self.start_msg = None

    def main(self):  # Finished


        # start_msg check

        while True:

            if self.start_msg != None:

                break

            time.sleep(0.2)

        # start sdk , buffer , agregater

        # debug

        print("agent component creating started")

        # -----

        self.start_order = starters.Start_order(timestamp=time.time(),sender="starter",getters=["sdg","buffer","agregater"],service_name=self.start_msg.service_name)

        s = sdg.System_data_getter_V11(self.start_order.service_name)

        b = buffer.Buffer(self.start_order.service_name)

        a = agregater.Agregater(self.start_order.service_name)

        self.agent_components = starters.Agent_components(b=b , s=s , a=a , agent=self)

        for e in [s,b,a]:  # for each element in agent_components:

            e.start_run(self.agent_components)  #run only 1 time

        # debug

        print("agent component runned")

        # -----

        while self.running:

            time.sleep(0.2)

        else:

            for e in [s,b,a]:  # for each element in agent_components:

                e.stop_run()  #run only 1 time


    def start_run(self):  # Finished

        self.running = True

        self.thread = threading.Thread(target=self.main)

        self.thread.start()


    def stop_run(self):  # Finished

        print("stopping agent ...")

        self.running = False

        self.start_msg = None

        self.thread.join(timeout=30)

        if self.thread.is_alive():

            raise TimeoutError("Agent cant be stopped")

        else:

            print("agent stopped")

    def kill_agent(self):  # Finished

        self.sdk_c.stop_run()

        self.stop_run()

        self.h.stop_run()

        self.cp_c.stop_run()

        print("agent killed.")









class SDK_client:

    def __init__(self , agent: Agent = None):  # Finished

        self.running = False

        self.agent = agent

        self.queue = Queue()

    def send_item(self,sdk_shema) -> None:  # Finished

        # # debug

        # print(f"\nsdk_client 4:\n{sdk_shema}\n")

        # # -----

        self.agent.agent_components.b.get_SDK_shema(sdk_shema)


    def get_from_sdk(self, item: metrics_and_reprots.SDK_reprot_shema | starters.Start_msg) -> None:  # Finished


        if type(item) == starters.Start_msg:

            self.agent.get_start_msg(start_msg=item)

        else:

            self.queue.put(item)



    def main(self):  # event_driven

        while self.running or (not self.queue.empty()):

            # getting from SDK through UDS

            # item = item from SDK through UDS

            # self.get_from_sdk(item)

            try:

                item = self.queue.get(timeout=0.5)

                # # debug

                # print(f"sdk_client 3:\n{item.__dict__}")

                # # ------

                self.send_item(sdk_shema=item)

            except Empty:

                pass
    

    def start_run(self):  # Finished

        self.running = True

        self.thread = threading.Thread(target=self.main)

        self.thread.start()


    def stop_run(self):  # Finished

        self.running = False

        self.thread.join(timeout=30)

        if self.thread.is_alive():

            raise TimeoutError("SDK_client in agent cant be stopped")

    




class CP_client:

    def __init__(self , agent: Agent = None):  # Finished

        self.running = False

        self.agent = agent

        self.queue = Queue()


    def get_item(self,item):  # Finished

        self.queue.put(item)


    def send_item(self , item) -> None:

        # debug

        print(f"\nCP_client item:\n{item.__dict__}\n")

        # -----

        # sending

        pass



    def main(self):  # Finished

        while self.running or (not self.queue.empty()):

            try:

                item = self.queue.get(timeout=0.5)

                self.send_item(item=item)

            except Empty:

                pass
    

    def start_run(self):  # Finished

        self.running = True

        self.thread = threading.Thread(target=self.main)

        self.thread.start()


    def stop_run(self):  # Finished

        self.running = False

        self.thread.join(timeout=30)

        if self.thread.is_alive():

            raise TimeoutError("CP_client in agent cant be stopped")

        

        




