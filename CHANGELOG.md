# Changelog

All notable changes to the [LLM Multi-Round Coding Tournament](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament) are documented in this file.

This project has no formal releases or version tags. Changes are tracked by individual commits on the `main` branch.

---

## 2026-02-21 -- Licensing and Branding

### License Replaced with MIT + OpenAI/Anthropic Rider

The plain MIT license (added 2026-01-21) was replaced with a modified MIT license that adds a rider restricting use by OpenAI, Anthropic, their affiliates, and any parties acting on their behalf, unless Jeffrey Emanuel grants express written permission. The rider applies to the software and all derivative works.

- **Commit:** [`9ba2cda`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/9ba2cdab8018ebbf80412dd2a7c9b2ea396206bf) -- chore: update license to MIT with OpenAI/Anthropic Rider
- **File:** `LICENSE`

### GitHub Social Preview Image

A 1280x640 PNG social preview image (`gh_og_share_image.png`) was added for consistent link previews when sharing the repository URL on social media platforms.

- **Commit:** [`f08c858`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/f08c8580c6671855c968e9e4b575fa5c378c2246) -- chore: add GitHub social preview image (1280x640)
- **File:** `gh_og_share_image.png`

---

## 2026-02-11 -- Code Cleanup

### Dead Code Removal in Tournament Script

Two assigned-but-never-used variables were removed from the `Claude37_round_1` class in `fix_markdown_tables_tournament.py`:

- `header_row` (assigned from `lines[0]`, never referenced)
- `current_index` (initialized, never used in the loop)

No behavioral change. The expressions the variables depended on still execute correctly without the assignments.

- **Commit:** [`e5bed6f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/e5bed6fd502a0bc2b4e4c2f7c2a9571d7bb8cee9) -- Remove unused variables from markdown table fixer
- **File:** `fix_markdown_tables_tournament.py`

---

## 2026-01-21 -- Initial MIT License

Added a standard MIT License file. This was later superseded on 2026-02-21 by the MIT + OpenAI/Anthropic Rider version.

- **Commit:** [`897206f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/897206fd23f7c1cda2c53e0b583da5c6fde4fa70) -- Add MIT License
- **File:** `LICENSE`

---

## 2025-03-23 -- Project Launch

The entire project was created and published in a single day by Jeffrey Emanuel. Rather than listing commits in diff order, changes are grouped below by capability.

### Tournament Experiment Data (51 files, ~1.17 million lines)

The core of the repository: a complete record of a 5-round coding tournament where four LLMs competed on the problem of fixing invalid markdown tables extracted from SEC EDGAR filings via `html2text`. The four competing models were Claude 3.7 Sonnet, Grok3 (with thinking mode), o1-pro, and o3-mini-high.

**Tournament code**

- `fix_markdown_tables_tournament.py` -- A ~3,500-line Python file containing 20 classes (4 models x 5 rounds), each implementing a distinct markdown table fixing algorithm. Includes a main function that runs all 20 solutions against a test file and writes the results.

**Test input**

- `sample_10k_reformatted.md` -- A ~57,000-line markdown conversion of Entergy's 2020 10-K filing from SEC EDGAR, used as the shared test input for all solutions.

**Model responses (24 files across 6 directories)**

Each round directory (`round_0_responses/` through `round_5_responses/`) contains one response per model. Round 0 holds initial independent solutions; rounds 1-5 hold solutions produced after each model read all other models' code from the previous round.

- `round_N_responses/tournament_response__round_N__MODEL.md`

**Inter-round prompts (4 files)**

Unified prompt files for rounds 1-4 containing all previous-round solutions concatenated together, used as input for the next round.

- `markdown_table_prompt_response_comparison__round_[1-4].md`

**Output results (20 files)**

Fixed versions of the test 10-K filing produced by each model/round combination.

- `output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__MODEL_round_N.md`

