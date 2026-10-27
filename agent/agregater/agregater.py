


from typing import TYPE_CHECKING

import threading

from proto.metrics_and_reprots import metrics_and_reprots

import time


if TYPE_CHECKING:

    from proto.starters import starters

    from schemas.agent.buffer import i_buffer












def calculate_cpu(ld:"i_buffer.Buffer_output" , nd:"i_buffer.Buffer_output") -> metrics_and_reprots.CPU:  # Finished

    elapsed_time = nd.system_datas.metric_10s.s_time - ld.system_datas.metric_10s.s_time

    last_cpu_time = ld.system_datas.metric_10s.cpu_time

    now_cpu_time = nd.system_datas.metric_10s.cpu_time

    cpu_cores = nd.system_datas.metric_10s.effective_cpu_count

    delta_cpu_tick = now_cpu_time - last_cpu_time

    CLK_TCK = nd.system_datas.metric_10s.CLK_TCK

    delta_cpu_seconds = delta_cpu_tick / CLK_TCK

    cpu_utilization = (delta_cpu_seconds / elapsed_time) / cpu_cores

    cpu = metrics_and_reprots.CPU(cpu_utilization=cpu_utilization,cpu_cores=cpu_cores)

    return cpu


def calculate_memory(ld:"i_buffer.Buffer_output" , nd:"i_buffer.Buffer_output") -> metrics_and_reprots.Memory:  # Finished

    max_memory = nd.system_datas.metric_10s.max_memory

    n , sum_memory = 0 , 0

    maximom_memory = -1

    for metric_500ms in nd.system_datas.metrics_500ms:

        n += 1

        current_memory = metric_500ms.current_memory

        sum_memory += current_memory

        if current_memory > maximom_memory:

            maximom_memory = current_memory

    avg_memory = sum_memory / n

    avg_memory_utilization = avg_memory / max_memory

    max_memory_utilization = maximom_memory / max_memory

    memory = metrics_and_reprots.Memory(avg_memory_utilization=avg_memory_utilization,max_memory_utilization=max_memory_utilization)

    return memory
    

def calculate_disk(ld:"i_buffer.Buffer_output" , nd:"i_buffer.Buffer_output") -> metrics_and_reprots.Disk:  # Finished

    read_bytes = nd.system_datas.metric_10s.read_bytes

    write_bytes = nd.system_datas.metric_10s.write_bytes

    io_bytes = nd.system_datas.metric_10s.io_bytes

    disk = metrics_and_reprots.Disk(
        read_bytes=read_bytes,
        write_bytes=write_bytes,
        io_bytes=io_bytes
    )

    return disk

def calculate_network(ld:"i_buffer.Buffer_output" , nd:"i_buffer.Buffer_output") -> metrics_and_reprots.Network:  # Finished

    rx_bytes = nd.system_datas.metric_10s.rx_bytes

    tx_bytes = nd.system_datas.metric_10s.tx_bytes

    network = metrics_and_reprots.Network(rx_bytes=rx_bytes,tx_bytes=tx_bytes)

    return network













class Agregater:

    def __init__(self , service_name: str):  # Finished

        self.service_name = service_name

        self.running = False

        self.old_buffer_output = None

        self.new_timestamp = -1

        self.old_timestamp = -1

    def get_buffer_output(self , buffer_output: "i_buffer.Buffer_output"):  # Finished

        self.new_buffer_output = buffer_output

        # # debug

        # print("new_buffer_output getted")

        # # -----

        self.new_timestamp = time.time()

    

    def process(self) -> None:

        # # debug

        # print("agregater porcess started")

        # # -----

        outbounds = []

        # pack pre_schema

        if self.old_timestamp == -1:

            window = -1

            # # debug

            # print("window == -1")

            # # -----

        else:

            window = self.new_timestamp - self.old_timestamp

        if self.new_buffer_output.sdk_shemas != []:

            instance_id = self.new_buffer_output.sdk_shemas[0].instance_id

            # pack RED_metrics

            for sh in self.new_buffer_output.sdk_shemas:

                b = sh.bound_type

                # # debug

                # print(f"bound_type: {b}")

                # # -----

                if type(b) == metrics_and_reprots.Inbound:

                    # # debug

                    # print("inbound getted in agregater")

                    # # -----

                    inbound = b

                else:

                    outbounds.append(b)
            

            red_metrics = metrics_and_reprots.RED_metrics(inbound=inbound,outbounds=outbounds)

        else:

            instance_id = -1

            # pack RED_metrics

            red_metrics = None
        


        # pack USE_metrics

        if self.old_buffer_output == None:

            use_metrics = None

        else:

            ld = self.old_buffer_output

            nd = self.new_buffer_output

            cpu = calculate_cpu(ld=ld,nd=nd)

            memory = calculate_memory(ld=ld,nd=nd)

            disk = calculate_cpu(ld=ld,nd=nd)

            network = calculate_network(ld=ld,nd=nd)

            use_metrics = metrics_and_reprots.USE_metrics(cpu=cpu,memory=memory,disk=disk,network=network)



        # packing


        agregater_shema = metrics_and_reprots.Aggregator_schema(red_metrics=red_metrics,use_metrics=use_metrics)

        agent_state_report = metrics_and_reprots.Agent_state_report_shema(
            timestamp=self.new_timestamp,
            window=window,
            service_name=self.service_name,
            instance_id=instance_id,
            agregater_shema=agregater_shema
        )

        # # debug

        # print(f"agregater_output:\n{agent_state_report.__dict__}")

        # # -----


        # send to control_plane_client

        self.agent_components.agent.cp_c.get_item(agent_state_report)




    def main(self) -> None:  # Finished

        while self.running:

            ready = self.new_timestamp > self.old_timestamp

            if ready:

                self.process()

                self.old_timestamp = self.new_timestamp

                self.old_buffer_output = self.new_buffer_output

            time.sleep(0.2)


    def start_run(self,agent_components: "starters.Agent_components"):  # Finished

        self.agent_components = agent_components

        self.running = True

        self.thread = threading.Thread(target=self.main)

        self.thread.start()

    def stop_run(self):  # Finished

        self.running = False

        self.thread.join(timeout=30)

        if self.thread.is_alive():

            raise TimeoutError("CP_client in agent cant be stopped")


