import urllib.parse
from contextlib import contextmanager

from radar import aisa, breakout, config, feeds


def test_model_key_is_separate_from_data_key(monkeypatch):
    monkeypatch.setenv("RADAR_LLM_BASE_URL", "https://provider.example/v1/")
    monkeypatch.setenv("RADAR_LLM_API_KEY", "model-key")
    monkeypatch.setenv("AISA_API_KEY", "data-key")
    captured = {}

    def post(url, body, timeout, api_key=None):
        captured.update(url=url, key=api_key)
        return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(aisa, "_post", post)
    assert aisa.chat("model", "system", "user") == "ok"
    assert captured == {"url": "https://provider.example/v1/chat/completions", "key": "model-key"}
    assert aisa.key() == "data-key"


def test_market_queries_deduplicate_repositories(monkeypatch, cfg, tmp_path):
    cfg["breakout"].update(queries=["legal", "legaltech"])
    repo = {"full_name": "owner/legal", "stargazers_count": 10}
    requests = []
    scored = []

    def get(path):
        requests.append(urllib.parse.unquote(path))
        return {"items": [repo]}

    def score(repos, *args):
        scored.extend(repos)
        return []

    monkeypatch.setattr(breakout, "_get", get)
    monkeypatch.setattr(breakout, "score", score)
    result = breakout.breakouts(cfg, tmp_path)
    assert result["searched"] == 1 and scored == [repo]
    assert len(requests) == 2 and all("created:>=" in p for p in requests)


def test_feed_baseline_then_new_article_with_evidence(monkeypatch, cfg, tmp_path):
    cfg["feeds"] = {"publisher": {"url": "https://example.com/feed", "include": "software"}}
    payload = [b'<rss><channel><item><guid>1</guid><title>Old software</title></item></channel></rss>']

    @contextmanager
    def open_feed(*args, **kwargs):
        class Response:
            def read(self):
                return payload[0]
        yield Response()

    monkeypatch.setattr(feeds.urllib.request, "urlopen", open_feed)
    assert feeds.discover(cfg, tmp_path)["terms"] == []
    payload[0] = b'<rss><channel><item><guid>2</guid><title>LexPilot2 launches legal software</title><link>https://example.com/launch</link></item></channel></rss>'
    new = feeds.discover(cfg, tmp_path)
    assert "lexpilot2" in [r["term"] for r in new["terms"]]
    assert new["articles"][0]["url"] == "https://example.com/launch"
    assert feeds.discover(cfg, tmp_path)["terms"] == []


def test_atom_alternate_link():
    raw = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x</id><title>LexPilot2</title><link rel="self" href="https://example.com/api"/><link href="https://example.com/post"/></entry></feed>'
    assert feeds.parse(raw)[0]["url"] == "https://example.com/post"


def test_market_excludes_out_of_scope_repositories(monkeypatch, cfg, tmp_path):
    cfg["breakout"].update(include_pattern="legal", exclude_pattern="italia")
    repos = [{"full_name": "owner/legal", "description": "legal software", "stargazers_count": 10},
             {"full_name": "owner/italia", "description": "legal software", "stargazers_count": 10}]
    captured = []
    monkeypatch.setattr(breakout, "_get", lambda *args: {"items": repos})
    monkeypatch.setattr(breakout, "score", lambda rows, *args: captured.extend(rows) or [])
    result = breakout.breakouts(cfg, tmp_path)
    assert result["searched"] == 2 and result["matched"] == 1
    assert captured == repos[:1]


def test_legal_profile_has_no_paid_signals_by_default():
    from pathlib import Path
    profile = config.load(Path("config.legal-us.json"))
    assert {"x", "newsites", "review", "usecases"} <= set(profile["skip"])
    assert profile["judge"]["model"] == ""
    assert profile["market"]["country"] == "US"
