


from sample_service.service_B import service_B

import signal




def shutdown(signum,frame):

    print("docker is stopping container ...")

    service_B.service_B.stop_run()

    print("docker desktop stopped")





signal.signal(signal.SIGTERM , handler=shutdown)

service_B.service_B.start_run()



