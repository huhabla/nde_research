from typing import List, Dict

import anthropic
import openai
import json
import os
import logging
from datetime import datetime
import time
import yaml
from yaml import dump
from nde_research.agents import Agent

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


class Conversation:
    def __init__(self, api_key, model, document, agents, max_turns, log_dir, history_size):
        self.document = document
        self.agents: List[Agent] = agents
        self.max_turns = max_turns
        self.current_turn = 0
        self.full_conversation = []
        self.log_dir = log_dir
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history_size = history_size
        self.max_tokens = 1024
        self.model = model
        if self.model == "anthropic":
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = openai.OpenAI(api_key=api_key)
        self.api_log = []

    def run_conversation(self):
        self._load_or_init_conversation()

        try:
            while self.current_turn < self.max_turns:
                for agent in self.agents:
                    response, metadata = self.generate_response(agent, (self.current_turn + 1) == self.max_turns)
                    self._log_response(agent.name, response, metadata)
                    for other_agent in self.agents:
                        other_agent.add_to_history(agent.name, response)
                self.current_turn += 1
                self._save_conversation_state()
                logging.info(f"Completed turn {self.current_turn}/{self.max_turns}")
        except Exception as e:
            logging.error(f"Error during conversation: {e}")
            raise
        finally:
            self._save_api_log()

    def compile_conversation_for_agent_anthropic(self, agent, last_round=False):
        conversation = []
        prev_role = None

        for i, entry in enumerate(agent.get_conversation_history(self.history_size)):
            if entry["speaker"] == "__document__":
                role = "user"
            else:
                role = "user" if entry['speaker'] != agent.name else "assistant"

            if i == 0 and role == "assistant":
                conversation.append({"role": "user", "content": "Please continue."})

            if role == "user" and prev_role == "user":
                conversation.append({"role": "assistant", "content": "Please continue."})

            conversation.append({"role": role, "content": entry['message']})
            prev_role = role

        if not conversation or conversation[-1]['role'] == "assistant":
            if last_round:
                conversation.append({"role": "user",
                                     "content": "Please formulate your final statements, "
                                                "we are running out of time, find your final words."})
            else:
                conversation.append({"role": "user", "content": "Please continue."})

        return conversation

    def compile_conversation_for_agent_openai(self, agent, last_round=False):
        conversation = []
        for entry in agent.get_conversation_history(self.history_size):
            # The first entry is the document and therefor the user role
            if entry["speaker"] == "__document__":
                role = "user"
            else:
                role = "user" if entry['speaker'] != agent.name else "assistant"
            conversation.append({"role": role, "content": entry['message']})

        return conversation

    def _request_anthropic(self, conversation, system_message):
        client: anthropic.Anthropic = self.client
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=self.max_tokens,
            messages=conversation,
            system=system_message,
            temperature=0.7
        )
        self.api_log[-1]["response"] = response.model_dump()
        return response.content[0].text, ""

    def _request_openai(self, conversation: List[Dict], system_message):
        openai_messages = [{"role": "system", "content": system_message}]
        openai_messages.extend(conversation)
        client: openai.OpenAI = self.client
        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            max_tokens=self.max_tokens,
            messages=openai_messages,
            temperature=0.7
        )
        self.api_log[-1]["response"] = response.model_dump()
        return response.choices[0].message.content, ""

    def generate_response(self, agent, last_round=False):
        max_retries = 1
        for attempt in range(max_retries):
            try:
                if self.model == "anthropic":
                    conversation = self.compile_conversation_for_agent_anthropic(agent=agent, last_round=last_round)
                else:
                    conversation = self.compile_conversation_for_agent_openai(agent=agent, last_round=last_round)

                self.api_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "agent": agent.name,
                    "system_message": agent.system_prompt,
                    "conversation": conversation
                })

                if self.model == "anthropic":
                    statement = self._request_anthropic(conversation=conversation, system_message=agent.system_prompt)
                else:
                    statement = self._request_openai(conversation=conversation, system_message=agent.system_prompt)

                return statement

            except Exception as e:
                logging.error(f"API call failed: {e}. Attempt {attempt + 1} of {max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def _extract_metadata(self, response):
        # Placeholder for metadata extraction
        # Implement logic to extract metadata from the response
        return {"confidence": 0.8, "source": "document_section_1"}

    def _log_response(self, speaker, message, metadata):
        self.full_conversation.append({"speaker": speaker, "message": message, "metadata": metadata})
        self._save_conversation_state()

    def _save_conversation_state(self):
        conversation_state = {
            "document": self.document,
            "current_turn": self.current_turn,
            "full_conversation": [
                {
                    "turn": i + 1,
                    "speaker": entry["speaker"],
                    "message": entry["message"],
                }
                for i, entry in enumerate(self.full_conversation)
            ],
            "agent_states": {
                agent.name: {
                    "role_type": agent.role_type,
                    "lead_role": agent.lead_role,
                    "conversation_history": [
                        {
                            "speaker": entry["speaker"],
                            "message": entry["message"]
                        }
                        for entry in agent.conversation_history
                    ]
                }
                for agent in self.agents
            }
        }

        with open(os.path.join(self.log_dir, f"conversation_state_{self.conversation_id}.yaml"), "w",
                  encoding='utf-8') as f:
            yaml.dump(conversation_state, f,default_flow_style=False, allow_unicode=True,
                      sort_keys=False)

    def _save_api_log(self):
        with open(os.path.join(self.log_dir, f"api_log_{self.conversation_id}.json"), "w") as f:
            json.dump(self.api_log, f, indent=2)

    def _load_or_init_conversation(self):
        conversation_file = os.path.join(self.log_dir, f"conversation_state_{self.conversation_id}.json")
        if os.path.exists(conversation_file):
            with open(conversation_file, "r") as f:
                conversation_state = json.load(f)
            self.current_turn = conversation_state["current_turn"]
            self.full_conversation = conversation_state["full_conversation"]
            for agent in self.agents:
                agent.load_history(conversation_state["agent_states"][agent.name]["conversation_history"])
            logging.info(f"Resumed conversation from turn {self.current_turn}")
        else:
            # Always add the document prompt at the beginning of the conversation to the history of each agent
            for agent in self.agents:
                doc_prompt = agent.doc_prompt_template.format(document=self.document)
                agent.add_to_history("__document__", doc_prompt)
            # If we have a lead agent, then he must be the first who makes the opening statement
            lead_agents = [agent for agent in self.agents if agent.lead_role is True]
            if lead_agents:
                lead_agent = lead_agents[0]  # use he first lead agent
                initial_statement, metadata = self.generate_response(lead_agent)
                self._log_response(lead_agent.name, initial_statement, metadata)
                for agent in self.agents:
                    agent.add_to_history(lead_agent.name, initial_statement)
            logging.info("Started new conversation")


class Debate(Conversation):
    def __init__(self, api_key, model, debate_text, agents, max_turns, log_dir, history_size):
        super().__init__(api_key, model, debate_text, agents, max_turns, log_dir, history_size)


class QAConversation(Conversation):
    def __init__(self, api_key, model, document, agents, max_turns, log_dir, history_size):
        super().__init__(api_key, model, document, agents, max_turns, log_dir, history_size)
        self.question_agent: Agent = next(agent for agent in agents if agent.role_type == "questioner")
        self.answer_agent: Agent = next(agent for agent in agents if agent.role_type == "answerer")

    def run_conversation(self):
        self._load_or_init_conversation()

        try:
            while self.current_turn < self.max_turns:
                question, q_metadata = self.generate_response(self.question_agent)
                self._log_response(self.question_agent.name, question, q_metadata)
                self.answer_agent.add_to_history(self.question_agent.name, question)
                self.question_agent.add_to_history(self.question_agent.name, question)

                answer, a_metadata = self.generate_response(self.answer_agent)
                self._log_response(self.answer_agent.name, answer, a_metadata)
                self.answer_agent.add_to_history(self.answer_agent.name, answer)
                self.question_agent.add_to_history(self.answer_agent.name, answer)

                self.current_turn += 1
                self._save_conversation_state()
                logging.info(f"Completed Q&A turn {self.current_turn}/{self.max_turns}")
        except Exception as e:
            logging.error(f"Error during Q&A conversation: {e}")
            raise
        finally:
            self._save_api_log()
