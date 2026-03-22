# Changelog

All notable changes to the [LLM Multi-Round Coding Tournament](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament) are documented in this file.

This project has no formal releases or version tags. Changes are tracked by commit history on the `main` branch.

---

## 2026-02-21 -- License and Social Preview Updates

### License Updated to MIT with OpenAI/Anthropic Rider

The plain MIT license was replaced with a modified MIT license that includes an
OpenAI/Anthropic rider. The rider restricts use by OpenAI, Anthropic, their
affiliates, and any parties acting on their behalf, unless Jeffrey Emanuel grants
express written permission. The rider applies to the software and all derivative
works.

- **Commit:** [`9ba2cda`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/9ba2cdab8018ebbf80412dd2a7c9b2ea396206bf) -- chore: update license to MIT with OpenAI/Anthropic Rider

### GitHub Social Preview Image Added

A 1280x640 PNG social preview image was added for consistent link previews when
sharing the repository URL on social media.

- **Commit:** [`f08c858`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/f08c8580c6671855c968e9e4b575fa5c378c2246) -- chore: add GitHub social preview image (1280x640)
- **File:** `gh_og_share_image.png`

---

## 2026-02-11 -- Code Cleanup

### Removed Unused Variables from Markdown Table Fixer

Two assigned-but-never-used variables in `fix_markdown_tables_tournament.py` were
removed from the `Claude37_round_1` class:

- `header_row`: was assigned from `lines[0]` but never referenced
- `current_index`: was initialized but never used in the loop

No behavioral change; the expressions they depended on still execute correctly.

- **Commit:** [`e5bed6f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/e5bed6fd502a0bc2b4e4c2f7c2a9571d7bb8cee9) -- Remove unused variables from markdown table fixer
- **File:** `fix_markdown_tables_tournament.py`

---

## 2026-01-21 -- MIT License Added

Added an initial MIT License file (later superseded by the OpenAI/Anthropic rider
version on 2026-02-21).

- **Commit:** [`897206f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/897206fd23f7c1cda2c53e0b583da5c6fde4fa70) -- Add MIT License
- **File:** `LICENSE`

---

## 2025-03-23 -- Initial Project Creation

The entire project was created and published in a single day (March 23, 2025) by
Jeffrey Emanuel. The work proceeded through several phases on that day, documented
below in chronological order.

### Phase 1: Initial Code and Data Upload

The foundational commit introduced the core experiment: a multi-round coding
tournament where four LLMs (Claude 3.7 Sonnet, Grok3, o1-pro, o3-mini-high)
competed on the problem of fixing invalid markdown tables from SEC EDGAR filings.

Contents of the initial upload:

- **`fix_markdown_tables_tournament.py`** -- ~3,500-line Python file containing 20
  classes (4 models x 5 rounds), each implementing a different markdown table
  fixing algorithm produced during the tournament. Includes a main function that
  applies all 20 solutions to a test file.
- **`sample_10k_reformatted.md`** -- A ~57,000-line markdown file converted from an
  SEC EDGAR 10-K filing (Entergy, 2020) using `html2text`, used as the test input.
- **`article__llm_multi_round_coding_tournament.md`** -- The original article
  (later renamed to `README.md`).
- **`round_0_responses/`** through **`round_5_responses/`** -- Complete LLM
  responses for each round and model (24 files total). Round 0 contains the initial
  independent solutions; rounds 1-5 contain solutions after seeing all other models'
  code from the previous round.
- **`markdown_table_prompt_response_comparison__round_*.md`** -- The unified prompt
  files (rounds 1-4) that were given to each model, containing all previous-round
  solutions concatenated together.
- **`output_results_for_each_round_and_model/`** -- 20 output files showing the
  fixed version of `sample_10k_reformatted.md` produced by each model/round
  combination.

