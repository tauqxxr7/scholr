from agents.doubt_agent import build_doubt_prompt, get_doubt_generation_config
from agents.notes_agent import build_notes_prompt, get_notes_generation_config
from agents.research_agent import build_research_prompt, get_research_generation_config


def test_research_prompt_builder_returns_non_empty_prompt():
    prompt = build_research_prompt("binary search trees")
    assert "binary search trees" in prompt
    assert prompt.strip()


def test_notes_prompt_builder_returns_non_empty_prompt():
    prompt = build_notes_prompt("operating systems")
    assert "operating systems" in prompt
    assert prompt.strip()


def test_doubt_prompt_builder_returns_non_empty_prompt():
    prompt = build_doubt_prompt("what is normalization", "DBMS")
    assert "what is normalization" in prompt
    assert "DBMS" in prompt
    assert prompt.strip()


def test_fast_mode_has_smaller_research_token_budget_than_deep_mode():
    fast = get_research_generation_config("fast")
    deep = get_research_generation_config("deep")
    assert fast["max_output_tokens"] < deep["max_output_tokens"]


def test_fast_mode_has_smaller_notes_token_budget_than_deep_mode():
    fast = get_notes_generation_config("fast")
    deep = get_notes_generation_config("deep")
    assert fast["max_output_tokens"] < deep["max_output_tokens"]


def test_fast_mode_has_smaller_doubt_token_budget_than_deep_mode():
    fast = get_doubt_generation_config("fast")
    deep = get_doubt_generation_config("deep")
    assert fast["max_output_tokens"] < deep["max_output_tokens"]
