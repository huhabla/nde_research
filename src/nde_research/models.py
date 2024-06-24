from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union


class NdeJesusChristReport(BaseModel):
    summary: str = Field(default="", description="A short single line summary of the NDE report, that contains all important events of the NDE. ")
    assessment: str = Field(default="", description="The assessment of the NDE experience as a single line LLM pointing out all important steps of the NDE.")
    state_of_consciousness: str = Field(default="unknown", description="The state of consciousness the the experiencer experienced while the NDE. This can be normal, higher, lower or unknown")
    experience_type: str = Field(default="unknown", description="The type of experience the NDE was: positive, negative, neutral, unknown")
    past_life_memories: bool = Field(default=False, description="Based on your reasoning set true if past life memories are evidently present in this NDE")
    life_review: bool = Field(default=False, description="Based on your reasoning set true if a life review was evidently present in this NDE")
    jesus_christ: bool = Field(default=False, description="Based on your reasoning set true if the presence of Jesus Christ is evident in the NDE")
    buddha: bool = Field(default=False, description="Based on your reasoning set true if the presence of Buddha is evident in the NDE")
    mohammed: bool = Field(default=False, description="Based on your reasoning set true if the presence of prophet Mohammed is evident in the NDE")
    profound_experience: bool = Field(default=False, description="Based on your reasoning set true if the experiencer had a profound spiritual experience")
    return_to_body: str = Field(default="unknown", description="How the experiencer returned to his body: unknown, voluntary or involuntary")
    religion: str = Field(default="unknown", description="The religion of the person before the NDE if known, otherwise unknown")
    gender: str = Field(default="unknown", description="The gender of the person that experienced the NDE: male, female, unknown")
    date: str = Field(default="unknown", description="The date of the NDE if known")
