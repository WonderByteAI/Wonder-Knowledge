import { useEffect, useState } from 'react';
import { fetchJson, normaliseList } from './api.js';
import { ActionPanel } from './components/ActionPanel.jsx';
import { ChatPanel } from './components/ChatPanel.jsx';
import { GraphPanel } from './components/GraphPanel.jsx';
import { InsightPanel } from './components/InsightPanel.jsx';

const INITIAL_CHAT = [
  {
    role: 'system',
    flair: 'Wonder navigator',
    timestamp: 'moments ago',
    content: 'Welcome back! Explore your graph, curate resources, and share ideas with collaborators.',
  },
  {
    role: 'user',
    timestamp: 'moments ago',
    content: 'What does my FastAPI learning path look like today?',
  },
];

async function loadGraph() {
  const [nodes, relationships] = await Promise.all([
    fetchJson('/knowledge'),
    fetchJson('/relationships'),
  ]);
  return { nodes, relationships };
}

export default function App() {
  const [graph, setGraph] = useState({ nodes: [], relationships: [] });
  const [sessions, setSessions] = useState([]);
  const [curricula, setCurricula] = useState([]);
  const [shares, setShares] = useState([]);
  const [matches, setMatches] = useState([]);
  const [quizItems, setQuizItems] = useState([]);
  const [chat, setChat] = useState(INITIAL_CHAT);

  useEffect(() => {
    async function bootstrap() {
      try {
        const [graphData, sessionsResponse, curriculaResponse, sharesResponse] = await Promise.all([
          loadGraph(),
          fetchJson('/sessions'),
          fetchJson('/curricula'),
          fetchJson('/shares'),
        ]);
        setGraph(graphData);
        setSessions(sessionsResponse);
        setCurricula(curriculaResponse);
        setShares(sharesResponse);
      } catch (error) {
        console.error('Failed to load initial data', error);
      }

      try {
        const response = await fetchJson('/shares/matchups?viewer=wonder-team');
        const simplified = response.map((item) => ({
          id: item.share.id,
          title: item.share.title,
          summary: item.share.summary,
          tags: item.share.tags,
          score: item.affinity,
        }));
        setMatches(simplified);
      } catch (error) {
        console.warn('Unable to load share matchups', error);
      }
    }

    bootstrap();
  }, []);

  const handleChatSend = (message, attachments) => {
    setChat((current) => [
      ...current,
      { role: 'user', timestamp: 'just now', content: message, tags: attachments.map((item) => `file:${item}`) },
      {
        role: 'assistant',
        flair: 'Wonder navigator',
        timestamp: 'responding…',
        content:
          'I will align your sessions and curricula. Check the insights column for the latest recommendations.',
      },
    ]);
  };

  const createConcept = async (payload) => {
    await fetchJson('/knowledge', {
      method: 'POST',
      body: JSON.stringify({
        name: payload.name,
        description: payload.description?.trim() ?? '',
        tags: normaliseList(payload.tags),
      }),
    });
    const graphData = await loadGraph();
    setGraph(graphData);
  };

  const createSession = async (payload) => {
    await fetchJson('/sessions', {
      method: 'POST',
      body: JSON.stringify({
        name: payload.name,
        description: payload.description?.trim() ?? '',
        focus_tags: normaliseList(payload.focus_tags),
        linked_concepts: normaliseList(payload.linked_concepts),
      }),
    });
    const response = await fetchJson('/sessions');
    setSessions(response);
  };

  const createCurriculum = async (payload) => {
    await fetchJson('/curricula', {
      method: 'POST',
      body: JSON.stringify({
        title: payload.title,
        description: payload.description?.trim() ?? '',
        tags: normaliseList(payload.tags),
        source_url: payload.source_url?.trim() || null,
        linked_concepts: normaliseList(payload.linked_concepts),
      }),
    });
    const response = await fetchJson('/curricula');
    setCurricula(response);
  };

  const createShare = async (payload) => {
    await fetchJson('/shares', {
      method: 'POST',
      body: JSON.stringify({
        author: payload.author,
        title: payload.title,
        summary: payload.summary,
        tags: normaliseList(payload.tags),
        linked_concepts: normaliseList(payload.linked_concepts),
        visibility: payload.visibility,
        authorized_handles: normaliseList(payload.authorized_handles),
      }),
    });
    const response = await fetchJson('/shares');
    setShares(response);
  };

  const generateQuiz = async (payload) => {
    const response = await fetchJson('/quiz/generate', {
      method: 'POST',
      body: JSON.stringify({
        concept: payload.concept,
        difficulty: payload.difficulty,
        questions: Number(payload.questions) || 3,
      }),
    });
    const items = response.questions.map((question) => ({
      question: question.prompt,
      options: question.choices,
    }));
    setQuizItems(items);
  };

  return (
    <div className="app-shell">
      <ActionPanel
        onCreateConcept={createConcept}
        onCreateSession={createSession}
        onCreateCurriculum={createCurriculum}
        onCreateShare={createShare}
        onGenerateQuiz={generateQuiz}
      />
      <div className="middle-column">
        <GraphPanel nodes={graph.nodes} relationships={graph.relationships} />
        <ChatPanel messages={chat} onSend={handleChatSend} />
      </div>
      <InsightPanel
        nodes={graph.nodes}
        sessions={sessions}
        curricula={curricula}
        shares={shares}
        matches={matches}
        quizItems={quizItems}
      />
    </div>
  );
}
