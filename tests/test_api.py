from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_homepage_served() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Wonder Knowledge Studio" in response.text
    assert "<html" in response.text.lower()


def test_seeded_knowledge_available() -> None:
    response = client.get("/knowledge")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert "Programming Fundamentals" in names
    assert "FastAPI" in names


def test_add_relationship_and_learning_path() -> None:
    payload = {"source": "Programming Fundamentals", "target": "Python"}
    response = client.post("/relationships", json=payload)
    assert response.status_code == 201
    client.post("/knowledge", json={"name": "AsyncIO", "description": "Python async"})
    client.post("/relationships", json={"source": "Python", "target": "AsyncIO"})
    path_response = client.get("/learning-path", params={"start": "Programming Fundamentals", "goal": "AsyncIO"})
    assert path_response.status_code == 200
    path = [node["name"] for node in path_response.json()["path"]]
    assert path[0] == "Programming Fundamentals"
    assert path[-1] == "AsyncIO"


def test_session_management() -> None:
    payload = {
        "name": "API Sprint",
        "description": "Target FastAPI skills",
        "focus_tags": ["python", "api"],
        "linked_concepts": ["Python", "FastAPI"],
    }
    response = client.post("/sessions", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "API Sprint"
    list_response = client.get("/sessions")
    assert list_response.status_code == 200
    names = {item["name"] for item in list_response.json()}
    assert "API Sprint" in names


def test_curriculum_upload() -> None:
    payload = {
        "title": "FastAPI Crash Course",
        "description": "Session outline",
        "tags": ["fastapi", "backend"],
        "source_url": "https://fastapi.tiangolo.com/",
        "linked_concepts": ["FastAPI"],
    }
    response = client.post("/curricula", json=payload)
    assert response.status_code == 200
    library = client.get("/curricula")
    assert library.status_code == 200
    titles = {item["title"] for item in library.json()}
    assert "FastAPI Crash Course" in titles


def test_quiz_generation_and_attempt() -> None:
    response = client.post("/quizzes/generate", json={"concept": "Python", "count": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["questions"]
    question = data["questions"][0]
    attempt = client.post(
        "/quizzes/attempt",
        json={"question_id": question["id"], "selected_index": 0},
    )
    assert attempt.status_code == 200
    result = attempt.json()
    assert "correct" in result


def test_share_publication_and_listing() -> None:
    payload = {
        "author": "test-handle",
        "title": "Async brainstorming",
        "summary": "Exploring async features in Python.",
        "tags": ["python", "async"],
        "linked_concepts": ["Python"],
        "visibility": "connections",
        "authorized_handles": ["ally"],
    }
    response = client.post("/shares", json=payload)
    assert response.status_code == 200
    created = response.json()
    assert created["title"] == "Async brainstorming"
    # Viewer without handle should not see connections-only share.
    public_feed = client.get("/shares")
    assert all(item["id"] != created["id"] for item in public_feed.json())
    ally_feed = client.get("/shares", params={"viewer": "ally"})
    ids = {item["id"] for item in ally_feed.json()}
    assert created["id"] in ids
    # Grant additional access and ensure viewer can see it.
    grant = client.post(f"/shares/{created['id']}/authorize", json={"handles": ["buddy"]})
    assert grant.status_code == 200
    buddy_feed = client.get("/shares", params={"viewer": "buddy"})
    ids = {item["id"] for item in buddy_feed.json()}
    assert created["id"] in ids


def test_share_matchups_and_manifest() -> None:
    response = client.get("/shares/matchups", params={"viewer": "ally", "limit": 3})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    manifest = client.get("/.well-known/mcp/manifest.json")
    assert manifest.status_code == 200
    data = manifest.json()
    assert data["name"] == "wonder-knowledge"
    assert any(action["name"] == "publish_share" for action in data["actions"])
