import pytest

from app.core.graph import KnowledgeGraph, KnowledgeNode


@pytest.fixture()
def graph() -> KnowledgeGraph:
    instance = KnowledgeGraph()
    instance.add_node(KnowledgeNode(name="A", description="Alpha foundations", tags=["foundational"]))
    instance.add_node(KnowledgeNode(name="B", description="Beta concept", tags=["intermediate"]))
    instance.add_node(KnowledgeNode(name="C", description="Gamma advanced", tags=["advanced"]))
    instance.add_relationship("A", "B")
    instance.add_relationship("B", "C")
    return instance


def test_shortest_path(graph: KnowledgeGraph) -> None:
    path = graph.shortest_path("A", "C")
    assert [node.name for node in path] == ["A", "B", "C"]


def test_prerequisites(graph: KnowledgeGraph) -> None:
    prereqs = graph.prerequisites("C")
    assert {node.name for node in prereqs} == {"A", "B"}


def test_remove_relationship(graph: KnowledgeGraph) -> None:
    graph.remove_relationship("B", "C")
    with pytest.raises(ValueError):
        graph.shortest_path("A", "C")


def test_remove_node(graph: KnowledgeGraph) -> None:
    graph.remove_node("B")
    assert graph.get_node("B") is None
    with pytest.raises(ValueError):
        graph.add_relationship("B", "C")


def test_create_session(graph: KnowledgeGraph) -> None:
    session = graph.create_session(
        name="Deep dive",
        description="Focus on intermediate skills",
        focus_tags=["intermediate", "practice"],
        linked_concepts=["A", "B"],
    )
    assert session.id
    assert session.linked_concepts == ["A", "B"]
    updated = graph.update_session(session.id, status="paused", current_focus="Review A")
    assert updated.status == "paused"
    assert updated.current_focus == "Review A"


def test_create_curriculum(graph: KnowledgeGraph) -> None:
    curriculum = graph.create_curriculum(
        title="Beta syllabus",
        description="Outline for beta concept",
        tags=["intermediate"],
        source_url="https://example.com",
        linked_concepts=["B"],
    )
    assert curriculum.linked_concepts == ["B"]
    assert curriculum.tags == ["intermediate"]


def test_generate_and_grade_quiz(graph: KnowledgeGraph) -> None:
    questions = graph.generate_quiz("B", count=2)
    assert questions
    first = questions[0]
    correct, _ = graph.grade_quiz(first.id, first.correct_index)
    assert correct is True
    with pytest.raises(ValueError):
        graph.grade_quiz(first.id, 99)


def test_share_publication_and_matching(graph: KnowledgeGraph) -> None:
    share = graph.publish_share(
        author="alpha",
        title="Exploring foundations",
        summary="Documenting core lessons",
        tags=["foundational", "practice"],
        linked_concepts=["A"],
        visibility="connections",
        authorized_handles=["beta"],
    )
    assert share.visibility == "connections"
    assert graph.list_shares(viewer="beta")
    graph.authorize_share(share.id, ["gamma"])
    assert graph.list_shares(viewer="gamma")
    matches = graph.affinity_for_viewer("beta", limit=3)
    assert matches and matches[0].affinity == 0.0
    graph.publish_share(
        author="delta",
        title="Advanced collab",
        summary="Working on advanced flows",
        tags=["advanced", "practice"],
        linked_concepts=["C"],
        visibility="public",
    )
    matches = graph.affinity_for_viewer("beta", limit=3)
    assert matches
    shared, divergent = graph.compare_handles("alpha", "delta")
    assert "practice" in shared or "practice" in divergent
