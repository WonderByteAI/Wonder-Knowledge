export function InsightPanel({ nodes, sessions, curricula, shares, matches, quizItems }) {
  return (
    <aside className="panel sidebar">
      <header className="panel-header">
        <p className="eyebrow">Live insights</p>
        <h2>What&apos;s new in your studio</h2>
        <p className="helper">Review active sessions, curated resources, and suggested collaborators.</p>
      </header>
      <div className="panel-body insights">
        <section className="insight-block">
          <h3>Concepts</h3>
          <ul className="list">
            {nodes.map((node) => (
              <li key={node.name}>
                <strong>{node.name}</strong>
                {node.tags?.length ? <span className="chip subtle">{node.tags.join(', ')}</span> : null}
                {node.description ? <p>{node.description}</p> : null}
              </li>
            ))}
          </ul>
        </section>
        <section className="insight-block">
          <h3>Learning sessions</h3>
          <ul className="list">
            {sessions.map((session) => (
              <li key={session.id}>
                <header className="item-header">
                  <strong>{session.name}</strong>
                  <span className="chip success">{session.status}</span>
                </header>
                {session.description ? <p>{session.description}</p> : null}
                {session.focus_tags?.length ? <p className="helper">Focus: {session.focus_tags.join(', ')}</p> : null}
              </li>
            ))}
          </ul>
        </section>
        <section className="insight-block">
          <h3>Curricula</h3>
          <ul className="list">
            {curricula.map((curriculum) => (
              <li key={curriculum.id}>
                <strong>{curriculum.title}</strong>
                {curriculum.tags?.length ? <span className="chip subtle">{curriculum.tags.join(', ')}</span> : null}
                {curriculum.description ? <p>{curriculum.description}</p> : null}
                {curriculum.source_url ? (
                  <a href={curriculum.source_url} target="_blank" rel="noreferrer">
                    Source
                  </a>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
        <section className="insight-block">
          <h3>Shares</h3>
          <ul className="list">
            {shares.map((share) => (
              <li key={share.id}>
                <header className="item-header">
                  <strong>{share.title}</strong>
                  <span className="chip subtle">{share.visibility}</span>
                </header>
                <p>{share.summary}</p>
                <p className="helper">By {share.author}</p>
              </li>
            ))}
          </ul>
        </section>
        <section className="insight-block">
          <h3>Suggested collaborators</h3>
          <ul className="list matches">
            {matches.map((match) => (
              <li key={match.id}>
                <header className="item-header">
                  <strong>{match.title}</strong>
                  <span className="chip primary">{(match.score * 100).toFixed(0)}% match</span>
                </header>
                <p className="helper">{match.summary}</p>
                {match.tags?.length ? <p className="helper">Tags: {match.tags.join(', ')}</p> : null}
              </li>
            ))}
          </ul>
        </section>
        {quizItems.length ? (
          <section className="insight-block">
            <h3>Quiz preview</h3>
            <ol className="quiz-list">
              {quizItems.map((item, index) => (
                <li key={item.question}>
                  <p>
                    <strong>Question {index + 1}.</strong> {item.question}
                  </p>
                  <ul className="quiz-options">
                    {item.options.map((option) => (
                      <li key={option}>{option}</li>
                    ))}
                  </ul>
                </li>
              ))}
            </ol>
          </section>
        ) : null}
      </div>
    </aside>
  );
}
