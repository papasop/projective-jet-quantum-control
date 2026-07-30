# A-Landau-Ginzburg-Reynold

Reusable experiments for estimating Landau-Ginzburg-Reynolds (LGR)
functionals on reasoning traces.

The original repository history contained a notebook-style `LGR.py` script.
This version packages the same core ideas into importable, testable Python
modules:

- estimate instance complexity with gzip length
- derive `phi(x)`, `lambda_K`, and `h(x)`
- build trajectory signals `phi(t)` from answer steps
- compute LGR functionals `F2`, `F4`, and gradient terms `G1..Gn`
- compare simple baselines with linear LGR fits

## Install

```bash
python -m pip install -e ".[dev]"
```

Optional OpenAI-backed runs require:

```bash
python -m pip install -e ".[openai]"
export OPENAI_API_KEY="..."
```

## Run A Mock Experiment

The mock provider is deterministic and does not call external APIs. It is useful
for smoke tests and examples.

```bash
lgr-experiment --provider mock --out outputs/mock.csv
```

## Run With OpenAI

```bash
lgr-experiment --provider openai --model gpt-4o-mini --out outputs/openai.csv
```

The CLI runs the bundled 30 reasoning tasks in both `FAST` and `CoT` modes,
saves raw rows to CSV, and prints baseline/LGR regression summaries.

## Test

```bash
pytest
```
