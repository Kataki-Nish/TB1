


from sample_service.service_A import service_A

import signal

import os

# debug

from proto.starters import starters

from time import sleep

# -----




def shutdown(signum,frame):

    print("docker is stopping container ...")

    service_A.service_A.stop_run()

    # # debug

    # print(f"inbound_req_count:\n{service_A.sdk.service_name}: {service_A.sdk.inbound_req_c}")

    # print(f"inbound_error_count:\n{service_A.sdk.service_name}: {service_A.sdk.inbound_error_c}")

    # print(f"inbound_latency:\n{service_A.sdk.service_name}: {service_A.sdk.inbound_latency_h.get_latency_histogram()}")


    # print(f"outbound_req_count:\n{service_A.sdk.outbound_req_d}")

    # print(f"outbound_error_count:\n{service_A.sdk.outbound_error_d}")

    # print(f"outbound_latency:")

    # for k , v in service_A.sdk.outbound_latency_d2.items():

    #     print(f"{k}: {v.get_latency_histogram()}")

    # # -----

    print("docker desktop stopped")





signal.signal(signal.SIGTERM , handler=shutdown)

service_A.service_A.start_run()




# debug

start_ping = starters.Start_ping(timestamp=-1,sender="CP",getters="SDK",starting=True)

service_A.sdk.get_start_ping(start_ping=start_ping)

sleep(5)

start_ping = starters.Start_ping(timestamp=-1,sender="CP",getters="SDK",starting=True)

service_A.sdk.get_start_ping(start_ping=start_ping)

sleep(20)

start_ping = starters.Start_ping(timestamp=-1,sender="CP",getters="SDK",starting=False)

service_A.sdk.get_start_ping(start_ping=start_ping)

sleep(10)

start_ping = starters.Start_ping(timestamp=-1,sender="CP",getters="SDK",starting=True)

service_A.sdk.get_start_ping(start_ping=start_ping)


# -----


