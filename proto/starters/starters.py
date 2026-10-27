


from dataclasses import dataclass

from agent.buffer import buffer

from agent.system_data_getter import sdg

from agent.agregater import agregater

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from agent.agent_body import agent_body



@dataclass
class Start_msg:
    timestamp : float
    sender : str
    getters : str
    service_name: str
    starting: bool




@dataclass
class Start_order:
    timestamp : float
    sender : str
    getters : list[str]
    service_name: str


@dataclass
class Agent_components:
    b: buffer.Buffer
    s: sdg.System_data_getter_V11
    a: agregater.Agregater
    agent: "agent_body.Agent"


@dataclass
class Start_ping:
    timestamp : float
    sender : str
    getters : str
    starting: bool
    # instance_id: int



