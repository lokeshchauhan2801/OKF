from pathlib import Path
from unittest.mock import patch
import json
import os

import pytest

from demo.assistant import (
    Concept,
    ask_deepseek,
    build_messages,
    load_concepts,
    retrieve_concepts,
)

ROOT = Path(__file__).resolve().parents[1]


def test_loads_official_acme_bundle_as_okf_concepts():
    concepts = load_concepts(ROOT / "bundles" / "acme_retail")

    assert concepts
    assert any(concept.title == "Revenue" for concept in concepts)
    assert all(concept.frontmatter.get("type") for concept in concepts)


def test_retrieval_prioritizes_matching_metric():
    concepts = load_concepts(ROOT / "bundles" / "acme_retail")

    matches = retrieve_concepts("How is revenue calculated?", concepts)

    assert matches
    assert matches[0].title == "Revenue"


def test_retrieval_returns_no_matches_for_empty_query_terms():
    concept = Concept(
        concept_id="sample",
        title="Sample",
        description="",
        relative_path="sample.md",
        body="",
        frontmatter={"type": "Reference"},
    )

    assert retrieve_concepts("the and is", [concept]) == []


def test_prompt_includes_source_labels_and_grounding_rule():
    concept = load_concepts(ROOT / "bundles" / "acme_retail")[0]

    messages = build_messages("What does this say?", [concept])

    assert "only the OKF excerpts" in messages[0]["content"]
    assert "[C1]" in messages[1]["content"]
    assert concept.relative_path in messages[1]["content"]


def test_deepseek_request_uses_configured_model_and_returns_answer():
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps(
                {"choices": [{"message": {"content": "Answer [C1]."}}]}
            ).encode()

    concept = load_concepts(ROOT / "bundles" / "acme_retail")[0]
    with patch.dict(os.environ, {"LLM_PROVIDER": "deepseek", "LLM_MODEL": "deepseek-chat"}):
        with patch("demo.assistant.urlopen", return_value=FakeResponse()) as mocked:
            answer = ask_deepseek("Question?", [concept], api_key="test-key")

    assert answer == "Answer [C1]."
    request = mocked.call_args.args[0]
    assert request.full_url == "https://api.deepseek.com/chat/completions"
    assert request.get_header("Authorization") == "Bearer test-key"
    assert json.loads(request.data)["model"] == "deepseek-chat"


def test_deepseek_requires_api_key():
    with patch.dict(os.environ, {"LLM_PROVIDER": "deepseek"}, clear=True):
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            ask_deepseek("Question?", [])
