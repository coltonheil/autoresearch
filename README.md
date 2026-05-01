# autoresearch for business optimization

This repository is a fork of [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and preserves its core autoresearch loop pattern while adapting it for business optimization work.

Instead of iterating on ML training code, this fork organizes repeatable keep-or-discard loops for business surfaces like product page copy, ad creative, site performance, email, and SEO.

## Upstream pattern

The upstream project centers on a simple loop:
- change one thing
- measure the result
- keep the change if the score improves
- discard it if it does not
- repeat

This fork keeps that architecture, but swaps ML-specific files for domain-specific program instructions, fixed scoring rubrics, experiment logs, and a business-safe asset storage pattern outside the repo.

## Local canonical setup

Do not rebuild autoresearch from scratch. This repo is the canonical business
optimization fork on this Mac.

- Business loops live here: `~/repos/autoresearch`
- Apple Silicon ML training reference: `~/repos/autoresearch-mlx`
- Upstream reference: `https://github.com/karpathy/autoresearch`
- MLX reference fork: `https://github.com/trevin-creator/autoresearch-mlx`

Use the MLX reference only for Mac-native ML training experiments. Use this
business fork for product, ops, document-intelligence, bid-resolution, and other
scored agent loops.

For Codex runs, `/goal` should wrap a named autoresearch program. The
autoresearch harness remains the program/rubric/scorer/results layer.

## Repo-scoped layout

New loops must be scoped by the repo or business surface they improve:

```text
programs/<repo-slug>/<loop-slug>.md
rubrics/<repo-slug>/<loop-slug>.md
scripts/<repo_slug>/score_<loop_slug>.py
scripts/<repo_slug>/promote_<loop_slug>.py
results/<repo-slug>/<loop-slug>.tsv
~/.openclaw/workspace/outputs/autoresearch/<repo-slug>/<loop-slug>/
```

Examples:

- `programs/blue-star/bid-resolution.md`
- `rubrics/blue-star/bid-resolution.md`
- `scripts/blue_star/score_bid_resolution.py`
- `scripts/blue_star/promote_bid_resolution.py`
- `programs/heil-ginseng/packaging.md`

Older flat files may exist from earlier loops, but do not add new loops to the
flat namespace.

## Repository structure

```text
autoresearch/
├── README.md
├── programs/
│   ├── pdp-copy.md
│   ├── ad-creative.md
│   ├── blue-star/
│   │   └── bid-resolution.md
│   ├── heil-ginseng/
│   │   ├── packaging.md
│   │   └── packaging-visual-loop.md
│   ├── site-performance.md
│   ├── email.md
│   └── seo.md
├── rubrics/
│   ├── pdp-cro.md
│   ├── ad-creative-visual.md
│   ├── ad-creative-copy.md
│   ├── blue-star/
│   │   └── bid-resolution.md
│   ├── heil-ginseng/
│   │   ├── packaging-brand.md
│   │   └── packaging-visual.md
│   ├── email.md
│   ├── seo.md
│   └── site-performance.md
└── results/
    ├── pdp-copy.tsv
    ├── ad-creative.tsv
    ├── blue-star/
    │   └── bid-resolution.tsv
    ├── site-performance.tsv
    ├── email.tsv
    └── seo.tsv
```

## File categories

- `programs/` contains human-written agent instructions for each optimization loop. This is the business equivalent of the upstream `program.md`.
- `rubrics/` contains the fixed evaluation harness for each domain. Agents may read these, but only humans should edit them. This is the business equivalent of the upstream `prepare.py` role in defining stable evaluation context.
- `results/` contains experiment logs for each domain. This is the business equivalent of the upstream `results.tsv` workflow.

## Asset storage

Generated assets do not live in this repository. Store them in the workspace under:

`~/.openclaw/workspace/outputs/autoresearch/`

Example domains include:
- `outputs/autoresearch/pdp-copy/`
- `outputs/autoresearch/ad-creative/`
- `outputs/autoresearch/blue-star/bid-resolution/`
- `outputs/autoresearch/heil-ginseng/packaging/`
- `outputs/autoresearch/heil-ginseng/packaging-visual/`
- `outputs/autoresearch/site-performance/`
- `outputs/autoresearch/email/`
- `outputs/autoresearch/seo/`

## Strategy reference

For the full architecture, operating model, and domain strategy, see:

`~/.openclaw/workspace/AUTORESEARCH-STRATEGY.md`

## Credits

Credit to [karpathy/autoresearch](https://github.com/karpathy/autoresearch) for the original loop architecture this fork builds on.
