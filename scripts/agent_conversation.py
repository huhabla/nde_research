import argparse
import logging
import os
import random
from nde_research.agents import load_agent_descriptions, Agent
from nde_research.conversation import Debate, QAConversation
import os


def create_directory(directory_name):
    # Get the current working directory
    current_path = os.getcwd()

    # Construct the full path of the new directory
    new_directory_path = os.path.join(current_path, directory_name)

    # Check if the directory already exists
    if not os.path.exists(new_directory_path):
        # Create the directory
        os.makedirs(new_directory_path)
        logging.info(f"Directory '{directory_name}' created at {new_directory_path}")
    else:
        logging.info(f"Directory '{directory_name}' already exists at {new_directory_path}")


def main():
    """
    python scripts/agent_conversation.py --mode debate \
           --document ./nde_reports/1_ahly_s_nde.txt \
           --output_dir output --agents agent_data/agent_descriptions.yaml \
           --llm openai --max_turns 10 --history_size 40


    :return:
    """
    parser = argparse.ArgumentParser(description="Run Debate or Q&A Conversation")
    parser.add_argument("--mode", choices=["debate", "qa"], required=True, help="Mode of operation: debate or qa")
    parser.add_argument("--document", required=True,
                        help="The path to the document that should be the base for the diskussion or QA generation")
    parser.add_argument("--output_dir", default="conversations",
                        help="Directory for storing output files (logging and conversaion)")
    parser.add_argument("--agents", required=True, help="Path to YAML file containing agent descriptions")
    parser.add_argument("--max_turns", type=int, default=10, help="Maximum number of turns in the conversation")
    parser.add_argument("--history_size", type=int, default=10,
                        help="Number of recent messages to include in conversation history")
    parser.add_argument("--llm", type=str, default="anthropic", choices=["anthropic", "openai"],
                        help="The LLM that should be used for the conversation")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if args.llm == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logging.error("ANTHROPIC_API_KEY not found")
            raise ValueError("ANTHROPIC_API_KEY not found")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OPENAI_API_KEY not found")
            raise ValueError("OPENAI_API_KEY not found")

    create_directory(args.output_dir)

    with open(args.document, "r", encoding="utf-8") as f:
        document = f.read()

    agent_descriptions = load_agent_descriptions(args.agents)

    if args.mode == "debate":
        agents = [Agent(desc) for desc in agent_descriptions if desc.role_type in ["expert", "moderator"]]
        conversation = Debate(api_key, args.llm, document, agents, args.max_turns, args.output_dir, args.history_size)
    else:  # qa mode
        questioner = Agent(next(desc for desc in agent_descriptions if desc.role_type == "questioner"))
        answerer = Agent(next(desc for desc in agent_descriptions if desc.role_type == "answerer"))
        agents = [questioner, answerer]
        conversation = QAConversation(api_key, args.llm, document, agents, args.max_turns, args.output_dir,
                                      args.history_size)

    conversation.run_conversation()

    logging.info("Conversation has been completed and saved.")


if __name__ == "__main__":
    main()
