"""Tiny helpers for the ICSSI "LLMs via the API" tutorial.

Nothing here is magic. Every class is a thin wrapper over the official anthropic
SDK so that your hackathon code stays short. Read the raw-API version in the
notebooks first, then reach for these helpers.

The module provides five things. PRICING and cost_of_usage turn a response's token
usage into dollars. CostTracker accumulates spend across many calls and can warn you
when you pass a budget. ClaudeClient gives you a one-line ask() method with cost
tracking built in. Conversation manages multi-turn history for you. Agent is a small
research agent that uses the web tools and loops over rounds.
"""

from __future__ import annotations

from typing import Any

import anthropic

# models and pricing

DEFAULT_MODEL = "claude-sonnet-4-6"  # intermediate model, cheaper than Opus but more capable than Haiku

# usd per million tokens, as of mid-2026; update from https://www.anthropic.com/pricing
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-8": {"input": 5.0, "output": 25.0},
    "claude-opus-4-7": {"input": 5.0, "output": 25.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0},
}

# prompt-cache multipliers relative to the base input token rate
CACHE_WRITE_MULTIPLIER = 1.25  # writing to the 5-minute cache costs about 1.25x input
CACHE_READ_MULTIPLIER = 0.10  # reading from cache costs about 0.1x input

# server-side web search is billed per search, separately from tokens
WEB_SEARCH_PRICE = 10.0 / 1000  # $10 per 1000 searches; one request may run several


def usage_int(usage: Any, name: str) -> int:
    """Read an integer field off a usage object, treating a missing or None value as zero."""
    return getattr(usage, name, 0) or 0


def cost_of_usage(usage: Any, model: str, used_batch_api: bool = False) -> float:
    """Return the dollar cost of a single response, computed from its usage object."""
    price = PRICING.get(model)
    if price is None:
        return 0.0
    input_rate = price["input"] / 1_000_000
    output_rate = price["output"] / 1_000_000

    if used_batch_api:
        # batch API calls are billed at 0.5x the normal rates
        input_rate *= 0.5
        output_rate *= 0.5

    return (
        usage_int(usage, "input_tokens") * input_rate
        + usage_int(usage, "output_tokens") * output_rate
        + usage_int(usage, "cache_creation_input_tokens")
        * input_rate
        * CACHE_WRITE_MULTIPLIER
        + usage_int(usage, "cache_read_input_tokens")
        * input_rate
        * CACHE_READ_MULTIPLIER
    )


def text_of(response: Any) -> str:
    """Concatenate the text blocks of a response into a single plain string."""
    return "".join(
        getattr(block, "text", "")
        for block in response.content
        if getattr(block, "type", None) == "text"
    )


def count_web_searches(response: Any) -> int:
    """Count the web_search calls in one response. A single request can search several times."""
    return sum(
        1
        for block in response.content
        if getattr(block, "type", None) == "server_tool_use"
        and getattr(block, "name", None) == "web_search"
    )


# cost tracking


class CostTracker:
    """Accumulates token usage and dollars across many API calls.

    Pass an optional budget_usd to get a one-time warning when you cross it. That is
    handy when a room full of people are all spending on their own keys.
    """

    def __init__(self, budget_usd: float | None = None):
        self.budget_usd = budget_usd
        self.records: list[dict[str, Any]] = []
        self.already_warned = False

    def add(self, model: str, usage: Any, label: str = "", searches: int = 0) -> float:
        # check if reponse from batch API
        if usage.service_tier == "batch":
            used_batch_api = True
        else:
            used_batch_api = False

        # total cost is tokens plus any server-side web searches this call ran
        cost = cost_of_usage(usage, model, used_batch_api) + searches * WEB_SEARCH_PRICE
        self.records.append(
            {
                "label": label,
                "model": model,
                "input": usage_int(usage, "input_tokens"),
                "output": usage_int(usage, "output_tokens"),
                "cache_write": usage_int(usage, "cache_creation_input_tokens"),
                "cache_read": usage_int(usage, "cache_read_input_tokens"),
                "searches": searches,
                "cost": cost,
            }
        )
        if (
            self.budget_usd
            and self.total_usd > self.budget_usd
            and not self.already_warned
        ):
            self.already_warned = True
            print(
                f"  budget of ${self.budget_usd:.2f} exceeded "
                f"(now ${self.total_usd:.4f})"
            )
        return cost

    def add_response(self, model: str, response: Any, label: str = "") -> float:
        """Track a response, billing any server-side web searches it ran on top of tokens."""
        return self.add(
            model, response.usage, label=label, searches=count_web_searches(response)
        )

    @property
    def total_usd(self) -> float:
        return sum(record["cost"] for record in self.records)

    def report(self) -> None:
        """Print a per-model breakdown of calls, tokens, searches, and dollars, plus the total."""
        if not self.records:
            print("No API calls tracked yet.")
            return
        by_model: dict[str, dict[str, float]] = {}
        for record in self.records:
            stats = by_model.setdefault(
                record["model"],
                {
                    "calls": 0,
                    "input": 0,
                    "output": 0,
                    "cache_read": 0,
                    "searches": 0,
                    "cost": 0.0,
                },
            )
            stats["calls"] += 1
            stats["input"] += record["input"]
            stats["output"] += record["output"]
            stats["cache_read"] += record["cache_read"]
            stats["searches"] += record.get("searches", 0)
            stats["cost"] += record["cost"]
        print(
            f"{'model':<20}{'calls':>6}{'in tok':>10}{'out tok':>10}"
            f"{'cached':>10}{'searches':>10}{'cost $':>12}"
        )
        print("-" * 78)
        for model, stats in by_model.items():
            print(
                f"{model:<20}{stats['calls']:>6}{stats['input']:>10}{stats['output']:>10}"
                f"{stats['cache_read']:>10}{stats['searches']:>10}{stats['cost']:>12.4f}"
            )
        print("-" * 78)
        total_searches = sum(record.get("searches", 0) for record in self.records)
        print(
            f"{'TOTAL':<20}{len(self.records):>6}{'':>10}{'':>10}{'':>10}"
            f"{total_searches:>10}{self.total_usd:>12.4f}"
        )


