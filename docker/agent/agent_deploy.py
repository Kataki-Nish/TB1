
from agent.agent_body import agent_body_v2

import signal






agent = agent_body_v2.Agent()



def shutdown(signum,frame):

    print("docker is stopping container ...")

    agent.kill_agent()

    print("docker desktop stopped")


signal.signal(signal.SIGTERM , handler=shutdown)

agent.start_run()
