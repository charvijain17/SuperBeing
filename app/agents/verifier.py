"""Verifier agent: improves clarity and query coverage, without external fact checking."""


def verifier_prompt(query: str, draft: str) -> str:
    return f'''Improve the draft answer below.
Check that it directly answers the original request, fills obvious omissions, and is clear.
Return only the improved final answer. Do not claim that you fact-checked or searched the web.

Original request: {query}
Draft answer: {draft}'''
