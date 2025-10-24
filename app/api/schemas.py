from datetime import datetime
from typing import List, Optional
from typing_extensions import Literal

from pydantic import BaseModel, Field


class KnowledgeNodeCreate(BaseModel):
    name: str = Field(..., description="Name of the concept or skill.")
    description: Optional[str] = Field(None, description="Short description of the concept.")
    tags: List[str] = Field(default_factory=list, description="List of labels associated with the concept.")


class KnowledgeNodeResponse(BaseModel):
    name: str
    description: str = ""
    tags: List[str] = Field(default_factory=list)


class KnowledgeNodeDetailResponse(KnowledgeNodeResponse):
    prerequisites: List[KnowledgeNodeResponse] = Field(
        default_factory=list,
        description="Other concepts that should be understood beforehand.",
    )


class RelationshipCreate(BaseModel):
    source: str = Field(..., description="Name of the prerequisite concept.")
    target: str = Field(..., description="Name of the concept that depends on the source.")


class RelationshipResponse(BaseModel):
    source: str
    target: str


class LearningPathResponse(BaseModel):
    path: List[KnowledgeNodeResponse]


class LearningSessionCreate(BaseModel):
    name: str = Field(..., description="Display name for the learning session.")
    description: Optional[str] = Field(
        None, description="Context or goals for this session."
    )
    focus_tags: List[str] = Field(
        default_factory=list,
        description="Tags that anchor this learning session.",
    )
    linked_concepts: List[str] = Field(
        default_factory=list,
        description="Concepts explicitly included in the session."
    )


class LearningSessionUpdate(BaseModel):
    status: Optional[str] = Field(
        None, description="Update the lifecycle stage (active, paused, archived)."
    )
    current_focus: Optional[str] = Field(
        None, description="Optional note for what to tackle next."
    )


class LearningSessionResponse(BaseModel):
    id: str
    name: str
    description: str
    focus_tags: List[str]
    linked_concepts: List[str]
    status: str
    current_focus: Optional[str] = None
    created_at: datetime


class CurriculumUpload(BaseModel):
    title: str = Field(..., description="Curriculum or syllabus title.")
    description: Optional[str] = Field(
        None, description="Brief overview of what this curriculum covers."
    )
    tags: List[str] = Field(
        default_factory=list, description="Tags that describe this curriculum."
    )
    source_url: Optional[str] = Field(
        None, description="Optional URL pointing to the canonical source."
    )
    linked_concepts: List[str] = Field(
        default_factory=list,
        description="Concepts this curriculum aligns with."
    )


class CurriculumResponse(BaseModel):
    id: str
    title: str
    description: str
    tags: List[str]
    source_url: Optional[str] = None
    linked_concepts: List[str]
    uploaded_at: datetime


class QuizQuestionResponse(BaseModel):
    id: str
    concept: str
    prompt: str
    choices: List[str]


class QuizGenerationRequest(BaseModel):
    concept: str = Field(..., description="Concept to review.")
    count: int = Field(
        default=3, ge=1, le=10, description="How many quiz items to generate."
    )


class QuizGenerationResponse(BaseModel):
    questions: List[QuizQuestionResponse]


class QuizAttemptRequest(BaseModel):
    question_id: str = Field(..., description="Identifier of the quiz question.")
    selected_index: int = Field(
        ..., ge=0, description="Index of the selected answer choice."
    )


class QuizAttemptResponse(BaseModel):
    correct: bool
    concept: str
    prompt: str
    correct_answer: str
    explanation: Optional[str] = None


class IdeaShareCreate(BaseModel):
    author: str = Field(..., description="Handle or name of the sharer.")
    title: str = Field(..., description="Short headline describing the idea.")
    summary: str = Field(..., description="Narrative summary for collaborators.")
    tags: List[str] = Field(
        default_factory=list,
        description="Keywords that describe this share for matching.",
    )
    linked_concepts: List[str] = Field(
        default_factory=list,
        description="Existing concepts that relate to this share.",
    )
    visibility: Literal["public", "connections", "private"] = Field(
        default="public",
        description="Controls how broadly the share is visible.",
    )
    authorized_handles: List[str] = Field(
        default_factory=list,
        description="Specific handles that can view a connections-only share.",
    )


class IdeaShareResponse(BaseModel):
    id: str
    author: str
    title: str
    summary: str
    tags: List[str]
    linked_concepts: List[str]
    visibility: str
    authorized_handles: List[str]
    created_at: datetime


class IdeaShareAuthorize(BaseModel):
    handles: List[str] = Field(
        default_factory=list,
        description="Handles that should gain access to this share.",
    )


class IdeaMatchResponse(BaseModel):
    share: IdeaShareResponse
    affinity: float
    shared_tags: List[str]
    complementary_tags: List[str]


class HandleComparisonResponse(BaseModel):
    handle_a: str
    handle_b: str
    shared_tags: List[str]
    divergent_tags: List[str]
