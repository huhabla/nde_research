#!/usr/bin/env bash
# Make sure you are located in the root directory of this project
mkdir -p playground
# Run the agent_debater from the root directory of this project
python scripts/agent_debater.py --text_list nde_reports/nde_discuss_list.txt \
    --text_dir nde_reports --log_dir playground --output_dir playground \
    --agent_descriptions agent_data/agent_descriptions.yaml --max_turns 3 \
    --mode debate
