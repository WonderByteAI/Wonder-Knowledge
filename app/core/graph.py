from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import random
from typing import Dict, Iterable, List, Optional, Set, Tuple
from uuid import uuid4


@dataclass
class KnowledgeNode:
    """Represents a concept within the knowledge graph."""

    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class LearningSession:
    """Tracks a focussed learning journey over a subset of the graph."""

    id: str
    name: str
    description: str
    focus_tags: List[str]
    linked_concepts: List[str]
    status: str = "active"
    current_focus: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Curriculum:
    """Represents an uploaded curriculum or study outline."""

    id: str
    title: str
    description: str
    tags: List[str]
    source_url: Optional[str]
    linked_concepts: List[str]
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QuizQuestion:
    """Generated quiz item tied to a concept."""

    id: str
    concept: str
    prompt: str
    choices: List[str]
    correct_index: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class IdeaShare:
    """Captures a shareable snapshot of someone's knowledge focus."""

    id: str
    author: str
    title: str
    summary: str
    tags: List[str]
    linked_concepts: List[str]
    visibility: str = "public"
    authorized_handles: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class IdeaMatch:
    """Represents an affinity score between the viewer and a shared idea."""

    share: IdeaShare
    affinity: float
    shared_tags: List[str]
    complementary_tags: List[str]


