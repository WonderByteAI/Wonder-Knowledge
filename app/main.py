from pathlib import Path

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from app.api.schemas import (
    CurriculumResponse,
    CurriculumUpload,
    HandleComparisonResponse,
    IdeaMatchResponse,
    IdeaShareAuthorize,
    IdeaShareCreate,
    IdeaShareResponse,
    KnowledgeNodeCreate,
    KnowledgeNodeDetailResponse,
    KnowledgeNodeResponse,
    LearningPathResponse,
    LearningSessionCreate,
    LearningSessionResponse,
    LearningSessionUpdate,
    QuizAttemptRequest,
    QuizAttemptResponse,
    QuizGenerationRequest,
    QuizGenerationResponse,
    QuizQuestionResponse,
    RelationshipCreate,
    RelationshipResponse,
)
from app.core.graph import KnowledgeGraph, KnowledgeNode

app = FastAPI(title="Wonder Knowledge", description="Prototype knowledge mapping assistant")

graph = KnowledgeGraph()
FRONTEND_INDEX = Path(__file__).resolve().parent / "frontend" / "index.html"


def seed_graph() -> None:
    """Populate the in-memory graph with a few starter concepts."""

    initial_nodes = [
        KnowledgeNode(
            name="Programming Fundamentals",
            description="Core ideas such as variables, loops, and functions.",
            tags=["programming", "basics"],
        ),
        KnowledgeNode(
            name="Python",
            description="General purpose programming language focusing on readability.",
            tags=["python", "programming"],
        ),
        KnowledgeNode(
            name="FastAPI",
            description="Modern Python web framework for building APIs.",
            tags=["python", "web"],
        ),
        KnowledgeNode(
            name="REST APIs",
            description="Architectural style for building web services.",
            tags=["web", "api"],
        ),
    ]

    for node in initial_nodes:
        graph.add_node(node)

    relationships = [
        ("Programming Fundamentals", "Python"),
        ("Python", "FastAPI"),
        ("Programming Fundamentals", "REST APIs"),
        ("REST APIs", "FastAPI"),
    ]

    for source, target in relationships:
        try:
            graph.add_relationship(source, target)
        except ValueError:
            # The nodes should exist, but guard against a partially-seeded graph.
            continue

    # Seed a sample session and curriculum to show the new surfaces in the UI.
    try:
        graph.create_session(
            name="Full-stack Python sprint",
            description="Blend Python fundamentals with modern API practices.",
            focus_tags=["python", "web", "api"],
            linked_concepts=["Programming Fundamentals", "Python", "FastAPI"],
        )
    except ValueError:
        pass

    try:
        graph.create_curriculum(
            title="Intro to FastAPI Workshop",
            description="Curated workshop outline covering routing, dependency injection, and deployment tips.",
            tags=["fastapi", "web", "backend"],
            source_url="https://fastapi.tiangolo.com/",
            linked_concepts=["FastAPI", "REST APIs"],
        )
    except ValueError:
        pass

    try:
        graph.publish_share(
            author="wonder-team",
            title="API-first brainstorming",
            summary="Mapping how we co-create learning journeys and surface helpful context for collaborators.",
            tags=["collaboration", "brainstorm", "learning"],
            linked_concepts=["REST APIs", "FastAPI"],
            visibility="public",
        )
    except ValueError:
        pass


seed_graph()


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def home() -> HTMLResponse:
    """Serve the interactive explorer UI."""

    if not FRONTEND_INDEX.exists():
        raise HTTPException(status_code=500, detail="Frontend build missing")
    return HTMLResponse(FRONTEND_INDEX.read_text(encoding="utf-8"))


@app.get("/.well-known/mcp/manifest.json", include_in_schema=False, response_class=JSONResponse)
async def mcp_manifest() -> JSONResponse:
    """Expose a lightweight MCP manifest so AI clients can discover actions."""

    manifest = {
        "name": "wonder-knowledge",
        "description": "Knowledge map assistant with sessions, quizzes, and collaborative shares.",
        "version": "0.2.0",
        "actions": [
            {
                "name": "create_concept",
                "description": "Add a concept to the shared knowledge graph.",
                "args": {
                    "name": "str",
                    "description": "str",
                    "tags": "List[str]",
                },
                "method": "POST",
                "path": "/knowledge",
            },
            {
                "name": "publish_share",
                "description": "Publish a new collaborative knowledge share.",
                "args": {
                    "author": "str",
                    "title": "str",
                    "summary": "str",
                    "tags": "List[str]",
                    "visibility": "public|connections|private",
                },
                "method": "POST",
                "path": "/shares",
            },
            {
                "name": "suggest_matches",
                "description": "Retrieve affinity-ranked collaborator ideas for a handle.",
                "args": {
                    "viewer": "str",
                    "limit": "int",
                },
                "method": "GET",
                "path": "/shares/matchups",
            },
        ],
    }
    return JSONResponse(content=manifest)