# one-shot client


class ClaudeClient:
    """A thin convenience wrapper that adds sensible defaults and automatic cost tracking.

    A short example. Create the client with kit = ClaudeClient(), then call
    kit.ask("Summarize the abstract below in one sentence.") to get a plain string back.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 1024,
        tracker: CostTracker | None = None,
        client: anthropic.Anthropic | None = None,
    ):
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.tracker = tracker or CostTracker()

    def build_params(self, prompt, system, model, max_tokens, extra) -> dict[str, Any]:
        # accept either a plain string prompt or a full messages list
        messages = (
            [{"role": "user", "content": prompt}] if isinstance(prompt, str) else prompt
        )
        params: dict[str, Any] = {
            "model": model or self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
        }
        if system is not None:
            params["system"] = system
        params.update(extra)
        return params

    def ask(
        self, prompt, *, system=None, model=None, max_tokens=None, label="", **extra
    ) -> str:
        """Send one request, track its cost, and return the text of the reply."""
        params = self.build_params(prompt, system, model, max_tokens, extra)
        response = self.client.messages.create(**params)
        self.tracker.add(params["model"], response.usage, label=label or "ask")
        return text_of(response)


# multi-turn conversation


class Conversation:
    """Remembers history so that you do not have to resend it by hand.

    The API is stateless, which means you are responsible for the running transcript.
    This class keeps self.messages and appends each turn for you.
    """

    def __init__(
        self,
        client: ClaudeClient,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
    ):
        self.client = client
        self.system = system
        self.model = model or client.model
        self.max_tokens = max_tokens or client.max_tokens
        self.messages: list[dict[str, Any]] = []

    def send(self, user_text: str, label: str = "turn") -> str:
        self.messages.append({"role": "user", "content": user_text})
        params: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": self.messages,
        }
        if self.system is not None:
            params["system"] = self.system
        response = self.client.client.messages.create(**params)
        self.client.tracker.add(self.model, response.usage, label=label)
        # keep the full content, not just the text, so non-text blocks survive
        self.messages.append({"role": "assistant", "content": response.content})
        return text_of(response)


# web research agent


def server_tool_calls(response: Any) -> list[str]:
    """Return a human-readable list of the web searches and fetches in one response."""
    actions = []
    for block in response.content:
        if getattr(block, "type", None) == "server_tool_use":
            tool_input = getattr(block, "input", {}) or {}
            if block.name == "web_search":
                actions.append(f"web_search({tool_input.get('query', '')!r})")
            elif block.name == "web_fetch":
                actions.append(f"web_fetch({tool_input.get('url', '')!r})")
            else:
                actions.append(f"{block.name}(...)")
    return actions


class Agent:
    """A minimal research agent built on Claude's server-side web tools.

    Each iteration is a round. In a round, Claude thinks, may run web_search
    or web_fetch on Anthropic's servers, and either finishes with stop_reason "end_turn"
    or pauses with "pause_turn" to keep going. We cap the number of rounds and log the
    cost of each one.
    """

    def __init__(
        self,
        client: ClaudeClient,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 2048,
        max_rounds: int = 6,
        web: bool = True,
    ):
        self.client = client
        self.system = system
        self.model = model or client.model
        self.max_tokens = max_tokens
        self.max_rounds = max_rounds
        self.tools = (
            [
                {
                    "type": "web_search_20260209",
                    "name": "web_search",
                },  # these tool IDs are updated periodically; check https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
                {"type": "web_fetch_20260209", "name": "web_fetch"},
            ]
            if web
            else []
        )

    def run(self, task: str, verbose: bool = True) -> dict[str, Any]:
        messages: list[dict[str, Any]] = [{"role": "user", "content": task}]
        rounds = 0
        response = None
        while rounds < self.max_rounds:
            rounds += 1
            params: dict[str, Any] = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages,
                "tools": self.tools,
            }
            if self.system is not None:
                params["system"] = self.system
            response = self.client.client.messages.create(**params)
            cost = self.client.tracker.add_response(
                self.model, response, label=f"agent round {rounds}"
            )
            if verbose:
                actions = server_tool_calls(response)
                shown = "  ".join(actions) if actions else "(no web tools this round)"
                print(
                    f"round {rounds}: stop={response.stop_reason:<10} "
                    f"${cost:.4f}  {shown}"
                )
            messages.append({"role": "assistant", "content": response.content})
            # server-side tool loops pause when they hit their iteration cap;
            # re-send with no new user message to let the server resume
            if response.stop_reason != "pause_turn":
                break
        return {
            "answer": text_of(response) if response is not None else "",
            "rounds": rounds,
            "stop_reason": getattr(response, "stop_reason", None),
        }
