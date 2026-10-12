# Local Windows setup

Installed with Python 3.13 in `.venv`. The core uses the standard library; optional mail and Search Console packages are not installed.

Run from PowerShell:

```powershell
.\run-radar.cmd
```

This reads the free Hugging Face and GitHub signals and writes `report.md` and `report.json`. State and snapshots live in `state`. The first Hugging Face run builds a baseline; later runs detect changes. Internet access is required.

`config.json` is copied from the upstream example. Edit accounts, topics, known terms and sitemaps there. Default runs skip example sitemaps and paid features.

For the full report, configure your AIsa key in your local PowerShell session, then run:

```powershell
$env:AISA_API_KEY = '<your-key>'
.\run-radar.cmd daily --skip newsites --out report.md
```

Full runs use paid API calls. The upstream README documents prices and optional integrations. The new-sites signal is skipped because the upstream README currently reports an API issue. Before enabling example sitemaps, check each site's robots.txt and crawl delay as instructed upstream.

UTF-8 mode is enabled by the launcher for Windows report compatibility. No recurring schedule or email delivery is configured.
