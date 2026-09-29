"""The council loop. Structure only — no model names, no prompts, no selectors."""

from pathlib import Path

from .agents import ChatAgent, ToolAgent
from .clients.base import ModelClient
from .config import CouncilConfig
from .log import Log
from .router import Router


def build_moderator_prompt(
    config: CouncilConfig, root: Path, log: Log, phase: str
) -> str:
    catalog = config.read_catalog(root)
    mod_prompt = config.read_prompt(root, config.moderator.prompt)
    return (
        f"{catalog}\n\n---\n\n{mod_prompt}\n\n"
        f"## Current log\n{log.render_trimmed()}\n\n"
        f"## Phase: {phase}"
    )


def build_agents(
    config: CouncilConfig, root: Path, clients: dict[str, ModelClient]
) -> dict[str, ChatAgent]:
    agents: dict[str, ChatAgent] = {}
    for role, acfg in config.agents.items():
        prompt = config.read_prompt(root, acfg.prompt)
        client = clients[role]
        if acfg.type == "tool_agent":
            agents[role] = ToolAgent(role, acfg, prompt, client)
        else:
            agents[role] = ChatAgent(role, acfg, prompt, client)
    return agents


def extract_ask_for(log: Log, role: str) -> str:
    """Find the most recent moderator line addressing this role."""
    for entry in reversed(log.entries):
        if entry.who == "MODERATOR" and f"@{role}" in entry.text:
            for line in entry.text.splitlines():
                if f"@{role}" in line:
                    return line.strip()
    return f"Address the current problem from your role as {role}."


async def invoke_role(
    role: str, log: Log, agents: dict[str, ChatAgent]
) -> None:
    agent = agents.get(role)
    if agent is None:
        log.append(role, "UNAVAILABLE")
        return
    ask = extract_ask_for(log, role)
    response = await agent.respond(log, ask)
    log.append(role, response.text)


async def run_council(
    problem: str,
    config: CouncilConfig,
    root: Path,
    clients: dict[str, ModelClient],
) -> tuple[str, Log]:
    router = Router(config)
    agents = build_agents(config, root, clients)
    moderator = clients["moderator"]

    log = Log(trim_after=config.loop.log_trim_after)
    log.pin("CATALOG", config.read_catalog(root))
    log.pin("PROBLEM", problem)

    # Turn 1 — bootstrap
    mod_prompt = build_moderator_prompt(config, root, log, "bootstrap")
    mod_reply = await moderator.query(mod_prompt)
    log.append("MODERATOR", mod_reply)

    targets = router.parse_start(mod_reply)
    targets = router.enforce_invariants(targets, problem)
    if not targets:
        targets = ["ARCHITECT", "CRITIC"]

    for target in targets:
        await invoke_role(target, log, agents)

    # Subsequent rounds
    for _ in range(1, config.loop.max_rounds):
        if log.turn_count() >= config.loop.max_turns:
            break

        mod_prompt = build_moderator_prompt(config, root, log, "route")
        mod_reply = await moderator.query(mod_prompt)
        log.append("MODERATOR", mod_reply)

        if router.is_final(mod_reply):
            return router.extract_final(mod_reply), log

        next_targets = router.parse_targets(mod_reply)

        if "CODER" in next_targets:
            log.append("CODER", "[tool loop — Phase 2 placeholder]")
            break

        for target in next_targets:
            await invoke_role(target, log, agents)

    # Force final
    log.append("SYSTEM", "Round budget reached. Forcing synthesis.")
    force_prompt = (
        build_moderator_prompt(config, root, log, "force_final")
        + "\n\nYou have exceeded the round budget. "
        + "Synthesize the council's input now. "
        + "Reply ONLY with <final>your synthesis</final>."
    )
    final_reply = await moderator.query(force_prompt)
    log.append("MODERATOR", final_reply)
    return router.extract_final(final_reply), log