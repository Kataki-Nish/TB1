

from typing import TYPE_CHECKING

from pathlib import Path

import subprocess

from schemas.agent.system_data_getter import test_01

import time

from dataclasses import dataclass

from typing import List , Dict

import os

import threading



if TYPE_CHECKING:

    from proto.starters import starters

    from agent.buffer import buffer

    from agent.agregater import agregater

    from agent.agent_heart import agent_heart



@dataclass
class Run_result:
    returncode: int
    stdout: str
    stderr: str



@dataclass
class Candidate:
    container_id: str
    image: str
    name: str







def separating_number(string: str) -> str:

    a = ""

    for ch in string:

        if ch.isdigit():

            a += ch

    return a




def is_number_in(string: str) -> bool:

    for ch in string:

        if ch.isdigit():

            return True

    else:

        return False




def run(order: str , inside_wsl: bool = False) -> Run_result:  # Finished

    # if "|" in order:

    #     order = f"sh -c {order}"

    # if inside_wsl == True:

    #     order = "wsl -d docker-desktop " + order

    # r = subprocess.run(order,shell=True,capture_output=True,text=True)

    if inside_wsl:

        r = subprocess.run(
            ["wsl", "-d", "docker-desktop", "sh", "-c", order],
            capture_output=True,
            text=True
        )

    else:

        r = subprocess.run(
            order,
            shell=True,
            capture_output=True,
            text=True
        )

    answer = Run_result(int(r.returncode) , str(r.stdout.strip()) , str(r.stderr.strip()))

    return answer







def input_setting(service_name:str) -> test_01.Target_selector_rules:  # Finished

    target_selector_rules = test_01.Target_selector_rules(service_name=service_name)

    return target_selector_rules





def orchestrator_detect() -> str:  # Finished

    if "KUBERNETES_SERVICE_HOST" in os.environ.keys():

        orchestrator = "kubernetes"

    elif run("test -f /app/docker-compose.yml",inside_wsl=True).returncode == 0 or run("test -f /app/compose.yaml",inside_wsl=True).returncode == 0:

        orchestrator = "docker_compose"

    else:

        orchestrator = "none"


    if orchestrator != "none": #(only for TB1)

        orchestrator = "unknown"


    return orchestrator





def container_runtime_detect() -> str:  # Finished

    if run("test -e /var/run/docker.sock",inside_wsl=True).returncode == 0 or run("docker info").returncode == 0 or "docker" in run("cat /proc/self/cgroup",inside_wsl=True).stdout:

        container_runtime = "docker"

    else:

        container_runtime = "unknown"

    return container_runtime




def cgroup_driver_detect() -> str:  # Finished

    cgroup_path_read = run("cat /proc/self/cgroup",inside_wsl=True).stdout

    if "system.slice" in cgroup_path_read:

        cgroup_driver = "systemd"

    elif "docker" in cgroup_path_read or "kubepods" in cgroup_path_read:

        cgroup_driver = "cgroupfs"

    else:

        cgroup_driver = "unknown"


    if cgroup_driver != "cgroupfs": #(only for TB1)

        cgroup_driver = "unknown"


    return cgroup_driver





def cgroup_version_detect() -> str:  # Finished


    if run("test -f /sys/fs/cgroup/cgroup.controllers",inside_wsl=True).returncode == 0:

        cgroup_version = "v2"

    else:

        cgroup_version = "unknown"


    return cgroup_version





def host_environment_detect() -> str:  # Finished

    is_docker_desktop = False

    # check docker-desktop WSL distribution {operation component}

    if "docker-desktop" in run("wsl -l -v").stdout:

        is_docker_desktop = True

    # check docker info metadata {operation component}
    
    if "docker-desktop" in run("docker info").stdout:

        is_docker_desktop = True

    # classify

    if is_docker_desktop == True:

        host_environment = "docker_desktop"

    else:

        host_environment = "unknown"

    return host_environment





def execution_environment_detector() -> test_01.Execution_env_metadata:  # Finished

    orchestrator = orchestrator_detect()

    container_runtime = container_runtime_detect()

    cgroup_driver = cgroup_driver_detect()

    cgroup_version = cgroup_version_detect()

    host_environment = host_environment_detect()

    execution_env_metadata = test_01.Execution_env_metadata(
        orchestrator=orchestrator,
        container_runtime=container_runtime,
        cgroup_driver=cgroup_driver,
        cgroup_version=cgroup_version,
        host_environment=host_environment
    )

    return execution_env_metadata






