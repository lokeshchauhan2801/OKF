import json
from unittest.mock import patch

import pytest

from assistant import (
    ask_deepseek,
    find_concepts,
    format_inr,
    get_answer,
    load_concepts,
    load_sample_orders,
    messages_with_okf,
    messages_without_okf,
    parse_okf_file,
    run_query,
)


def test_parse_okf_file_splits_frontmatter_and_body():
    frontmatter, body = parse_okf_file("---\ntype: Metric\ntitle: X\n---\n# Definition\nText")
    assert frontmatter == {"type": "Metric", "title": "X"}
    assert body == "# Definition\nText"


def test_parse_okf_file_rejects_missing_type():
    with pytest.raises(ValueError):
        parse_okf_file("---\ntitle: X\n---\nbody")


def test_loads_acme_bundle():
    concepts = load_concepts()
    assert any(c.title == "Revenue" for c in concepts)
    assert all(c.frontmatter.get("type") for c in concepts)


def test_find_concepts_puts_revenue_first():
    matches = find_concepts("How is revenue calculated?", load_concepts())
    assert matches[0].title == "Revenue"


def test_find_concepts_skips_deprecated_files():
    matches = find_concepts("How was revenue defined before?", load_concepts())
    assert matches
    assert all(c.frontmatter.get("status") != "deprecated" for c in matches)


def test_find_concepts_returns_nothing_for_stopwords_only():
    assert find_concepts("the and is", load_concepts()) == []


def test_prompts_send_schema_but_never_the_order_rows():
    concept = load_concepts()[0]
    for messages in (messages_without_okf("What was revenue?"), messages_with_okf("Q?", [concept])):
        content = messages[1]["content"]
        assert "net_amount" in content
        assert "1001" not in content and "2026-03-15" not in content
    assert "OKF excerpts" not in messages_without_okf("Q?")[1]["content"]


def test_run_query_uses_local_orders():
    rows = run_query("SELECT order_id, net_amount FROM sales.orders WHERE order_status = 'delivered'")
    assert sorted(r["order_id"] for r in rows) == [1001, 1002, 1004]


def test_run_query_rejects_non_select():
    with pytest.raises(ValueError):
        run_query("DELETE FROM sales.orders")


def test_sample_orders_have_five_rows():
    assert len(load_sample_orders()) == 5


def test_with_okf_prompt_has_labelled_excerpts():
    concept = load_concepts()[0]
    content = messages_with_okf("Q?", [concept])[1]["content"]
    assert "[C1]" in content and concept.relative_path in content


def test_deepseek_request_and_answer():
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "Answer [C1]."}}]}).encode()

    with patch("assistant.urlopen", return_value=FakeResponse()) as mocked:
        answer = ask_deepseek([{"role": "user", "content": "Q?"}], api_key="test-key")

    assert answer == "Answer [C1]."
    request = mocked.call_args.args[0]
    assert request.full_url == "https://api.deepseek.com/chat/completions"
    assert request.get_header("Authorization") == "Bearer test-key"


def test_get_answer_runs_the_ai_query_locally():
    reply = {
        "sql": "SELECT order_id, net_amount FROM sales.orders "
               "WHERE order_status = 'delivered' AND delivered_on <= date('2026-11-18', '-30 days')",
        "kind": "amount",
        "summary": "Delivered orders past the return window.",
        "notes": ["n1"],
    }
    with patch("assistant.ask_deepseek", return_value=json.dumps(reply)):
        answer = get_answer([], api_key="test-key")
    assert answer.counted_ids == [1001, 1002]
    assert answer.total == 1300  # 500 + 800 from sample_orders.csv
    assert answer.notes == ["n1"]


def test_deepseek_requires_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
        ask_deepseek([])


def test_format_inr_uses_indian_grouping():
    assert format_inr(42000) == "₹42,000"
    assert format_inr(123456) == "₹1,23,456"
    assert format_inr(500) == "₹500"
