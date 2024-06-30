import yaml
from typing import List
from pydantic import BaseModel


class AgentDescription(BaseModel):
    name: str
    role_type: str
    lead_role: bool
    system_prompt: str
    doc_prompt_template: str


class Agent:
    def __init__(self, description: AgentDescription):
        self.name = description.name
        self.role_type = description.role_type
        self.lead_role = description.lead_role
        self.system_prompt = description.system_prompt
        self.doc_prompt_template = description.doc_prompt_template
        self.conversation_history = []

    def add_to_history(self, speaker, message):
        self.conversation_history.append({"speaker": speaker, "message": message})

    def get_conversation_history(self, history_size):
        return self.conversation_history[-history_size:]

    def load_history(self, history):
        self.conversation_history = history


def load_agent_descriptions(file_path) -> List[AgentDescription]:
    with open(file_path, "r") as f:
        descriptions = yaml.safe_load(f)
    return [AgentDescription(**desc) for desc in descriptions]