def enumerate_runtime_containers(orchestrator: str,container_runtime: str) -> List[str]:  # Finished

    #get the list of workloads from the container_runtime

    list_of_workloads = []
    
    if container_runtime=="docker" and orchestrator=="none":
    
        list_of_workloads : List[str] = run("docker ps").stdout.splitlines()

    else:

        if container_runtime=="unknown":

            print("enumeration_failed: container_runtime==unknown")

        else: #orchestrator==unknown

            print("enumeration_failed: orchestrator==unknown")

    return list_of_workloads






def normalize_candidates(list_of_workloads: List[str]) -> List[Candidate]:  # Finished

    candidates : List[Candidate] = []

    for l in list_of_workloads:

        l = l.split()

        cnd_id , img , nm = str(l[0]) , str(l[1]) , str(l[-1])

        candidates.append(Candidate(container_id=cnd_id,image=img,name=nm))


    return candidates




# Finished
def match_service_name_against_container_name(candidates: List[Candidate] , target_selector_rules: test_01.Target_selector_rules) -> Dict[int,bool]:

    candidates_index_matched: Dict[int,bool] = {}

    service_name = target_selector_rules.service_name

    i=0

    for cnd in candidates:

        if cnd.name == service_name:

            candidates_index_matched[i] = True
        
        else:

            candidates_index_matched[i] = False
            
        i+=1

    return candidates_index_matched






def resolve_ambiguity(candidates: List[Candidate] , candidates_index_matched: Dict[int,bool]) -> str:  # Finished

    s=0

    i=-1

    container_id = ""

    for k,v in candidates_index_matched.items():

        if v == True:

            s += 1

            i = k
    
    if s == 1:

        container_id = candidates[i].container_id
    
    else:

        if s == 0:

            print("resolve ambiguity failed: No candidates matched")
        
        else: # s > 1

            print("resolve ambiguity failed: candidates matched is more than 1")

    return container_id





def target_container_discovery(
        execution_env_metadata:test_01.Execution_env_metadata , 
        target_selector_rules:test_01.Target_selector_rules
        ) -> test_01.Target_container_identity:  # Finished

    list_of_workloads = enumerate_runtime_containers(execution_env_metadata.orchestrator,execution_env_metadata.container_runtime)

    # structured_workloads
    candidates = normalize_candidates(list_of_workloads)

    candidates_index_matched = match_service_name_against_container_name(candidates,target_selector_rules)

    container_id = resolve_ambiguity(candidates=candidates,candidates_index_matched=candidates_index_matched)

    target_container_identity = test_01.Target_container_identity(container_id=container_id)

    return target_container_identity







def PID_discovery(
        execution_env_metadata: test_01.Execution_env_metadata ,
        target_container_identity: test_01.Target_container_identity
        ) -> test_01.PID_discovery_output:  # Finished

    container_runtime = execution_env_metadata.container_runtime
    host_environment = execution_env_metadata.host_environment
    container_id = target_container_identity.container_id

    host_PID = "-1"

    if container_runtime == "docker":

        a = run(f"docker inspect  -f  '{{{{.State.Pid}}}}' {container_id}")

        if a.returncode == 0:

            runtime_pid: str = a.stdout.strip("'")

        else:

            print(f"PID_discovery failed: call ('docker inspect  -f  '{{{{.State.Pid}}}}' container_id') be failed\nError: {a.stderr}")

            runtime_pid = None

    else:

        print("PID_discovery failed: container_runtime != 'docker' ")

        runtime_pid = None
    

    if host_environment == "docker_desktop":

        r0 : Run_result = run("ls /proc | grep '^[0-9]'",inside_wsl=True)

        if r0.returncode == 0:

            l_pids : List[str] = r0.stdout.splitlines()

        else:

            print(f"PID_discovery failed: call (ls /proc | grep '^[0-9]') be failed\nError: {r0.stderr}")

            l_pids = []

        Errors: List[str] = [] 

        for p in l_pids:

            r1 : Run_result = run(f"cat /proc/{p}/status | grep NSpid",inside_wsl=True)

            if r1.returncode == 0:

                pids : List[str] = r1.stdout.split()

            else:

                Errors.append(f"call (cat /proc/{p}/status | grep NSpid) failed\n Error: {r1.stderr}")

                #print(f"call (cat /proc/{p}/status | grep NSpid) failed\n Error: {r1.stderr}")

                pids = []

            if runtime_pid in pids:

                host_PID = p

                break


        else:

            print("PID_discovery failed: there is NO visible_pid that have runtime_pid\nHint: if visible_pid have runtime_pid -> host_PID = visible_pid \nelse: failed")

            for er in Errors:

                print(er)


    else:

        print("PID_discovery failed: host_environment != 'docker_desktop' ")


    return test_01.PID_discovery_output(runtime_pid=runtime_pid,host_PID=host_PID)






