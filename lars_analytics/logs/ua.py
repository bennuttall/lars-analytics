import user_agents


# Overrides for UAs that user_agents library misidentifies
UA_OVERRIDES = [
    ("ChatGPT", "ChatGPT", True),
    ("Feedly", "Feedly", True),
    ("Bytespider", "Bytespider", True),
    ("Go-http-client", "Go-http-client", True),
]


def parse_ua(user_agent: str) -> tuple[str, bool]:
    """Returns (simplified_name, is_bot)."""
    if not user_agent:
        return "Unknown", False
    for pattern, name, is_bot in UA_OVERRIDES:
        if pattern in user_agent:
            return name, is_bot
    parsed = user_agents.parse(user_agent)
    return parsed.browser.family, parsed.is_bot
