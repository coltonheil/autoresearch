# Blue Star Source Completeness Gate Rubric

Version: 1.0

## Primary Score

`candidate_score - baseline_score`, higher is better.

The scorer grades each baseline and candidate decision on a 100-point scale:

| Dimension | Weight |
|---|---:|
| Valid verdict and source-completeness state | 20 |
| Direct evidence coverage | 25 |
| Blocker/no-fit separation | 25 |
| Expected-label agreement where labels exist | 15 |
| Concrete next owner/action | 15 |

## Direct Evidence

Direct evidence must include source, locator, and summary. Filenames, graph
absence, previous labels, and partial indexes are discovery hints only.

## Regression Failures

Any of these force discard:

- unsupported final verdict count increases
- blocker-as-no-fit count increases
- direct evidence coverage decreases
- source-completeness state is missing from candidate rows
- false partner-referral positives increase
- candidate changes the scorer, rubric, or eval set during the run

## Keep/Discard Bands

- `keep`: delta >= 5.0 and no regression failure
- `discard`: delta < 5.0 or any regression failure
- `crash`: scorer cannot parse or evaluate the artifact
- `blocked`: eval labels or source artifacts are missing
