# Using LLMs via the API: ICSSI 2026 Hackathon

This is a hands-on, fork-me tutorial for building with the Anthropic (Claude) API. It is
flavored for the Science of Science and Innovation, so every example works on scholarly
artifacts such as paper abstracts, citations, patents, grants, scientist careers, and
collaboration networks.

You can run everything in your browser with Google Colab (zero install) or locally.

## Option A: Google Colab (nothing to install)

1. Open Google Colab > File > Open notebook > GitHub > paste the repo URL > select the notebook(s).
2. Get an API key at <https://console.anthropic.com/> under Settings then API Keys.
3. In Colab, click the Secrets panel (the key icon in the left sidebar), add a secret
   named `ANTHROPIC_API_KEY`, and turn on notebook access.
4. Run the cells top to bottom. The first cell installs `anthropic` automatically.

## Option B: Local (Python 3.10 or newer)

```bash
# create an isolated environment
python3 -m venv .venv

# activate it
source .venv/bin/activate          # macOS and Linux
# .venv\Scripts\activate           # Windows (PowerShell)

# install dependencies
pip install -r requirements.txt

# add your key
cp .env.example .env               # then edit .env and paste your key
#   (Windows: copy .env.example .env)

# launch
jupyter lab                        # or open the folder in VS Code or Cursor
```

You do not need Docker or conda. Python 3.10 or newer is required. If you use VS Code or
Cursor, open the folder and select the `.venv` interpreter as your kernel instead of
launching JupyterLab.

> Note that this costs a little real money. Each notebook makes live API calls. The whole
> tutorial runs for well under one dollar on your own key. We track spend live with a
> `CostTracker` so you always see what you are spending.

## Live demos

Run these three notebooks in order.

| # | Notebook | What you learn |
|---|----------|----------------|
| 0 | [`00_setup.ipynb`](00_setup.ipynb) | Make your first API call and read token usage. |
| 1 | [`01_cost.ipynb`](01_cost.ipynb) | Minimize cost: tokens, pricing, model tiering, prompt caching, and the Batch API. |
| 2 | [`02_web_and_documents.ipynb`](02_web_and_documents.ipynb) | Web search and fetch, plus reading a PDF and summarizing it. |

## Take-home notebooks

These are templates to fork for your own project.

| # | Notebook | What is inside |
|---|----------|---------------|
| 10 | [`take_home_tutorials/10_fundamentals.ipynb`](take_home_tutorials/10_fundamentals.ipynb) | The Messages API, statelessness, streaming, and error handling. |
| 11 | [`take_home_tutorials/11_structured_and_tools.ipynb`](take_home_tutorials/11_structured_and_tools.ipynb) | Getting reliable JSON out and defining your own tools. |
| 12 | [`take_home_tutorials/12_interactive_vs_noninteractive.ipynb`](take_home_tutorials/12_interactive_vs_noninteractive.ipynb) | Interactive chat versus an unattended agent that loops over rounds. |

The file `claude_kit.py` holds small helper classes (`ClaudeClient`, `CostTracker`,
`Conversation`, and `Agent`) used across the notebooks so that your own code stays short.

## Models used here

The default is Claude Sonnet 4.6 (`claude-sonnet-4-6`). The cost notebook also uses
Opus 4.8 (`claude-opus-4-8`) and Haiku 4.5 (`claude-haiku-4-5`) to show the tradeoff
between quality and price. Take-home notebooks default to Haiku to minimize cost.
