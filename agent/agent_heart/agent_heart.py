

from typing import TYPE_CHECKING

import threading

from proto.heartbeat import heartbeat

import time


if TYPE_CHECKING:

    from agent.agent_body import agent_body



class Agent_heart:

    def __init__(self , agent: "agent_body.Agent" = None):

        self.running = False

        self.agent = agent

    def main(self):

        v = 1

        while self.running:

            hb = heartbeat.Heartbeat(
                timestamp=time.time(),
                component_type="agent",
                component_id=1,
                heartbeat_version=v
            )

            # # debug

            # print(f"agent_heart output:\n{hb.__dict__}")

            # # -----

            self.agent.cp_c.get_item(hb)

            v += 1

            time.sleep(3)

    def start_run(self):

        self.running = True

        self.thread = threading.Thread(target=self.main)

        self.thread.start()

    def stop_run(self):

        self.running = False


