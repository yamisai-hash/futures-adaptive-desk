# The Learning Loop — Futures Adaptive Desk

The headline feature isn't trading. It's measuring whether the scoring model is
worth anything **before** trusting it.

## The question

If a setup is scored 0-100 at signal time, do higher scores actually produce
better realized outcomes (R multiple, win rate)?

## How it's answered (`src/score_validator.py`)

1. Each closed paper trade stores the confluence score it had **at signal
   time** plus its realized R.
2. Trades are bucketed by score band (0-39, 40-49, 50-59, 60-69, 70-100).
3. Per bucket: win rate and average R.
4. Across all trades: a Spearman **rank correlation** between score and R.
5. An honest verdict: `PREDICTIVE` / `PARTIALLY_PREDICTIVE` / `NOT_PREDICTIVE` /
   `INCONCLUSIVE` (small sample).

## Why it matters

A backtest that "looks profitable" is easy to fake yourself into. A
score->outcome correlation that comes out **negative or flat** tells you the
truth: the current factors aren't ranking trades well yet. See
`demo_data/sample_score_validation.json` for an example read-out
(`PARTIALLY_PREDICTIVE`, rank corr -0.58 at n=20).

## The governor (summarized)

A self-tuning governor may *recommend* weight changes (e.g. "reduce
`session_blocked`, increase `economic_event_guard`") but applies them slowly and
only with enough samples — it prefers collecting data over over-fitting a
handful of trades. The recommendations are surfaced; they are not blindly
applied.