def cgroup_discovery(execution_env_metadata: test_01.Execution_env_metadata,host_PID: str) -> str:  # Finished

    cgroup_version = execution_env_metadata.cgroup_version

    raw_cgroup_path = run(f"cat /proc/{host_PID}/cgroup",inside_wsl=True).stdout


    # parse according to cgroup_version

    if cgroup_version == "v2":

        raw_cgroup_path_l = ["", "" ,""]

        i = 0

        for ch in raw_cgroup_path:

            if ch != ":":

                raw_cgroup_path_l[i] += ch
            
            else:

                i+=1

    else:

        print("cgroup_discovery , parse according to cgroup_version failed: cgroup_version != 'v2' ")

    
    relative_path : str = raw_cgroup_path_l[2]



    # build absolute path

    if cgroup_version == "v2":

        cgroup_version_root : str = "/sys/fs/cgroup"
    
    else:

        print("cgroup_discovery , build absolute path failed: cgroup_version != 'v2' ")
    
    cgroup_candidate_absolute_path : str = cgroup_version_root + relative_path



    # validate path exists

    cgroup_absolute_path = ""

    if run(f"test -d {cgroup_candidate_absolute_path}",inside_wsl=True).returncode == 0:

    # if Path(cgroup_candidate_absolute_path).exists():

        cgroup_absolute_path : str = cgroup_candidate_absolute_path

    else:

        print("cgroup_discovery , validate path exists failed: cgroup_candidate_absolute_path does not exist as directory")


    return cgroup_absolute_path










def namespace_discovery(host_PID: str) -> str:  # Finished


    namespace_handler_path = ""

    namespace_root = f"/proc/{host_PID}/ns"

    # operation

    if run(f"test -d {namespace_root}",inside_wsl=True).returncode == 0:

    # if Path(namespace_root).exists():

        namespace_handler_path = namespace_root

    else:

        print("namespace_discovery failed: namespace_root as the path does not exist")

    return namespace_handler_path


    




def workload_resolver(
        execution_env_metadata: test_01.Execution_env_metadata,
        target_container_identity:test_01.Target_container_identity
        ) -> test_01.Workload_resolver_output:  # Finished

    pids = PID_discovery(execution_env_metadata=execution_env_metadata,target_container_identity=target_container_identity)
    runtime_pid = pids.runtime_pid
    host_PID = pids.host_PID
    cgroup_absolute_path = cgroup_discovery(execution_env_metadata=execution_env_metadata,host_PID=host_PID)
    namespace_handler_path = namespace_discovery(host_PID=host_PID)

    return test_01.Workload_resolver_output(runtime_pid,host_PID,cgroup_absolute_path,namespace_handler_path)






def parse_fields_to_list(raw_fields: str) -> List[str]:  # Finished

    state_fields = raw_fields.split()

    # state_fields : List[str] = []

    # i = 0

    # j = 0

    # state_fields[i] = ""

    # for ch in raw_fields:

    #     if ch != " ":

    #         if ch == "(":

    #             j = 1

    #         elif ch == ")":

    #             j = 0

    #         state_fields[i] += ch
    
    #     else: #ch == " "

    #         if j == 0:

    #             i += 1

    #             state_fields[i] = ""

    return state_fields





def process_starttime_finder(host_PID: str) -> int:  # Finished

    raw_fields = run(f"cat /proc/{host_PID}/stat" , inside_wsl=True).stdout

    # parse fields to list

    state_fields = parse_fields_to_list(raw_fields)

    # extract field[21] {field 22}

    process_starttime = int(state_fields[21])

    return process_starttime





def container_starttime_finder(container_id: str) -> str:

    r = run(f"docker inspect -f '{{{{.State.StartedAt}}}}' {container_id}")

    if r.returncode == 0:

        container_starttime = r.stdout

    else:

        print(f"call (docker inspect -f '{{{{.State.StartedAt}}}}' {container_id}) failed \nError: {r.stderr}")

        raise ValueError

    return container_starttime