def _share_to_response(share) -> IdeaShareResponse:
    return IdeaShareResponse(
        id=share.id,
        author=share.author,
        title=share.title,
        summary=share.summary,
        tags=list(share.tags),
        linked_concepts=list(share.linked_concepts),
        visibility=share.visibility,
        authorized_handles=list(share.authorized_handles),
        created_at=share.created_at,
    )


@app.post("/knowledge", response_model=KnowledgeNodeResponse, summary="Create or update a knowledge node")
async def create_knowledge_node(payload: KnowledgeNodeCreate) -> KnowledgeNodeResponse:
    node = KnowledgeNode(
        name=payload.name.strip(),
        description=(payload.description or "").strip(),
        tags=sorted(set(tag.strip().lower() for tag in payload.tags if tag.strip())),
    )
    if not node.name:
        raise HTTPException(status_code=422, detail="Name cannot be empty")
    graph.add_node(node)
    stored = graph.get_node(node.name)
    if stored is None:
        raise HTTPException(status_code=500, detail="Failed to persist node")
    return KnowledgeNodeResponse(**stored.__dict__)


@app.get("/knowledge", response_model=list[KnowledgeNodeResponse], summary="List all knowledge nodes")
async def list_knowledge_nodes() -> list[KnowledgeNodeResponse]:
    nodes = graph.list_nodes()
    return [KnowledgeNodeResponse(**node.__dict__) for node in nodes]


@app.get(
    "/knowledge/{name}",
    response_model=KnowledgeNodeDetailResponse,
    summary="Retrieve a single knowledge node with prerequisites",
)
async def get_knowledge_node(name: str) -> KnowledgeNodeDetailResponse:
    node = graph.get_node(name)
    if node is None:
        raise HTTPException(status_code=404, detail=f"Unknown concept: {name}")
    prerequisites = graph.prerequisites(name)
    return KnowledgeNodeDetailResponse(
        **node.__dict__,
        prerequisites=[KnowledgeNodeResponse(**item.__dict__) for item in prerequisites],
    )


@app.delete(
    "/knowledge/{name}",
    status_code=204,
    summary="Remove a concept and all of its relationships",
)
async def delete_knowledge_node(name: str) -> None:
    try:
        graph.remove_node(name)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post(
    "/relationships",
    status_code=201,
    summary="Connect two nodes to express that one concept depends on another",
)
async def create_relationship(payload: RelationshipCreate) -> None:
    try:
        graph.add_relationship(payload.source, payload.target)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get(
    "/relationships",
    response_model=list[RelationshipResponse],
    summary="List all defined concept dependencies",
)
async def list_relationships() -> list[RelationshipResponse]:
    relationships = graph.list_relationships()
    return [
        RelationshipResponse(source=source.name, target=target.name)
        for source, target in relationships
    ]


@app.delete(
    "/relationships",
    status_code=204,
    summary="Remove a dependency between two concepts",
)
async def delete_relationship(payload: RelationshipCreate) -> None:
    try:
        graph.remove_relationship(payload.source, payload.target)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get(
    "/learning-path",
    response_model=LearningPathResponse,
    summary="Compute the optimal learning path between two concepts",
)
async def get_learning_path(start: str, goal: str) -> LearningPathResponse:
    try:
        path = graph.shortest_path(start, goal)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return LearningPathResponse(path=[KnowledgeNodeResponse(**node.__dict__) for node in path])


