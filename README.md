# ai-dev-agent

Multi-agent development automation. A crew of specialized LLM agents — developer, tester, and documenter — that collaborate on a codebase: generating code, writing tests, and producing documentation, with shared memory and direct GitHub integration.

## How it works

Each agent is defined declaratively in `agents/*.json` (role, goal, tools) and loaded at runtime by `core/agent_loader.py`. The crew shares context through a persistent memory layer, so the tester knows what the developer wrote and the documenter sees both.

| Component | Purpose |
|---|---|
| `agents/developer.json` | Writes and refactors code for a given task |
| `agents/tester.json` | Generates and maintains tests for the developer's output |
| `agents/documenter.json` | Produces documentation from code and change history |
| `core/memory_manager.py` | Shared agent memory — ChromaDB vector store + Redis state |
| `core/github_handler.py` | Reads repos, opens branches/PRs via the GitHub API |
| `core/test_manager.py` | Runs the generated tests and feeds results back |
| `core/documentation_generator.py` | Renders the documenter's output |

## Stack

- **CrewAI** — agent orchestration
- **LangChain + OpenAI** — LLM calls and tooling
- **ChromaDB** — vector memory (embeddings)
- **Redis** — fast shared state between agents
- **github3.py** — GitHub integration
- **Docker / docker-compose** — one-command local setup

## Getting started

```bash
cp env.example .env      # add your OpenAI + GitHub tokens
docker-compose up        # starts Redis, ChromaDB, and the agent runtime
```

Then point it at a task:

```bash
python main.py           # see config/settings.py for task and repo configuration
```

## Configuration

Runtime settings live in `config/settings.py`; secrets are read from `.env` (see `env.example` for the full list). Agent behavior — prompts, roles, and tool access — is edited in the `agents/*.json` files without touching code.

## License

See [LICENSE](LICENSE).
