# US legal software radar

An initial market profile for English-language discovery of software for US law firms and in-house legal teams. The reports track products and emerging terms, not legal advice.

## Run

```powershell
.\run-legal-radar.cmd
```

Outputs: `report-legal-us.md`, `report-legal-us.json`. Separate history: `state/legal-us/`. Edit the committed `config.legal-us.json` to customize the profile.

GitHub's anonymous search quota is small. If you see a rate-limit error and have already signed into the GitHub CLI, set a session-only token before running (never commit it):

```powershell
$env:GITHUB_TOKEN = gh auth token
.\run-legal-radar.cmd
```

Free default sources:

- [LawNext RSS](https://www.lawnext.com/feed): legal technology publisher.
- [Clio blog RSS](https://www.clio.com/blog/feed/): vendor perspective on law firm software and operations.
- GitHub searches for legal, legaltech and ediscovery in repository names, descriptions and topics.

Topics: research and drafting; contracts and in-house legal; litigation and e-discovery; law firm operations. Feed titles are filtered by topic words. The first run establishes feed baselines; later runs include newly seen matching articles with source links and candidate product names. A newly seen article or repository is a lead to review, not proof of a launch or rising US demand.

Legal repositories use a 90-day discovery window, at least five stars, and either two stars per day since creation or five stars gained since the previous snapshot. Search results are deduplicated across queries, then filtered using configurable inclusion and exclusion patterns. The initial English profile excludes descriptions containing Chinese characters or explicit Italian-market terms; this heuristic can miss multilingual products. These thresholds are starting hypotheses for a smaller market. GitHub searches are global: the US target comes from publisher selection and the configured country for optional demand data, not a geographic repository filter. US availability still needs manual verification. Commercial products may have no public repository; RSS coverage is deliberately small and should be expanded.

The default profile skips X, Hugging Face, sitemaps, paid domain discovery, Search Console, review and keyword volumes. Name scoring is disabled until a model is configured. It makes no paid AIsa requests by default. No schedule or email is enabled.

## Use another model API

Set these locally; the base URL must include the provider's API version path (for example a URL ending in `/v1`). The adapter appends `/chat/completions`.

```powershell
$env:RADAR_LLM_BASE_URL = '<provider API base URL>'
$env:RADAR_LLM_API_KEY = '<provider key>'
```

Set `judge.model` in `config.legal-us.json` to a model supported by your provider. Requests use the common chat-completions schema with `temperature`, `max_tokens`, system/user messages and text responses; providers with a different schema need another adapter. Model usage is paid according to your provider and is not included in the report's AIsa data-spend total.

These credentials are separate from `AISA_API_KEY`. Without the custom base URL, the original AIsa model endpoint remains the fallback. The AIsa router still supplies X, search volumes, review Trends and domain data when enabled; replacing the model endpoint does not replace those data sources. Do not enable the keyword table assuming a model API alone is sufficient.

## Development

```powershell
.\.venv\Scripts\python.exe -m pip install pytest markdown
.\.venv\Scripts\python.exe -X utf8 -m pytest -q tests
```

The fork retains the upstream MIT license and attribution. GitHub Actions still uses the upstream configuration and remains opt-in; configure a legal-specific workflow before scheduling this profile.
