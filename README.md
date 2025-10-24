# Wonder-Knowledge

Wonder Knowledge is a conversational knowledge mapping studio. It blends a FastAPI backend with a ChatGPT-inspired front end so you can talk through ideas, capture concepts, link prerequisites, and instantly generate learning itineraries.

## Prototype application

The repository hosts a full vertical slice:

- **FastAPI backend** – Stores knowledge nodes in memory, computes learning paths, manages sessions/quizzes/curricula, and now exposes collaborative shares plus an MCP manifest for agent access.
- **React conversational UI** – Mobile-first interface with a left rail of mini tools, a central chat stream, and a Geo4G-inspired knowledge tree rendered with React.
- **Attachment sandbox** – Upload images or documents during a turn (kept locally in the browser for this prototype) to keep your conversations rich.
- **Idea sharing feed** – Publish quick “thought snapshots”, control visibility, and surface affinity-ranked matches so crews can sync faster.

### API surface

The backend exposes the core endpoints plus new collaborative surfaces:

- `POST /knowledge` – create or update concepts that a learner already understands.
- `GET /knowledge` – list all available concepts in the current in-memory graph.
- `GET /knowledge/{name}` – inspect a single concept together with its prerequisites.
- `DELETE /knowledge/{name}` – remove a concept and unlink all of its dependencies.
- `POST /relationships` – define dependency relationships between concepts.
- `GET /relationships` – list every dependency currently defined.
- `DELETE /relationships` – remove a dependency between two concepts.
- `GET /learning-path?start=...&goal=...` – compute the shortest learning path between two concepts.
- `POST /shares` – publish a knowledge share with visibility controls.
- `GET /shares?viewer=handle` – retrieve shares visible to a viewer.
- `POST /shares/{share_id}/authorize` – extend access to additional handles.
- `GET /shares/matchups?viewer=handle` – fetch affinity-ranked matches to accelerate brainstorms.
- `GET /shares/compare?handle_a=...&handle_b=...` – quickly see shared and divergent interests between collaborators.
- `GET /.well-known/mcp/manifest.json` – lightweight MCP manifest so GPT-style agents can discover available actions.

Concepts are still stored in memory to keep iteration fast. The API is ready to be swapped for a graph database (e.g. Neo4j) and already advertises an MCP manifest so ChatGPT or other MCP-compatible agents can call tools safely.

### Front-end experience

Visit [http://localhost:8000/](http://localhost:8000/) after starting the server to open the Wonder Knowledge Explorer UI. Highlights:

- **Chat-first workflow** – Chat just like in ChatGPT, switch tools to add concepts, launch sessions, publish shares, or request a learning path.
- **Geo4G-inspired tree** – A React-rendered radial map keeps foundational skills at the core and experimental areas on the frontier.
- **Attachment friendly** – Upload artefacts (images, docs) from your device when logging a turn. Files never leave the browser during this prototype.
- **Quick quizzes** – Generate concept check-ins on the fly and grade each attempt without leaving the chat stream.
- **Session & curriculum rail** – Create focussed learning sessions, catalogue syllabi, and see them update live alongside the conversation.
- **Idea share radar** – Post thought snapshots, browse the feed, and view affinity-ranked matches or overlap comparisons to accelerate team catch-ups.

The interface is responsive, so you can comfortably plan from phones, tablets, or desktops. Everything uses the same API endpoints, so actions appear instantly if you inspect the `/docs` view.

### Example workflow

1. Start a conversation and choose **Add concept** to describe a new skill or topic.
2. Use **Learning session** to organise related ideas and keep focus tags top of mind.
3. Flip to **Learning path** or **Generate quiz** to explore dependencies and reinforce knowledge.
4. Drop study artefacts (slides, photos, notes) on a turn with the attachment dropzone to keep everything organised.
5. Publish a **Knowledge share** so collaborators instantly understand your context and priorities.
6. Watch the Geo4G-inspired tree update in real time as your graph expands.

### Learning accelerators

- **Learning sessions** – Group related concepts under a named journey (e.g. “Full-stack Python sprint”). Track status, surface the current focus, and view session metadata from the right-hand insight rail.
- **Curriculum uploads** – Attach lecture notes, syllabi, or course outlines to concepts. The FastAPI backend stores metadata while the UI presents a quick-access library with outbound links.
- **Quiz flow** – Wonder generates short multiple-choice quizzes based on descriptions, prerequisites, and dependents. Each answer is graded via `/quizzes/attempt`, revealing the correct choice plus coaching tips.
- **Idea shares & matches** – Publish snapshots of what you are exploring, authorise collaborators, and let Wonder surface overlapping interests or complementary gaps.

### Front-end layout

The conversation canvas mirrors the latest ChatGPT experience:

- **Left rail** – A vertical launcher for chat, concept capture, prerequisite linking, learning paths, quizzes, sessions, curricula, and attachments. Each tool swaps the contextual form in the composer.
- **Center stream** – Chat bubbles for you and Wonder, quiz cards with interactive answer buttons, and inline attachment previews. Everything is designed for thumb-friendly use on phones.
- **Right insights** – Knowledge health metrics, the Geo4G skill tree, personalised tag summaries, live sessions, and your curriculum library.

### Research snapshots

- [Quizlet](https://en.wikipedia.org/wiki/Quizlet) leans on flashcards, matching games, and live quizzes to reinforce memory, underscoring the value of lightweight practice loops.
- [Duolingo](https://en.wikipedia.org/wiki/Duolingo) emphasises streaks, levels, and structured lessons; its public approach to tracking progress inspired Wonder’s session and curriculum panels.

## Getting started

1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open [http://localhost:8000/](http://localhost:8000/) for the conversational UI, or visit [http://localhost:8000/docs](http://localhost:8000/docs) to explore the OpenAPI interface.

## Next steps

- Persist the graph in a database and sync attachments to cloud storage.
- Integrate AI copilots to propose tags, summarise attachments, and recommend study plans.
- Package the UI for native smartphone and smartwatch experiences so Wonder travels with you anywhere.
