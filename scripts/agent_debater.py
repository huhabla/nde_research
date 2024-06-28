import argparse
import logging
import os
import random
from nde_research.agents import load_agent_descriptions, Agent
from nde_research.conversation import Debate, QAConversation


def load_debate_texts(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def main():
    parser = argparse.ArgumentParser(description="Run Debate or Q&A Conversation")
    parser.add_argument("--mode", choices=["debate", "qa"], required=True, help="Mode of operation: debate or qa")
    parser.add_argument("--text_list", required=True, help="Path to file containing debate text filenames")
    parser.add_argument("--text_dir", required=True, help="Directory containing debate texts")
    parser.add_argument("--log_dir", required=True, help="Directory for storing conversation logs")
    parser.add_argument("--output_dir", required=True, help="Directory for storing output files")
    parser.add_argument("--agent_descriptions", required=True, help="Path to YAML file containing agent descriptions")
    parser.add_argument("--max_turns", type=int, default=10, help="Maximum number of turns in the conversation")
    parser.add_argument("--history_size", type=int, default=10,
                        help="Number of recent messages to include in conversation history")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logging.error("ANTHROPIC_API_KEY not found")
        raise ValueError("ANTHROPIC_API_KEY not found")

    debate_texts = load_debate_texts(args.text_list)
    debate_text_filename = random.choice(debate_texts)
    with open(os.path.join(args.text_dir, debate_text_filename), "r", encoding="utf-8") as f:
        document = f.read()

    agent_descriptions = load_agent_descriptions(args.agent_descriptions)

    if args.mode == "debate":
        agents = [Agent(desc) for desc in agent_descriptions if desc.role_type in ["expert", "moderator"]]
        conversation = Debate(api_key, document, agents, args.max_turns, args.log_dir, args.history_size)
    else:  # qa mode
        questioner = Agent(next(desc for desc in agent_descriptions if desc.role_type == "questioner"))
        answerer = Agent(next(desc for desc in agent_descriptions if desc.role_type == "answerer"))
        agents = [questioner, answerer]
        conversation = QAConversation(api_key, document, agents, args.max_turns, args.log_dir, args.history_size)

    conversation.run_conversation()

    logging.info("Conversation has been completed and saved.")


if __name__ == "__main__":
    main()