- **Commit:** [`7efcc5f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/7efcc5f193e2a9f0607155d8a3918e2e8730f134) -- initial code upload

### Phase 2: Article Renamed to README

The article file was renamed from `article__llm_multi_round_coding_tournament.md`
to `README.md` so it would render as the repository landing page on GitHub.

- **Commit:** [`42cbae7`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/42cbae7de410f5c6042a00870d00abba6bb168db) -- tweak

### Phase 3: Results Table and Response Links Added to README

Added the comprehensive results tables for all 6 rounds (0-5) with links to each
model's response files and output files. Added per-round metrics including response
size in KB, line counts, and output file sizes. Added links to round 0 response
files for all four models.

- **Commit:** [`ea15733`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/ea1573346550e80beadd3007325f1d311af7b6fb) -- added table and urls

### Phase 4: Tournament Automation Script

Added `llm_tournament.py`, a ~1,450-line Python script that automates the entire
multi-round tournament process using Andrew Ng's
[`aisuite`](https://github.com/andrewyng/aisuite) package. The script:

- Manages the full lifecycle of prompt creation, response collection, and code
  extraction across configurable numbers of rounds and models
- Supports multiple LLM providers through the aisuite API
- Creates a structured directory hierarchy for tournament artifacts
- Generates test scripts to evaluate the performance of each solution
- Handles error recovery and rate limiting
- Uses Claude 3.7 Sonnet to extract code from model responses (replacing hundreds
  of lines of regex-based extraction)

The README was also updated with documentation describing the automation approach,
noting the substitution of Google's Gemini model for Grok3 (which lacked an API at
the time), and the use of Claude 3.7 Sonnet to generate the automation code itself.

- **Commit:** [`006847c`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/006847c254792d7f6ebedcc675dc8c0c88f7b6f7) -- automated system

### Phase 5: Automation Script Moved to Separate Repository

The `llm_tournament.py` automation script was removed from this repository
and relocated to its own dedicated repository at
[`Dicklesworthstone/llm-tournament`](https://github.com/Dicklesworthstone/llm-tournament).
The README was expanded with additional analysis sections.

- **Commit:** [`656fda4`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/656fda4af7282315cf449d5518f569a037304833) -- tweaks

### Phase 6: Illustration Added

Added a WebP illustration (`llm_tournament_illustration.webp`, ~725 KB) and
embedded it at the top of the README.

- **Commit:** [`a348d55`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/a348d55787d6e03101f67de7815f7bb910594dd9) -- illustration

### Phase 7: Major README Expansion with Algorithm Analysis

The README received its largest single expansion. Added detailed algorithm analysis
including:

- A per-round, per-model comparison table with correctness, completeness, and
  sophistication scores for all 20 model/round combinations
- Key architecture components section (table block identification, continuation line
  merging, table validation, pattern detection, row normalization, style
  preservation, table reconstruction)
- Evolution trends analysis (increasing sophistication, cross-pollination, balance
  of concerns, convergence of approaches)
- Model strengths breakdown (Claude: comprehensive; Grok3: middle-ground; o1-pro:
  style preservation; o3-mini-high: conciseness)
- "Why LLM Multi-Round Tournaments Work So Well" essay covering cross-pollination of
  ideas, breaking out of local maxima, scaling beyond human feedback, and emergent
  sophistication
- Additional insights on evolutionary algorithms, cognitive diversity, reshaping
  software development practices, and applications beyond code

- **Commit:** [`38710ff`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/38710ff3c429db9c869db8f55af9c6e22914ffbb) -- Fix

### Phase 8: README Refinements

A series of small README formatting and wording adjustments:

- [`d249330`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/d249330bff82e3423aee94965a55d5623af74754) -- Formatting tweaks
- [`4fcae2f`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/4fcae2fc24762101d1605e49b4b343fecba0d4a5) -- Minor wording fix
- [`6657668`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/6657668b2ae8d4619a1d5ac57d9d5e8c6d22c80d) -- Condensed section formatting
- [`b2fc4ba`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/b2fc4baeca83c1699c80b09d8380fa83aa3306f2) -- Added content
- [`cd7d9de`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/cd7d9deea6944ff9eec28733ce1bf07351cc7174) -- Removed lines
- [`1245e96`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/1245e96ea6e8cd86c65c7b0b1bcf4bf7a5dc448f) -- Wording adjustments
- [`a7cc2fc`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/a7cc2fcfa0bf3eaeb4e105ccc32d7bad90f6c409) -- Wording adjustments
- [`8a8e8f0`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/commit/8a8e8f04a373cdb00357adaf9850e952b58c4ab6) -- Minor text fix

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
| Claude 3.7 Sonnet | `claude-37-sonnet` | Highest-rated final solution; most consistent improvement |
| Grok3 | `grok3` | Used with thinking mode; no API at the time |
| o1-pro | `o1-pro` | Strong focus on minimal-change style preservation |
| o3-mini-high | `o3-mini-high` | Most concise implementations |

### Related Repositories

- [llm-tournament](https://github.com/Dicklesworthstone/llm-tournament) -- The
  automated tournament runner (`llm_tournament.py`), originally created in this
  repo and later extracted to its own repository. Uses `aisuite` to orchestrate
  multi-model, multi-round coding tournaments on arbitrary prompts.