def build_outputs(
        execution_env_metadata: test_01.Execution_env_metadata,
        target_container_identity: test_01.Target_container_identity,
        workload_resolver_output: test_01.Workload_resolver_output,
        container_starttime: int
) -> test_01.Discoverer_output:  # Finished

    env_datas = test_01.Env_datas(execution_env_metadatas=execution_env_metadata,target_container_identity=target_container_identity)

    discoverer_results = test_01.Discoverer_results(
        host_PID = workload_resolver_output.host_PID ,
        cgroup_absolute_path = workload_resolver_output.cgroup_absolute_path ,
        namespace_handler_path = workload_resolver_output.namespace_handler_path ,
        cgroup_version = execution_env_metadata.cgroup_version
    )

    identity_datas = test_01.Identity_datas(runtime_pid=workload_resolver_output.runtime_pid , container_starttime=container_starttime)


    discoverer_output = test_01.Discoverer_output(env_datas=env_datas , discoverer_results=discoverer_results , identity_datas=identity_datas)

    return discoverer_output






class Discoverer:  # Finished

    def __init__(self , service_name: str):

        self.service_name = service_name
        self.first_discovery = True


    def process(self) -> test_01.Discoverer_output:

        if self.first_discovery:

            self.target_selector_rules = input_setting(self.service_name)
            
            self.first_discovery = False

        self.execution_env_metadata = execution_environment_detector()

        self.target_container_identity = target_container_discovery(execution_env_metadata=self.execution_env_metadata , target_selector_rules=self.target_selector_rules)

        self.workload_resolver_output = workload_resolver(execution_env_metadata=self.execution_env_metadata , target_container_identity=self.target_container_identity)

        self.container_starttime = container_starttime_finder(container_id=self.target_container_identity.container_id)

        self.discoverer_output = build_outputs(
            execution_env_metadata=self.execution_env_metadata , 
            target_container_identity=self.target_container_identity , 
            workload_resolver_output=self.workload_resolver_output , 
            container_starttime=self.container_starttime
            )

        return self.discoverer_output





class Cache:  # Finished

    def process(self , discoverer_output: test_01.Discoverer_output) -> None:

        self.env_datas = discoverer_output.env_datas

        self.discoverer_results = discoverer_output.discoverer_results

        self.identity_datas = discoverer_output.identity_datas

    def get_env_datas(self) -> test_01.Env_datas:

        return self.env_datas

    def get_discoverer_results(self) -> test_01.Discoverer_results:

        return self.discoverer_results

    def get_identity_datas(self) -> test_01.Identity_datas:

        return self.identity_datas








def time_recorder() -> float:  # Finished

    s_time = time.time()

    return s_time



def CLK_TCK_getter() -> int:  # Finished

    a = run("getconf CLK_TCK" , inside_wsl=True)

    if a.returncode == 0:

        CLK_TCK = a.stdout

    else:

        print(f"call getconf CLK_TCK be failed , Error: {a.stderr}")

        CLK_TCK = ""

    return int(CLK_TCK)




# cgroup_metrics_reader


def Memory_utilization_part2(cgroup_absolute_path: str) -> int:  # Finished

    r = run(f"cat {cgroup_absolute_path}/memory.max", inside_wsl=True)

    a = r.stdout

    if a == "max":

        r2 = run("awk '/^MemTotal:/ {print $2}' /proc/meminfo", inside_wsl=True)  #{max_memory == host_total_memory})

        max_memory = 1024 * int(separating_number(r2.stdout))

    else:

        max_memory = int(a)

    return max_memory







def placement_cpu_count_getter(cgroup_absolute_path: str) -> int:  # Finished

    r = run(f"cat {cgroup_absolute_path}/cpuset.cpus.effective",inside_wsl=True)

    a : str = r.stdout

    l = a.split(",")

    placement_cpu_count = 0

    for c in l:

        if "-" in c:

            c = c.split("-")  #List[start,end]

            placement_cpu_count += (int(c[1]) - int(c[0])) + 1

        else:

            placement_cpu_count += 1

    return placement_cpu_count





def quota_cpu_count_getter(cgroup_absolute_path: str , placement_cpu_count: int) -> float:  # Finished

    r = run(f"cat {cgroup_absolute_path}/cpu.max",inside_wsl=True)

    a : str = r.stdout

    if "max" in a:

        quota_cpu_count = placement_cpu_count
    
    else:

        #quota_cpu_count = quota / period

        l = a.split()

        quota_cpu_count = int(l[0]) / int(l[1])

    return quota_cpu_count