class KnowledgeGraph:
    """In-memory representation of a directed knowledge graph."""

    def __init__(self) -> None:
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._edges: Dict[str, Set[str]] = {}
        self._reverse_edges: Dict[str, Set[str]] = {}
        self._sessions: Dict[str, LearningSession] = {}
        self._curricula: Dict[str, Curriculum] = {}
        self._quiz_bank: Dict[str, QuizQuestion] = {}
        self._shares: Dict[str, IdeaShare] = {}

    def add_node(self, node: KnowledgeNode) -> None:
        key = node.name.lower()
        if key not in self._nodes:
            self._nodes[key] = node
            self._edges.setdefault(key, set())
            self._reverse_edges.setdefault(key, set())
        else:
            # Merge metadata if the node already exists.
            existing = self._nodes[key]
            if node.description:
                existing.description = node.description
            if node.tags:
                existing.tags = sorted(set(existing.tags).union(node.tags))

    def add_relationship(self, source: str, target: str) -> None:
        source_key, target_key = source.lower(), target.lower()
        if source_key not in self._nodes:
            raise ValueError(f"Unknown source node: {source}")
        if target_key not in self._nodes:
            raise ValueError(f"Unknown target node: {target}")
        self._edges.setdefault(source_key, set()).add(target_key)
        self._reverse_edges.setdefault(target_key, set()).add(source_key)

    def get_node(self, name: str) -> Optional[KnowledgeNode]:
        return self._nodes.get(name.lower())

    def list_nodes(self) -> List[KnowledgeNode]:
        return sorted(self._nodes.values(), key=lambda node: node.name.lower())

    def list_relationships(self) -> List[Tuple[KnowledgeNode, KnowledgeNode]]:
        pairs: List[Tuple[KnowledgeNode, KnowledgeNode]] = []
        for source_key, targets in self._edges.items():
            for target_key in targets:
                source_node = self._nodes[source_key]
                target_node = self._nodes[target_key]
                pairs.append((source_node, target_node))
        pairs.sort(key=lambda pair: (pair[0].name.lower(), pair[1].name.lower()))
        return pairs

    def remove_relationship(self, source: str, target: str) -> None:
        source_key, target_key = source.lower(), target.lower()
        if source_key not in self._nodes:
            raise ValueError(f"Unknown source node: {source}")
        if target_key not in self._nodes:
            raise ValueError(f"Unknown target node: {target}")
        if target_key not in self._edges.get(source_key, set()):
            raise ValueError(f"Relationship {source} -> {target} does not exist")
        self._edges[source_key].remove(target_key)
        if not self._edges[source_key]:
            self._edges[source_key] = set()
        if target_key in self._reverse_edges:
            self._reverse_edges[target_key].discard(source_key)

    def remove_node(self, name: str) -> None:
        key = name.lower()
        if key not in self._nodes:
            raise ValueError(f"Unknown node: {name}")
        for predecessor in list(self._reverse_edges.get(key, set())):
            self._edges[predecessor].discard(key)
        for successor in list(self._edges.get(key, set())):
            self._reverse_edges[successor].discard(key)
        self._edges.pop(key, None)
        self._reverse_edges.pop(key, None)
        self._nodes.pop(key)

    def shortest_path(self, start: str, goal: str) -> List[KnowledgeNode]:
        start_key, goal_key = start.lower(), goal.lower()
        if start_key not in self._nodes:
            raise ValueError(f"Unknown start node: {start}")
        if goal_key not in self._nodes:
            raise ValueError(f"Unknown goal node: {goal}")

        queue: deque[str] = deque([start_key])
        parents: Dict[str, Optional[str]] = {start_key: None}

        while queue:
            current = queue.popleft()
            if current == goal_key:
                break
            for neighbor in self._edges.get(current, set()):
                if neighbor not in parents:
                    parents[neighbor] = current
                    queue.append(neighbor)

        if goal_key not in parents:
            raise ValueError(
                f"No learning path between '{self._nodes[start_key].name}' and "
                f"'{self._nodes[goal_key].name}'."
            )

        path: List[str] = []
        current: Optional[str] = goal_key
        while current is not None:
            path.append(current)
            current = parents[current]
        path.reverse()

        return [self._nodes[key] for key in path]

    def prerequisites(self, name: str) -> List[KnowledgeNode]:
        key = name.lower()
        if key not in self._nodes:
            raise ValueError(f"Unknown node: {name}")

        visited: Set[str] = set()
        order: List[str] = []

        def walk(stack: Iterable[str]) -> None:
            frontier = deque(stack)
            while frontier:
                current = frontier.popleft()
                if current in visited:
                    continue
                visited.add(current)
                order.append(current)
                for parent in sorted(self._reverse_edges.get(current, set())):
                    if parent not in visited:
                        frontier.append(parent)

        walk(self._reverse_edges.get(key, set()))
        return [self._nodes[node_key] for node_key in order]

    def dependents(self, name: str) -> List[KnowledgeNode]:
        key = name.lower()
        if key not in self._nodes:
            raise ValueError(f"Unknown node: {name}")
        dependents = [
            self._nodes[target_key]
            for target_key, parents in self._reverse_edges.items()
            if key in parents
        ]
        dependents.sort(key=lambda node: node.name.lower())
        return dependents

    def create_session(
        self,
        name: str,
        description: str,
        focus_tags: Iterable[str],
        linked_concepts: Iterable[str],
    ) -> LearningSession:
        concept_keys: List[str] = []
        missing: List[str] = []
        for concept in linked_concepts:
            key = concept.lower()
            if key not in self._nodes:
                missing.append(concept)
            else:
                concept_keys.append(key)
        if missing:
            raise ValueError(
                "Unknown concepts in session: "
                + ", ".join(sorted({item.strip() or "(blank)" for item in missing}))
            )
        session_id = str(uuid4())
        ordered_concepts: List[str] = []
        seen: Set[str] = set()
        for key in concept_keys:
            concept_name = self._nodes[key].name
            if concept_name not in seen:
                ordered_concepts.append(concept_name)
                seen.add(concept_name)

        session = LearningSession(
            id=session_id,
            name=name.strip(),
            description=description.strip(),
            focus_tags=sorted({tag.strip().lower() for tag in focus_tags if tag.strip()}),
            linked_concepts=ordered_concepts,
        )
        if not session.name:
            raise ValueError("Session name cannot be empty")
        self._sessions[session_id] = session
        return session

    def list_sessions(self) -> List[LearningSession]:
        return sorted(self._sessions.values(), key=lambda item: item.created_at, reverse=True)

    def update_session(
        self,
        session_id: str,
        *,
        status: Optional[str] = None,
        current_focus: Optional[str] = None,
    ) -> LearningSession:
        if session_id not in self._sessions:
            raise ValueError(f"Unknown session: {session_id}")
        session = self._sessions[session_id]
        if status is not None:
            status_value = status.strip()
            if status_value:
                session.status = status_value
        if current_focus is not None:
            focus_value = current_focus.strip()
            session.current_focus = focus_value or None
        return session

    def create_curriculum(
        self,
        title: str,
        description: str,
        tags: Iterable[str],
        source_url: Optional[str],
        linked_concepts: Iterable[str],
    ) -> Curriculum:
        concept_keys: List[str] = []
        missing: List[str] = []
        for concept in linked_concepts:
            key = concept.lower()
            if key not in self._nodes:
                missing.append(concept)
            else:
                concept_keys.append(key)
        if missing:
            raise ValueError(
                "Unknown concepts in curriculum: "
                + ", ".join(sorted({item.strip() or "(blank)" for item in missing}))
            )
        curriculum_id = str(uuid4())
        ordered_concepts: List[str] = []
        seen: Set[str] = set()
        for key in concept_keys:
            concept_name = self._nodes[key].name
            if concept_name not in seen:
                ordered_concepts.append(concept_name)
                seen.add(concept_name)

        curriculum = Curriculum(
            id=curriculum_id,
            title=title.strip(),
            description=description.strip(),
            tags=sorted({tag.strip().lower() for tag in tags if tag.strip()}),
            source_url=source_url.strip() if source_url else None,
            linked_concepts=ordered_concepts,
        )
        if not curriculum.title:
            raise ValueError("Curriculum title cannot be empty")
        self._curricula[curriculum_id] = curriculum
        return curriculum

    def list_curricula(self) -> List[Curriculum]:
        return sorted(self._curricula.values(), key=lambda item: item.uploaded_at, reverse=True)

    def generate_quiz(self, concept: str, count: int = 3) -> List[QuizQuestion]:
        concept_key = concept.lower()
        if concept_key not in self._nodes:
            raise ValueError(f"Unknown concept: {concept}")
        target = self._nodes[concept_key]
        questions: List[QuizQuestion] = []

        others = [node for key, node in self._nodes.items() if key != concept_key]
        random.shuffle(others)

        # Question 1: description match
        if target.description:
            distractors = [node.description for node in others if node.description]
            random.shuffle(distractors)
            choices = [target.description]
            for text in distractors[:3]:
                choices.append(text)
            while len(choices) < 4:
                choices.append(f"Practice prompt about {target.name}")
            random.shuffle(choices)
            correct_index = choices.index(target.description)
            questions.append(
                QuizQuestion(
                    id=str(uuid4()),
                    concept=target.name,
                    prompt=f"Which description best matches {target.name}?",
                    choices=choices,
                    correct_index=correct_index,
                )
            )

        # Question 2: prerequisite identification
        prereq_nodes = self.prerequisites(target.name)
        if prereq_nodes:
            distractor_names = [node.name for node in others if node.name not in {item.name for item in prereq_nodes}]
            random.shuffle(distractor_names)
            correct_prereq = prereq_nodes[0].name
            choices = [correct_prereq] + distractor_names[:3]
            while len(choices) < 4 and others:
                candidate = others.pop().name
                if candidate not in choices:
                    choices.append(candidate)
            random.shuffle(choices)
            questions.append(
                QuizQuestion(
                    id=str(uuid4()),
                    concept=target.name,
                    prompt=f"Which concept should you study before tackling {target.name}?",
                    choices=choices,
                    correct_index=choices.index(correct_prereq),
                )
            )

        # Question 3: dependent concept
        dependent_nodes = self.dependents(target.name)
        if dependent_nodes:
            distractor_names = [node.name for node in others if node.name not in {item.name for item in dependent_nodes}]
            random.shuffle(distractor_names)
            correct_dependent = dependent_nodes[0].name
            choices = [correct_dependent] + distractor_names[:3]
            while len(choices) < 4 and others:
                candidate = others.pop().name
                if candidate not in choices:
                    choices.append(candidate)
            random.shuffle(choices)
            questions.append(
                QuizQuestion(
                    id=str(uuid4()),
                    concept=target.name,
                    prompt=f"Which concept builds on {target.name}?",
                    choices=choices,
                    correct_index=choices.index(correct_dependent),
                )
            )

        if not questions:
            choices = [target.name] + [node.name for node in others[:3]]
            while len(choices) < 4:
                choices.append(f"Related idea {len(choices) + 1}")
            random.shuffle(choices)
            questions.append(
                QuizQuestion(
                    id=str(uuid4()),
                    concept=target.name,
                    prompt=f"Which option is most closely associated with {target.name}?",
                    choices=choices,
                    correct_index=choices.index(target.name),
                )
            )

        selected = questions[:count]
        for question in selected:
            self._quiz_bank[question.id] = question
        return selected

    def grade_quiz(self, question_id: str, selected_index: int) -> Tuple[bool, QuizQuestion]:
        question = self._quiz_bank.get(question_id)
        if question is None:
            raise ValueError(f"Unknown quiz question: {question_id}")
        if not 0 <= selected_index < len(question.choices):
            raise ValueError("Selected answer is out of range")
        return question.correct_index == selected_index, question

    # Idea sharing helpers -------------------------------------------------

    def publish_share(
        self,
        *,
        author: str,
        title: str,
        summary: str,
        tags: Iterable[str],
        linked_concepts: Iterable[str],
        visibility: str = "public",
        authorized_handles: Optional[Iterable[str]] = None,
    ) -> IdeaShare:
        """Create a shareable snapshot to help collaborators catch up quickly."""

        clean_author = author.strip()
        clean_title = title.strip()
        clean_summary = summary.strip()
        if not clean_author:
            raise ValueError("Author handle is required")
        if not clean_title:
            raise ValueError("Title is required")
        if not clean_summary:
            raise ValueError("Summary is required")

        normalized_tags = sorted({tag.strip().lower() for tag in tags if tag.strip()})
        if not normalized_tags:
            raise ValueError("At least one tag is required to anchor the share")

        normalized_visibility = visibility.lower()
        if normalized_visibility not in {"public", "connections", "private"}:
            raise ValueError("Visibility must be public, connections, or private")

        normalized_concepts: List[str] = []
        for concept in linked_concepts:
            if not concept:
                continue
            node = self.get_node(concept)
            if node is None:
                raise ValueError(f"Unknown concept for share: {concept}")
            normalized_concepts.append(node.name)

        share_id = str(uuid4())
        handles = sorted(
            {
                handle.strip().lower()
                for handle in (authorized_handles or [])
                if handle and handle.strip()
            }
        )
        share = IdeaShare(
            id=share_id,
            author=clean_author,
            title=clean_title,
            summary=clean_summary,
            tags=normalized_tags,
            linked_concepts=normalized_concepts,
            visibility=normalized_visibility,
            authorized_handles=handles,
        )
        self._shares[share_id] = share
        return share

    def list_shares(self, viewer: Optional[str] = None) -> List[IdeaShare]:
        """Return shares the viewer is allowed to see ordered by recency."""

        normalized_viewer = (viewer or "").strip().lower()
        visible: List[IdeaShare] = []
        for share in self._shares.values():
            if share.visibility == "public":
                visible.append(share)
                continue
            if normalized_viewer and share.author.lower() == normalized_viewer:
                visible.append(share)
                continue
            if (
                normalized_viewer
                and share.visibility == "connections"
                and normalized_viewer in share.authorized_handles
            ):
                visible.append(share)
        visible.sort(key=lambda item: item.created_at, reverse=True)
        return visible

    def authorize_share(self, share_id: str, handles: Iterable[str]) -> IdeaShare:
        """Grant additional collaborators access to a share."""

        share = self._shares.get(share_id)
        if share is None:
            raise ValueError(f"Unknown share: {share_id}")
        updated = sorted(
            {
                *share.authorized_handles,
                *(handle.strip().lower() for handle in handles if handle and handle.strip()),
            }
        )
        share.authorized_handles = updated
        self._shares[share_id] = share
        return share

    def affinity_for_viewer(self, viewer: str, limit: int = 5) -> List[IdeaMatch]:
        """Surface the most relevant shares for a viewer based on overlapping tags."""

        normalized_viewer = viewer.strip().lower()
        if not normalized_viewer:
            raise ValueError("Viewer handle required for affinity lookup")

        seen_tags: Set[str] = set()
        for share in self._shares.values():
            if share.author.lower() == normalized_viewer:
                seen_tags.update(share.tags)

        if not seen_tags:
            for share in self._shares.values():
                if share.visibility == "public":
                    seen_tags.update(share.tags)

        candidates: List[IdeaMatch] = []
        for share in self.list_shares(viewer=viewer):
            if share.author.lower() == normalized_viewer:
                continue
            shared_tags = sorted(set(share.tags).intersection(seen_tags))
            complementary = sorted(set(share.tags) - seen_tags)
            if not shared_tags and not complementary:
                continue
            overlap = len(shared_tags)
            breadth = len(shared_tags) + len(complementary)
            affinity = overlap / breadth if breadth else 0.0
            candidates.append(
                IdeaMatch(
                    share=share,
                    affinity=round(affinity, 3),
                    shared_tags=shared_tags,
                    complementary_tags=complementary,
                )
            )

        candidates.sort(key=lambda match: (match.affinity, match.share.created_at), reverse=True)
        return candidates[:limit]

    def compare_handles(self, primary: str, collaborator: str) -> Tuple[List[str], List[str]]:
        """Highlight shared and complementary interests between two handles."""

        primary_tags: Set[str] = set()
        collaborator_tags: Set[str] = set()

        for share in self._shares.values():
            author_handle = share.author.lower()
            if author_handle == primary.strip().lower():
                primary_tags.update(share.tags)
            if author_handle == collaborator.strip().lower():
                collaborator_tags.update(share.tags)

        return sorted(primary_tags & collaborator_tags), sorted(primary_tags ^ collaborator_tags)
