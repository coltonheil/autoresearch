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

This fork keeps that architecture, but swaps ML-specific files for domain-specific program instructions, fixed scoring rubrics, and experiment logs.

## Repository structure

```text
autoresearch/
├── README.md
├── programs/
│   ├── pdp-copy.md
│   ├── ad-creative.md
│   ├── site-performance.md
│   ├── email.md
│   └── seo.md
├── rubrics/
│   ├── pdp-cro.md
│   ├── ad-creative-visual.md
│   ├── ad-creative-copy.md
│   ├── email.md
│   ├── seo.md
│   └── site-performance.md
└── results/
    ├── pdp-copy.tsv
    ├── ad-creative.tsv
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
- `outputs/autoresearch/site-performance/`
- `outputs/autoresearch/email/`
- `outputs/autoresearch/seo/`

## Strategy reference

For the full architecture, operating model, and domain strategy, see:

`~/.openclaw/workspace/AUTORESEARCH-STRATEGY.md`

## Credits

Credit to [karpathy/autoresearch](https://github.com/karpathy/autoresearch) for the original loop architecture this fork builds on.