def CPU_utilization_part2(cgroup_absolute_path: str) -> float:  # Finished

    placement_cpu_count = placement_cpu_count_getter(cgroup_absolute_path)

    quota_cpu_count = quota_cpu_count_getter(cgroup_absolute_path , placement_cpu_count)

    # calculate effective_cpu_count

    effective_cpu_count = min(placement_cpu_count , quota_cpu_count)

    return effective_cpu_count





def Memory_utilization_part1(cgroup_absolute_path: str) -> int:  # Finished

    r = run(f"cat {cgroup_absolute_path}/memory.current" , inside_wsl=True)

    current_memory = int(r.stdout)

    return current_memory





def CPU_utilization_part1_per_container(cgroup_absolute_path: str) -> float:

    r = run(f"cat {cgroup_absolute_path}/cpu.stat",inside_wsl=True)

    if r.returncode == 0:

        a = r.stdout.splitlines()

        for s in a:

            if "usage_usec" in s:

                n = int(separating_number(s))

                break
        
        else:

            print(f"get usage_usec failed\n Error: \n{a}\n Don't have usage_usec section")

            raise ValueError


        cpu_time = n / 1000000

        return cpu_time

    else:

        print(f"call (cat {cgroup_absolute_path}/cpu.stat) failed \nError: {r.stderr}")

        raise ValueError





def Disk_utilization_getter_per_container(cgroup_absolute_path: str) -> test_01.Disk_utilization:

    r = run(f"cat {cgroup_absolute_path}/io.stat",inside_wsl=True)

    read_bytes , write_bytes = 0 , 0

    if r.returncode == 0:

        a: List[str] = r.stdout.splitlines()

        for s in a:

            e: List[str] = s.split()

            for i in e:

                if "rbytes" in i:

                    read_bytes += int(separating_number(i))

                elif "wbytes" in i:

                    write_bytes += int(separating_number(i))


        io_bytes = read_bytes + write_bytes

        disk_utilization = test_01.Disk_utilization(read_bytes=read_bytes,write_bytes=write_bytes,io_bytes=io_bytes)

        return disk_utilization

    else:

        print(f"call (cat {cgroup_absolute_path}/io.stat) failed\nError: {r.stderr}")

        raise ValueError















# Kernel_interface_reader


def CPU_utilization_part1_per_process(host_PID: str) -> int:  # Finished

    raw_fields = run(f"cat /proc/{host_PID}/stat" , inside_wsl=True).stdout

    # parse fields to list

    state_fields = parse_fields_to_list(raw_fields)

    # extract field[13] and field[14] {field 14 , field 15}

    utime  = int(state_fields[13])

    stime  = int(state_fields[14])

    cpu_time = utime + stime

    return cpu_time




def Disk_utilization_getter_per_process(host_PID: str) -> test_01.Disk_utilization:  # Finished

    r = run(f"cat /proc/{host_PID}/io",inside_wsl=True)

    io_l: List[str] = r.stdout.splitlines()

    for i in io_l:

        if "read_bytes" in i:

            read_bytes = int(separating_number(i))
        
        elif "write_bytes" in i:

            write_bytes = int(separating_number(i))
    
    io_bytes = read_bytes + write_bytes

    disk_utilization = test_01.Disk_utilization(read_bytes=read_bytes,write_bytes=write_bytes,io_bytes=io_bytes)

    return disk_utilization




def Network_utilization_getter(host_PID: str) -> test_01.Network_utilization:  # Finished

    r = run(f"cat /proc/{host_PID}/net/dev",inside_wsl=True)

    l_s: List[str] = r.stdout.splitlines()

    al : List[List[str]] = []

    for s in l_s:

        if "lo" not in s:

            al.append(s.split())

    
    rx_bytes , tx_bytes = 0 , 0
    
    for a in al:

        if is_number_in(a):

            rx_bytes += int(a[1])  #{Receive_bytes}

            tx_bytes += int(a[9])  #{Transmit_bytes}

    network_utilization = test_01.Network_utilization(rx_bytes=rx_bytes,tx_bytes=tx_bytes)

    return network_utilization