- **Commit:** [`7efcc5f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/7efcc5f193e2a9f0607155d8a3918e2e8730f134) -- initial code upload

### Tournament Automation Script (added then extracted)

An `llm_tournament.py` automation script (~1,450 lines) was created to generalize the tournament process for arbitrary coding prompts. It used Andrew Ng's [`aisuite`](https://github.com/andrewyng/aisuite) package to orchestrate multi-model, multi-round tournaments, with features including:

- Prompt creation, response collection, and code extraction lifecycle management
- Support for multiple LLM providers through a unified API
- Structured directory hierarchy for tournament artifacts
- Automated test script generation and metrics tracking
- Error recovery, rate limiting, and intelligent caching of prior responses
- LLM-based code extraction (using Claude 3.7 Sonnet) instead of brittle regex parsing

The script was added in commit [`006847c`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/006847c254792d7f6ebedcc675dc8c0c88f7b6f7) and later removed from this repository and relocated to its own dedicated repository at [`Dicklesworthstone/llm-tournament`](https://github.com/Dicklesworthstone/llm-tournament) in commit [`656fda4`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/656fda4af7282315cf449d5518f569a037304833).

### Article / README with Full Analysis

The repository README began as a standalone article (`article__llm_multi_round_coding_tournament.md`) and evolved through multiple commits into a comprehensive write-up covering:

**Methodology description** -- How the tournament technique works: posing the same prompt to multiple models, then feeding each model all other models' responses, repeating across rounds to drive cross-pollination and convergence.

**Problem statement** -- The challenge of fixing invalid markdown tables from SEC EDGAR HTML-to-markdown conversions, chosen because it admits many valid approaches and has no single "correct" solution.

**Comprehensive results tables** -- Per-round, per-model tables showing response sizes (KB and line counts), links to response files, and links to output files for all 20 model/round combinations across rounds 0-5.

**Algorithm analysis** -- A detailed comparison matrix scoring each model/round on correctness, completeness, and sophistication (ranging from 65 to 95), with per-entry descriptions of approach, key features, and improvements over the prior round.

**Architecture decomposition** -- Identification of seven shared components across all implementations: table block identification, continuation line merging, table validation, pattern detection, row normalization, style preservation, and table reconstruction.

**Evolution trends and model strengths** -- Analysis of increasing sophistication, cross-pollination of ideas, convergence of approaches, and per-model characterization (Claude: comprehensive; Grok3: middle-ground; o1-pro: style preservation; o3-mini-high: conciseness).

**Theoretical essays** -- Extended discussion of why the technique works (cross-pollination, breaking out of local maxima, scaling beyond human feedback, emergent sophistication) and broader implications (evolutionary algorithms, cognitive diversity, reshaping software development, applications beyond code).

Key commits:

- [`42cbae7`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/42cbae7de410f5c6042a00870d00abba6bb168db) -- Renamed article to `README.md`
- [`ea15733`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/ea1573346550e80beadd3007325f1d311af7b6fb) -- Added results tables and model response links
- [`006847c`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/006847c254792d7f6ebedcc675dc8c0c88f7b6f7) -- Added automation documentation and conclusions
- [`656fda4`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/656fda4af7282315cf449d5518f569a037304833) -- Expanded analysis sections
- [`38710ff`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/38710ff3c429db9c869db8f55af9c6e22914ffbb) -- Major expansion: algorithm comparison matrix, architecture decomposition, evolution trends, theoretical essays
- [`d249330`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/d249330bff82e3423aee94965a55d5623af74754), [`4fcae2f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/4fcae2fc24762101d1605e49b4b343fecba0d4a5), [`6657668`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/6657668b2ae8d4619a1d5ac57d9d5e8c6d22c80d), [`b2fc4ba`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/b2fc4baeca83c1699c80b09d8380fa83aa3306f2), [`cd7d9de`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/cd7d9deea6944ff9eec28733ce1bf07351cc7174), [`1245e96`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/1245e96ea6e8cd86c65c7b0b1bcf4bf7a5dc448f), [`a7cc2fc`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/a7cc2fcfa0bf3eaeb4e105ccc32d7bad90f6c409), [`8a8e8f0`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/8a8e8f04a373cdb00357adaf9850e952b58c4ab6) -- Formatting, wording, and structural refinements

### Illustration

A WebP illustration (`llm_tournament_illustration.webp`, ~725 KB) was added and embedded at the top of the README as a visual hero image for the repository.

- **Commit:** [`a348d55`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/a348d55787d6e03101f67de7815f7bb910594dd9) -- illustration

---

## Repository Structure

```
llm_multi_round_coding_tournament/
  fix_markdown_tables_tournament.py     # 20 table-fixing classes (4 models x 5 rounds)
  sample_10k_reformatted.md             # Test input: SEC EDGAR 10-K filing in markdown
  llm_tournament_illustration.webp      # Repository illustration
  gh_og_share_image.png                 # GitHub social preview image
  LICENSE                               # MIT with OpenAI/Anthropic Rider
  README.md                             # Full article and analysis
  markdown_table_prompt_response_comparison__round_[1-4].md  # Unified prompts per round
  round_[0-5]_responses/                # Individual model responses per round
    tournament_response__round_N__MODEL.md
  output_results_for_each_round_and_model/  # Fixed test files per model/round
    sample_10k_reformatted__fixed_tables__MODEL_round_N.md
```

### Models in Tournament

| Model | Identifier | Notes |
|-------|-----------|-------|
| Claude 3.7 Sonnet | `claude-37-sonnet` | Highest-rated final solution; most consistent improvement across rounds |
| Grok3 | `grok3` | Used with thinking mode; no API at the time of the experiment |
| o1-pro | `o1-pro` | Strong focus on minimal-change style preservation |
| o3-mini-high | `o3-mini-high` | Most concise implementations |

### Related Repositories

- [llm-tournament](https://github.com/Dicklesworthstone/llm-tournament) -- The automated tournament runner (`llm_tournament.py`), originally created in this repo and later extracted to its own repository. Uses `aisuite` to orchestrate multi-model, multi-round coding tournaments on arbitrary prompts.