@app.post("/sessions", response_model=LearningSessionResponse, summary="Create a new learning session")
async def create_session(payload: LearningSessionCreate) -> LearningSessionResponse:
    try:
        session = graph.create_session(
            name=payload.name,
            description=payload.description or "",
            focus_tags=payload.focus_tags,
            linked_concepts=payload.linked_concepts,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return LearningSessionResponse(**session.__dict__)


@app.get("/sessions", response_model=list[LearningSessionResponse], summary="List all learning sessions")
async def list_sessions() -> list[LearningSessionResponse]:
    sessions = graph.list_sessions()
    return [LearningSessionResponse(**session.__dict__) for session in sessions]


@app.patch(
    "/sessions/{session_id}",
    response_model=LearningSessionResponse,
    summary="Update session status or focus",
)
async def update_session(session_id: str, payload: LearningSessionUpdate) -> LearningSessionResponse:
    try:
        session = graph.update_session(
            session_id,
            status=payload.status,
            current_focus=payload.current_focus,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return LearningSessionResponse(**session.__dict__)


@app.post(
    "/curricula",
    response_model=CurriculumResponse,
    summary="Upload a curriculum outline to align with the knowledge graph",
)
async def upload_curriculum(payload: CurriculumUpload) -> CurriculumResponse:
    try:
        curriculum = graph.create_curriculum(
            title=payload.title,
            description=payload.description or "",
            tags=payload.tags,
            source_url=payload.source_url,
            linked_concepts=payload.linked_concepts,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return CurriculumResponse(**curriculum.__dict__)


@app.get("/curricula", response_model=list[CurriculumResponse], summary="List uploaded curricula")
async def list_curricula() -> list[CurriculumResponse]:
    curricula = graph.list_curricula()
    return [CurriculumResponse(**item.__dict__) for item in curricula]


@app.post(
    "/quizzes/generate",
    response_model=QuizGenerationResponse,
    summary="Generate quick quiz questions for a concept",
)
async def generate_quiz(payload: QuizGenerationRequest) -> QuizGenerationResponse:
    try:
        questions = graph.generate_quiz(payload.concept, payload.count)
    except ValueError as error:
        detail = str(error)
        status = 404 if "Unknown concept" in detail else 422
        raise HTTPException(status_code=status, detail=detail) from error
    return QuizGenerationResponse(
        questions=[QuizQuestionResponse(id=item.id, concept=item.concept, prompt=item.prompt, choices=item.choices) for item in questions]
    )


@app.post(
    "/quizzes/attempt",
    response_model=QuizAttemptResponse,
    summary="Check an answer for a generated quiz question",
)
async def attempt_quiz(payload: QuizAttemptRequest) -> QuizAttemptResponse:
    try:
        correct, question = graph.grade_quiz(payload.question_id, payload.selected_index)
    except ValueError as error:
        detail = str(error)
        status = 404 if "Unknown quiz question" in detail else 422
        raise HTTPException(status_code=status, detail=detail) from error
    explanation = (
        "Great job! Keep exploring related concepts to reinforce the link."
        if correct
        else "Review the concept description and prerequisites, then try again."
    )
    return QuizAttemptResponse(
        correct=correct,
        concept=question.concept,
        prompt=question.prompt,
        correct_answer=question.choices[question.correct_index],
        explanation=explanation,
    )


@app.post(
    "/shares",
    response_model=IdeaShareResponse,
    summary="Publish a knowledge share for collaborators",
)
async def publish_share(payload: IdeaShareCreate) -> IdeaShareResponse:
    try:
        share = graph.publish_share(
            author=payload.author,
            title=payload.title,
            summary=payload.summary,
            tags=payload.tags,
            linked_concepts=payload.linked_concepts,
            visibility=payload.visibility,
            authorized_handles=payload.authorized_handles,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return _share_to_response(share)


@app.get(
    "/shares",
    response_model=list[IdeaShareResponse],
    summary="List knowledge shares visible to the viewer",
)
async def list_shares(viewer: Optional[str] = None) -> list[IdeaShareResponse]:
    shares = graph.list_shares(viewer=viewer)
    return [_share_to_response(item) for item in shares]


@app.post(
    "/shares/{share_id}/authorize",
    response_model=IdeaShareResponse,
    summary="Add collaborators to an existing share",
)
async def authorize_share(share_id: str, payload: IdeaShareAuthorize) -> IdeaShareResponse:
    try:
        share = graph.authorize_share(share_id, payload.handles)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return _share_to_response(share)


@app.get(
    "/shares/matchups",
    response_model=list[IdeaMatchResponse],
    summary="Recommend relevant collaborator shares",
)
async def share_matchups(viewer: str, limit: int = 5) -> list[IdeaMatchResponse]:
    try:
        matches = graph.affinity_for_viewer(viewer, limit=limit)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    responses: list[IdeaMatchResponse] = []
    for match in matches:
        responses.append(
            IdeaMatchResponse(
                share=_share_to_response(match.share),
                affinity=match.affinity,
                shared_tags=match.shared_tags,
                complementary_tags=match.complementary_tags,
            )
        )
    return responses


@app.get(
    "/shares/compare",
    response_model=HandleComparisonResponse,
    summary="Compare overlaps between two handles",
)
async def compare_handles(handle_a: str, handle_b: str) -> HandleComparisonResponse:
    shared, divergent = graph.compare_handles(handle_a, handle_b)
    return HandleComparisonResponse(
        handle_a=handle_a,
        handle_b=handle_b,
        shared_tags=shared,
        divergent_tags=divergent,
    )
