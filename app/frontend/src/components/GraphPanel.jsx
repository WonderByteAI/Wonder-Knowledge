import { useMemo } from 'react';

const RING_STEP = 40;
const BASE_RADIUS = 120;

function polarToCartesian(index, total, radius) {
  if (!total) {
    return { x: 0, y: 0 };
  }
  const angle = (2 * Math.PI * index) / total;
  return {
    x: radius * Math.cos(angle),
    y: radius * Math.sin(angle),
  };
}

export function GraphPanel({ nodes, relationships }) {
  const positioned = useMemo(() => {
    return nodes.map((node, index) => {
      const radius = BASE_RADIUS + (index % 3) * RING_STEP;
      const { x, y } = polarToCartesian(index, nodes.length, radius);
      return {
        name: node.name,
        x,
        y,
      };
    });
  }, [nodes]);

  const findPosition = (name) => positioned.find((entry) => entry.name === name);

  return (
    <section className="panel graph-panel">
      <header className="panel-header">
        <p className="eyebrow">Concept graph</p>
        <h2>Your connected knowledge</h2>
        <p className="helper">Explore how your concepts relate to one another at a glance.</p>
      </header>
      <div className="graph-canvas">
        {relationships.map((edge) => {
          const source = findPosition(edge.source);
          const target = findPosition(edge.target);
          if (!source || !target) {
            return null;
          }
          const dx = target.x - source.x;
          const dy = target.y - source.y;
          const length = Math.sqrt(dx * dx + dy * dy);
          const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
          const midX = source.x + dx / 2;
          const midY = source.y + dy / 2;
          return (
            <span
              key={`${edge.source}-${edge.target}`}
              className="graph-edge"
              style={{
                width: `${length}px`,
                transform: `translate(calc(50% + ${source.x}px), calc(50% + ${source.y}px)) rotate(${angle}deg)`,
              }}
            >
              <span
                className="graph-edge-label"
                style={{
                  transform: `translate(${midX - source.x}px, ${midY - source.y - 12}px)`,
                }}
              >
                {edge.source} → {edge.target}
              </span>
            </span>
          );
        })}
        {positioned.map((node) => (
          <span
            key={node.name}
            className="graph-node"
            style={{ transform: `translate(calc(50% + ${node.x}px), calc(50% + ${node.y}px))` }}
          >
            {node.name}
          </span>
        ))}
      </div>
    </section>
  );
}
