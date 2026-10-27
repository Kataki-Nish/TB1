
# configuration | container_creating | running


from pathlib import Path

import sys


path_root = Path(__file__).resolve().parents[1]

if str(path_root) not in sys.path:

    sys.path.insert(0 , str(path_root))


from proto.starters import starters

import time

from agent.agent_body import agent_body_v2










# -- agent_deploy_test ----


from SDK import sdk


# instance creating

# Hint: Agent should be created before SDK , because SDK need SDK_client address for communication with Agent .

agent = agent_body_v2.Agent()

s = sdk.Sdk(sdk_client=agent.sdk_c,service_name="tb1-test1")


# running

s.start_run()

agent.start_run()


# debug

time.sleep(5)

# -----


# start of telemetry

s.get_start_ping(start_ping=True)



# time passed from start to before of shut-down

time.sleep(50)



# shutting-down

s.stop_run()

agent.stop_run()



# -------------------------