class Metric_reader:

    def __init__(self , buffer: "buffer.Buffer"):

        self.buffer = buffer

    def get_discoverer_results(self,discoverer_results: test_01.Discoverer_results) -> None:  # Finished

        self.discoverer_results = discoverer_results

    
    def buffer_10s_push(self , metric_10s: test_01.Metric_10s) -> None:  # Finished

        self.buffer.get_metric_10s(metric_10s=metric_10s)
        

        # # just for test sdg:

        # print("\nmetric_10s : ")

        # print(f"{metric_10s.__dict__}\n")


    def buffer_500ms_push(self , metric_500ms: test_01.Metric_500ms) -> None:  # Finished

        self.buffer.get_metric_500ms(metric_500ms=metric_500ms)

        # # just for test sdg:

        # print("\nmetric_500ms : ")

        # print(f"{metric_500ms.__dict__}\n")


    def reader_10s(self) -> test_01.Metric_10s:  # Finished

        s_time = time_recorder()

        CLK_TCK = CLK_TCK_getter()

        # cgroup_metrics_reader

        max_memory = Memory_utilization_part2(self.discoverer_results.cgroup_absolute_path)

        effective_cpu_count = CPU_utilization_part2(self.discoverer_results.cgroup_absolute_path)

        cpu_time = CPU_utilization_part1_per_container(self.discoverer_results.cgroup_absolute_path)

        disk_utilization = Disk_utilization_getter_per_container(self.discoverer_results.cgroup_absolute_path)

        io_bytes = disk_utilization.io_bytes

        read_bytes = disk_utilization.read_bytes

        write_bytes = disk_utilization.write_bytes


        # Kernel_interface_reader

        network_utilization: test_01.Network_utilization = Network_utilization_getter(self.discoverer_results.host_PID)

        rx_bytes = network_utilization.rx_bytes

        tx_bytes = network_utilization.tx_bytes

        # packing

        metric_10s = test_01.Metric_10s(
            timestamp=time.time(),
            s_time=s_time,
            CLK_TCK=CLK_TCK,
            effective_cpu_count=effective_cpu_count,
            cpu_time=cpu_time,
            max_memory=max_memory,
            read_bytes=read_bytes,
            write_bytes=write_bytes,
            io_bytes=io_bytes,
            rx_bytes=rx_bytes,
            tx_bytes=tx_bytes
        )

        return metric_10s



    def reader_500ms(self) -> test_01.Metric_500ms:  # Finished

        # cgroup_metrics_reader

        current_memory = Memory_utilization_part1(self.discoverer_results.cgroup_absolute_path)

        # packing

        metric_500ms = test_01.Metric_500ms(timestamp=time.time(),current_memory=current_memory)

        return metric_500ms
        

    def read_raw_metrics(self,allocated_time: float) -> None:  # Finished

        t1 = time.time()

        metric_10s = self.reader_10s()

        self.buffer_10s_push(metric_10s)

        t2 = time.time()

        elapsed_time = t2 - t1

        remain_time = allocated_time - elapsed_time

        while remain_time > 0:

            metric_500ms = self.reader_500ms()

            self.buffer_500ms_push(metric_500ms)

            time.sleep(0.5)

            t2 = time.time()

            elapsed_time = t2 - t1

            remain_time = allocated_time - elapsed_time

















@dataclass
class Sdg_components:
    discoverer: Discoverer
    cache: Cache
    metric_reader: Metric_reader



