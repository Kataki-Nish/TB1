


from sample_service.service_C import service_C

import signal




def shutdown(signum,frame):

    print("docker is stopping container ...")

    service_C.service_C.stop_run()

    print("docker desktop stopped")





signal.signal(signal.SIGTERM , handler=shutdown)

service_C.service_C.start_run()



