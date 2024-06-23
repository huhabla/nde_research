import anthropic
import os
import json
import logging
from nde_research.modules import NdeReport
from nde_research.prompts import SYSTEM_PROMPT, USER_PROMPT

logger = logging.getLogger(__name__)


def process_nde_report(file_path: str, client: anthropic.Anthropic, output_dir: str) -> None:
    # Read the NDE report
    with open(file_path, 'r', encoding='utf-8') as file:
        nde_report = file.read()

    # Prepare the prompts
    system_prompt = SYSTEM_PROMPT
    user_prompt = USER_PROMPT.format(nde_report=nde_report, base_model=NdeReport.schema_json(indent=2))
    prompt = f"{SYSTEM_PROMPT}\n{user_prompt}"

    # Make the API call
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract JSON from the response
    response_content = message.content[0].text
    json_start = response_content.find('<json_output>') + len('<json_output>')
    json_end = response_content.find('</json_output>')
    json_str = response_content[json_start:json_end].strip()

    # Parse and validate JSON using Pydantic
    try:
        nde_report_obj = NdeReport.parse_raw(json_str)
    except Exception as e:
        logger.error(f"Error parsing JSON for {file_path}: {str(e)}")
        return

    # Write the JSON output
    output_file = os.path.splitext(os.path.basename(file_path))[0] + '.json'
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nde_report_obj.dict(), f, indent=2)

    logger.info(f"Processed and saved: {output_path}")


def get_files_to_process(input_file: str, input_dir: str) -> list:
    with open(input_file, 'r') as f:
        nde_report_files = f.read().splitlines()

    return [
        file for file in nde_report_files
        if file.endswith('.md') and not os.path.exists(os.path.join(input_dir, os.path.splitext(file)[0] + '.json'))
    ]
