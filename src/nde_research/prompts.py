
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2024, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@holistech.de"


SYSTEM_PROMPT = """
You are a highly skilled Near Death Experience (NDE) researcher with vast knowledge of NDE reports. You will analyse 
new reports and put them intelligently in a Markdown text with an embedded JSON structure for further research.

"""

USER_PROMPT = """
Your task is to fully read and understand the provided near-death experience (NDE) report and carefully extract 
specific information. The report may include question after the NDE report that the experiencer directly answered. 
Include these answers carefully in your information extraction.
 
Here is the NDE report you will be analyzing:

<nde_report>
{nde_report}
</nde_report>

Follow these instructions to extract and format the information:

1. Read the entire NDE report carefully, including any question/answer sections if present.

- Markdown format: Write your response in Markdown format, start with the title "NDE Analysis"

- Summary: Provide a detailed and well written summary of all important events in the NDE.
  
- Assessment: Provide your analysis of the NDE, highlighting important aspects. Mention out all important steps 
  of the NDE. The assessment must include potential past life memories, life reviews, higher knowledge 
  and encounter with Jesus Christ, Buddha, Mohammed or other entities if present.

- Past life memories reasoning: Explain your reasoning mindfully and step by step why this NDE has evidence of past 
  life memories or why it has not. Past life memories or reincarnation must be explicitely mentioned or  discussed 
  in the NDE. The opinion or guessing of the experiencer is no evidence. This reasoning is the base for your decision 
  to set the field past_life_memories to true or false in the JSON output.

- Life review reasoning: Explain your reasoning mindfully and step by step if a life review
  has happened in this NDE report. This reasoning is the base for your decision 
  to set the field life_review to true or false in the JSON output.
  
- Higher knowledge reasoning: Explain your reasoning mindfully and step by step if higher
  knowledge was received by the NDE experiencer. 
  If higher knowledge was received, create a curated bullet point list of the knowledge that was received.
  This reasoning is the base for your decision to set the field higher_knowledge to true or false in the JSON output.

- Future event reasoning: Explain your reasoning mindfully and step by step if future world changing events
  are mentioned or discussed in the NDE. If future world changing events were mentioned, then create
  a curated bullet point list of all future events that were mentioned. Future events of personal changes of the
  experiencer should only be included in the list, if they give hints about world changing 
  events like wars, catastrophes, new consciousness, peace on earth and so on.
  This reasoning is the base for your decision to set the field future_events to true or false in the JSON output.

- Jesus Christ reasoning: Explain your reasoning mindfully and step by step why this NDE has evidence of presence 
  of Jesus Christ (Jesus) or why it has not. The presence of Jesus Christ is not evident if the experiencer is 
  just guessing that he has met Jesus Christ. This reasoning is the base for your decision to set the field 
  jesus_christ to true or false in the JSON output.
  
- Buddha reasoning: Explain your reasoning mindfully and step by step why this NDE has evidence of presence 
  of Buddha or why it has not. The presence of  Buddha the founder of Buddhism is not evident if the experiencer is 
  just guessing that he has met Buddha. This reasoning is the base for your decision to set the field 
  buddha to true or false in the JSON output.
  
- Mohammed reasoning: Explain your reasoning mindfully and step by step why this NDE has evidence of presence 
  of prophet Mohammed or why it has not. The presence of prophet Mohammed is not evident if the experiencer is 
  just guessing that he has met Mohammed. This reasoning is the base for your decision to set the field 
  muhammed to true or false in the JSON output.
  
- Profound experience reasoning: Explain your reasoning mindfully and step by step why this NDE has significantly 
  changed the life of the experiencer or why it has not. This reasoning  is the base for your decision to set the 
  field profound_experience to true or false in the JSON output.

2. Extract relevant details to fill a structured JSON output. 

You must extract information from this report and your response and format it into a JSON structure that matches 
the following Pydantic BaseModel:

```python
{base_model}
```

3. For each field in the NdeReport model:
   a. Extract relevant information from the report, your summary, assessment and reasoning.
   b. Ensure the extracted information matches the field's description and type.
   c. If information is uncertain or missing, use appropriate default values or indicate uncertainty.

4. Pay special attention to the following fields:
   - summary: Write your summary in that field as valid JSON string, without newlines
   - state_of_consciousness: Determine if it was normal, higher, lower, or unknown.
   - experience_type: Classify as positive, negative, neutral, or unknown.
   - assessment: Write your assessment  as valid JSON string, without newlines
   - past_life_memories: Based on your reasoning set true if past life memories are evidently present in this NDE
   - life_review: Based on your reasoning set true if a life review was evidently present in this NDE
   - higher_knowledge: Based on your reasoning set true if higher knowledge was received by the NDE experiencer
   - future_events: Based on your reasoning set true if future world changing events are mentioned in the NDE
   - jesus_christ: Based on your reasoning set true if the presence of Jesus Christ is evident in the NDE
   - buddha: Based on your reasoning set true if the presence of Buddha is evident in the NDE
   - mohammed: Based on your reasoning set true if the presence of prophet Mohammed is evident in the NDE
   - profound_experience: Based on your reasoning set true if the experiencer had a profound spiritual experience
   - return_to_body: How the experiencer returned to his body: unknown, voluntary or involuntary

5. If certain information is not present in the report, use these guidelines:
   - For string fields, use an empty string "" or "unknown" as appropriate.
   - For boolean fields, use False if not explicitly mentioned.

6. Format your response as Markdown text that includes as final output a valid JSON object within <json_output> tags, 
   ensuring all field names match the Pydantic model exactly. 
7. Present your final JSON output within <json_output> tags. Ensure the JSON is properly formatted and valid.
"""
