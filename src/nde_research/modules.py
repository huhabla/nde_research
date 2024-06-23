from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union


class NdeReport(BaseModel):
    """This class represents the NdeReport model that contains all important aspects of an NDE report
    that were investigated by a potent LLM like sonnet from Anthropic. It contains all fields
    that must be filled by the LLM when reading a single report"""

    summary: str = Field(default="", description="The summary of the NDE report, that contains all important "
                                                 "events of the NDE")
    conversations: str = Field(default="",
                               description="NDE's often contain conversations with spiritual entities, that"
                                           "may be dead relatives, angels, higher beings, Jesus, Mohammed "
                                           "and so on. This field should contain all important conversations "
                                           "between the NDE experiencer and the spiritual entity/entities.")
    spirit_leaders: List[str] = Field(default=[],
                                      description="The list of the names of spiritual leaders that"
                                                  "were met in the NDE by the experiencer. The names"
                                                  "should only be set, if the experience was sure "
                                                  "who he met. Spiritual entities can be positive or negative"
                                                  "and defined as important entities"
                                                  "in different religions and spiritual teachings (positive or negative), "
                                                  "for example Jesus, Mohammed, Buddha, Seth, Lucifer, Satan, Lilith"
                                                  "and so on. ")
    state_of_consciousness: str = Field(default="unknown",
                                        description="The state of consciousness the the experiencer "
                                                    "experienced while the NDE. This can be normal, "
                                                    "higher, lower or unknown")
    reinkarnation: str = Field(default="",
                               description="This field should contain information if reinkarnation was "
                                           "mentioned in the NDE and can be confirmed based on the NDE. "
                                           "Hence, if the experiencer had life reviews of previous lives "
                                           "or this topic was discussed by spiritual entities. ")
    experience_type: str = Field(default="unknown",
                                 description="The type of experience the NDE was: positive, "
                                             "negative, neutral, unknown")
    assessment: str = Field(default="",
                            description="The assessment of the NDE experience written by the LLM pointing "
                                        "out the important steps of the NDE. If there were a tunnel, other "
                                        "beings, higher realms, higher consciousness")
    experienced_good: bool = Field(default=False, description="Set True if the experiencer met God in the NDE")
    experienced_jesus: bool = Field(default=False,
                                    description="Set True if the experiencer met Jesus Christ in the NDE")

