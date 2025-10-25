import { ActionForm } from './ActionForm.jsx';

export function ActionPanel({
  onCreateConcept,
  onCreateSession,
  onCreateCurriculum,
  onCreateShare,
  onGenerateQuiz,
}) {
  return (
    <aside className="panel sidebar">
      <header className="panel-header">
        <p className="eyebrow">Create & organise</p>
        <h2>Launch new knowledge artifacts</h2>
        <p className="helper">
          Capture concepts, plan focused sessions, and publish shares to collaborate with your network.
        </p>
      </header>
      <div className="panel-body">
        <div className="stack">
          <div className="quick-grid">
            <a href="#concept-form" className="quick-card">Concept</a>
            <a href="#session-form" className="quick-card">Session</a>
            <a href="#curriculum-form" className="quick-card">Curriculum</a>
            <a href="#share-form" className="quick-card">Share</a>
          </div>
          <ActionForm
            id="concept-form"
            title="New concept"
            description="Add a concept node to your Wonder Knowledge graph."
            submitLabel="Create concept"
            onSubmit={onCreateConcept}
            fields={[
              { name: 'name', label: 'Name', required: true },
              { name: 'description', label: 'Description', kind: 'textarea', rows: 3 },
              { name: 'tags', label: 'Tags', placeholder: 'python, web' },
            ]}
          />
          <ActionForm
            id="session-form"
            title="New session"
            description="Frame a focused learning sprint tied to your graph nodes."
            submitLabel="Launch session"
            onSubmit={onCreateSession}
            fields={[
              { name: 'name', label: 'Session name', required: true },
              { name: 'description', label: 'Description', kind: 'textarea', rows: 3 },
              { name: 'focus_tags', label: 'Focus tags', placeholder: 'python, collaboration' },
              { name: 'linked_concepts', label: 'Linked concepts', placeholder: 'Python, FastAPI' },
            ]}
          />
          <ActionForm
            id="curriculum-form"
            title="Upload curriculum"
            description="Pair structured resources with your current focus."
            submitLabel="Upload curriculum"
            onSubmit={onCreateCurriculum}
            fields={[
              { name: 'title', label: 'Title', required: true },
              { name: 'description', label: 'Summary', kind: 'textarea', rows: 3 },
              { name: 'tags', label: 'Tags', placeholder: 'fastapi, backend' },
              { name: 'source_url', label: 'Source URL', type: 'url', placeholder: 'https://fastapi.tiangolo.com/' },
              { name: 'linked_concepts', label: 'Linked concepts', placeholder: 'REST APIs, FastAPI' },
            ]}
          />
          <ActionForm
            id="share-form"
            title="Publish idea share"
            description="Broadcast learnings or request collaborators."
            submitLabel="Publish share"
            onSubmit={onCreateShare}
            fields={[
              { name: 'author', label: 'Handle', required: true },
              { name: 'title', label: 'Title', required: true },
              { name: 'summary', label: 'Summary', kind: 'textarea', rows: 3, required: true },
              { name: 'tags', label: 'Tags', placeholder: 'brainstorm, ai' },
              { name: 'linked_concepts', label: 'Linked concepts', placeholder: 'Python, REST APIs' },
              {
                name: 'visibility',
                label: 'Visibility',
                kind: 'select',
                options: [
                  { value: 'public', label: 'Public' },
                  { value: 'connections', label: 'Connections' },
                  { value: 'private', label: 'Private' },
                ],
              },
              {
                name: 'authorized_handles',
                label: 'Authorized handles',
                placeholder: 'friend1, friend2',
              },
            ]}
          />
          <ActionForm
            id="quiz-form"
            title="Generate quiz"
            description="Practice with an adaptive quiz built from your graph."
            submitLabel="Generate quiz"
            successLabel="Generated"
            onSubmit={onGenerateQuiz}
            fields={[
              { name: 'concept', label: 'Concept', required: true },
              {
                name: 'difficulty',
                label: 'Difficulty',
                kind: 'select',
                options: [
                  { value: 'beginner', label: 'Beginner' },
                  { value: 'intermediate', label: 'Intermediate' },
                  { value: 'advanced', label: 'Advanced' },
                ],
                defaultValue: 'intermediate',
              },
              { name: 'questions', label: 'Question count', type: 'number', defaultValue: 3 },
            ]}
          />
        </div>
      </div>
    </aside>
  );
}
