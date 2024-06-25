import anthropic
import random
import json
import os
import argparse
import logging
from datetime import datetime
from typing import List
from pydantic import BaseModel
import time

__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2024, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@holistech.de"


class AgentDescription(BaseModel):
    name: str
    role: str
    personality: str
    knowledge_base: str


class Agent:
    def __init__(self, description: AgentDescription):
        self.name = description.name
        self.role = description.role
        self.personality = description.personality
        self.knowledge_base = description.knowledge_base
        self.conversation_history = []

    def add_to_history(self, speaker, message):
        self.conversation_history.append({"speaker": speaker, "message": message})

    def get_conversation_history(self, history_size):
        return self.conversation_history[-history_size:]

    def load_history(self, history):
        self.conversation_history = history


class Debate:
    def __init__(self, debate_text, agents, max_turns, log_dir, history_size, prompt_template):
        self.debate_text = debate_text
        self.agents = agents
        self.max_turns = max_turns
        self.current_turn = 0
        self.full_conversation = []
        self.log_dir = log_dir
        self.debate_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history_size = history_size
        self.prompt_template = prompt_template

    def run_debate(self, api_client):
        self._load_or_init_debate()

        while self.current_turn < self.max_turns:
            for agent in self.agents:
                response = self.generate_response(api_client, agent)
                self._log_response(agent.name, response)
                for other_agent in self.agents:
                    other_agent.add_to_history(agent.name, response)
            self.current_turn += 1
            self._save_debate_state()
            logging.info(f"Completed turn {self.current_turn}/{self.max_turns}")

    def generate_response(self, api_client, agent):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                prompt = self.prompt_template.format(
                    agent_name=agent.name,
                    agent_role=agent.role,
                    agent_personality=agent.personality,
                    agent_knowledge_base=agent.knowledge_base,
                    debate_text=self.debate_text,
                    conversation_history=json.dumps(agent.get_conversation_history(self.history_size), indent=2)
                )

                response = api_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    prompt=prompt,
                    max_tokens_to_sample=2048,
                )
                return response.completion
            except Exception as e:
                logging.error(f"API call failed: {e}. Attempt {attempt + 1} of {max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def _log_response(self, speaker, message):
        self.full_conversation.append({"speaker": speaker, "message": message})
        self._save_debate_state()

    def _save_debate_state(self):
        debate_state = {
            "debate_text": self.debate_text,
            "current_turn": self.current_turn,
            "full_conversation": self.full_conversation,
            "agent_states": {
                agent.name: {
                    "conversation_history": agent.conversation_history
                } for agent in self.agents
            }
        }
        with open(os.path.join(self.log_dir, f"debate_{self.debate_id}.json"), "w") as f:
            json.dump(debate_state, f, indent=2)

    def _load_or_init_debate(self):
        debate_file = os.path.join(self.log_dir, f"debate_{self.debate_id}.json")
        if os.path.exists(debate_file):
            with open(debate_file, "r") as f:
                debate_state = json.load(f)
            self.current_turn = debate_state["current_turn"]
            self.full_conversation = debate_state["full_conversation"]
            for agent in self.agents:
                agent.load_history(debate_state["agent_states"][agent.name]["conversation_history"])
            logging.info(f"Resumed debate from turn {self.current_turn}")
        else:
            initial_statement = f"Moderator: Here's the text we'll be discussing:\n\n{self.debate_text}"
            self._log_response("Moderator", initial_statement)
            for agent in self.agents:
                agent.add_to_history("Moderator", initial_statement)
            logging.info("Started new debate")

    def export_for_fine_tuning(self):
        fine_tuning_data = []
        for turn in self.full_conversation:
            fine_tuning_data.append({
                "prompt": self.prompt_template.format(
                    agent_name=turn['speaker'],
                    agent_role="[Role]",
                    agent_personality="[Personality]",
                    agent_knowledge_base="[Knowledge Base]",
                    debate_text=self.debate_text,
                    conversation_history=json.dumps(self.full_conversation[:-1], indent=2)
                ),
                "completion": turn['message']
            })
        return fine_tuning_data


def load_debate_texts(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def load_agent_descriptions(file_path) -> List[AgentDescription]:
    with open(file_path, "r") as f:
        descriptions = json.load(f)
    return [AgentDescription(**desc) for desc in descriptions]


def load_prompt_template(file_path):
    with open(file_path, "r") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Run Debate")
    parser.add_argument("--text_list", required=True, help="Path to file containing debate text filenames")
    parser.add_argument("--text_dir", required=True, help="Directory containing debate texts")
    parser.add_argument("--log_dir", required=True, help="Directory for storing conversation logs")
    parser.add_argument("--output_dir", required=True, help="Directory for storing output files")
    parser.add_argument("--agent_descriptions", required=True, help="Path to JSON file containing agent descriptions")
    parser.add_argument("--prompt_template", required=True, help="Path to prompt template file")
    parser.add_argument("--max_turns", type=int, default=10, help="Maximum number of turns in the debate")
    parser.add_argument("--history_size", type=int, default=10,
                        help="Number of recent messages to include in conversation history")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logging.error("ANTHROPIC_API_KEY not found")
        raise ValueError("ANTHROPIC_API_KEY not found")

    client = anthropic.Client(api_key)

    debate_texts = load_debate_texts(args.text_list)
    debate_text_filename = random.choice(debate_texts)
    with open(os.path.join(args.text_dir, debate_text_filename), "r") as f:
        debate_text = f.read()

    agent_descriptions = load_agent_descriptions(args.agent_descriptions)
    agents = [Agent(desc) for desc in agent_descriptions]

    prompt_template = load_prompt_template(args.prompt_template)

    debate = Debate(debate_text, agents, args.max_turns, args.log_dir, args.history_size, prompt_template)

    debate.run_debate(client)

    # Export the debate for fine-tuning
    fine_tuning_data = debate.export_for_fine_tuning()
    with open(os.path.join(args.output_dir, "fine_tuning_data.json"), "w") as f:
        json.dump(fine_tuning_data, f, indent=2)

    logging.info("Debate has been completed and saved. Fine-tuning data has been exported.")


if __name__ == "__main__":
    main()