class System_data_getter_V11:

    def __init__(self,service_name: str):

        self.service_name = service_name

        self.running = False


    def health_check_iteration(self) -> None:

        #health_check loop: (every 10_sec)

        t1 = time.time()

        self.components

        d = self.components.discoverer

        c  = self.components.cache

        m = self.components.metric_reader


        container_id = c.get_env_datas().target_container_identity.container_id

        runtime_pid = run(f"docker inspect  -f  '{{{{.State.Pid}}}}' {container_id}").stdout.strip("'")

        if runtime_pid != c.get_identity_datas().runtime_pid:

            print("rediscovery_01")  # debug

            discoverer_output = d.process()  # discovery(run discoverer) [discoverer]

            c.process(discoverer_output=discoverer_output)  # record discoverer_output [cache]

            m.get_discoverer_results(c.get_discoverer_results())  # update discoverer_results data in metric_reader [metric_reader | cache]

            t2 = time.time()

            allocated_time = max(0 , 10 - (t2 - t1))

            m.read_raw_metrics(allocated_time)  # read_raw_metrics(run metric_reader) [metric_reader]

        else:

            if container_starttime_finder(container_id) != c.get_identity_datas().container_starttime:  # starttime != cached_starttime

                print("rediscovery_02")  # debug

                discoverer_output = d.process()  # discovery(run discoverer) [discoverer]

                c.process(discoverer_output=discoverer_output)  # record discoverer_output [cache]

                m.get_discoverer_results(c.get_discoverer_results())  # update discoverer_results data in metric_reader [metric_reader | cache]

                t2 = time.time()

                allocated_time = max(0 , 10 - (t2 - t1))

                m.read_raw_metrics(allocated_time)  # read_raw_metrics(run metric_reader) [metric_reader]

            else:  # every thing is good .

                t2 = time.time()

                allocated_time = max(0 , 10 - (t2 - t1))

                m.read_raw_metrics(allocated_time)  # read_raw_metrics(run metric_reader) [metric_reader]





        """

        if not /proc/<host_PID[cache(identity_datas(host_PID))]> exists:

            1. discoverer_output = d.process()     #discovery(run discoverer) [discoverer]

            2. c.process(discoverer_output=discoverer_output)     #record discoverer_output [cache]

            3. m.get_discoverer_results(c.get_discoverer_results())

            4. t2 = time.time()

            5. allocated_time = max(0 , 10 - (t2 - t1))

            6. m.read_raw_metrics(allocated_time)     #read_raw_metrics(run metric_reader) [metric_reader]

        else:

            if /proc/<pid>/stat (starttime) != cached_starttime[cache(identity_datas(starttime))]:

                1. discoverer_output = d.process()     #discovery(run discoverer) [discoverer]

                2. c.process(discoverer_output=discoverer_output)     #record discoverer_output [cache]

                3. m.get_discoverer_results(c.get_discoverer_results())

                4. t2 = time.time()

                5. allocated_time = max(0 , 10 - (t2 - t1))

                6. m.read_raw_metrics(allocated_time)     #read_raw_metrics(run metric_reader) [metric_reader]

            else:

                1. t2 = time.time()

                2. allocated_time = max(0 , 10 - (t2 - t1))

                3. m.read_raw_metrics(allocated_time)     #read_raw_metrics(run metric_reader) [metric_reader]

        """




    def main(self):  #working pipeline: (start only when system_data_getter started(first_start))

        t1 = time.time()

        d = Discoverer(service_name=self.service_name)
        c = Cache()
        m = Metric_reader(self.agent_components.b)

        discoverer_output = d.process()  #1.discovery(run discoverer){first_discovery} [discoverer]

        c.process(discoverer_output=discoverer_output)  #2.record discoverer_output [cache]

        m.get_discoverer_results(c.get_discoverer_results())

        self.components = Sdg_components(discoverer=d , cache=c , metric_reader=m)

        t2 = time.time()

        allocated_time = max(0 , 10 - (t2 - t1))

        m.read_raw_metrics(allocated_time)  # read_raw_metrics(run metric_reader) [metric_reader]

        #evey 10 sec:
        
        while self.running: # need independent thread/loop , so i creat while loop just to say its a loop , it be changed later .

            self.health_check_iteration()



    def start_run(self, agent_components: "starters.Agent_components"):

        self.agent_components = agent_components

        self.running = True

        self.thread = threading.Thread(target=self.main)

        self.thread.start()

    def stop_run(self):

        self.running = False

        self.thread.join(timeout=30)

        if self.thread.is_alive():

            raise TimeoutError("sdg in agent cant be stopped")









# #agent run example: should be in deploy_folder

# start_msg: starters.Start_msg #from SDK[starter]

# if start_msg:  # SDK_client and control_plane client and starter created at the first(when SDK created , agent_body and whole_of_CP created too) 
#                # and they don't need configuraion , and they are function NOT class , and they are in agent_body .

#     start_order = starters.Start_order(timestamp=time.time(),sender="starter",getters=["sdg","buffer","agregater"],service_name=start_msg.service_name)

#     sdg = System_data_getter_V11(start_order.service_name)

#     b = buffer.Buffer(start_order.service_name)

#     a = agregater.Agregater(start_order.service_name)

#     h = agent_heart.Agent_heart(start_order.service_name)

#     agent_components = starters.Agent_components(b=b , s=sdg , a=a , h=h)

#     for e in [sdg,b,a,h]:  # for each element in agent_components:

#         e.main(agent_components)  #run only 1 time

    


















