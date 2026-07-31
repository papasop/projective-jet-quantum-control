# Symmetric-Loss Filtration

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Reference implementation scaffold and deterministic audit suite for
**symmetric-loss filtration, projective-jet degeneracy, and response-fibre
descent**.

This repository packages the first reproducible experiment layer as importable
Python modules. The current codebase focuses on Landau-Ginzburg-Reynolds (LGR)
trace functionals for reasoning trajectories, while the project name and
theoretical README establish the broader projective-jet filtration architecture
for the next implementation stages.

---

## Overview

Symmetric-loss filtration studies when matched projective response jets force
successive even-order loss terms to become identical. In the quantum-control
formulation, the core claim is that matching only low-order derivatives can be
insufficient: geometric contractions of projective jet tensors can preserve
fourth-order error splits unless the matched jet order is lifted to the correct
degeneracy level.

The intended framework has three layers:

1. **Projective Loss Filtration Theorem**  
   Matching projective jet order `r` determines the first possible
   symmetrized loss split through
   `e(r) = 2 * ceil((r + 2) / 2)`.

2. **Symmetric-Loss Degeneracy Level `k`**  
   Matching through projective order `r = 2k - 1` forces common symmetric loss
   terms through `L_2, ..., L_2k`, so the leading non-common split moves to
   `O(||epsilon||^(2k+2))`.

3. **Response-Fibre Descent**  
   Once projective jets are matched, optimization can continue along the
   matched-response fibre to reduce the leading non-common coefficient
   `G_(2k+2)` without breaking the lower-order constraints.

| Level `k` | Matched Jet `r = 2k - 1` | Tensor Components | Common Loss Orders | Leading Error Split | Expected Slope |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `k=1` | `r=1` | `Z_1` | `L_2` | `L_4` | `~4` |
| `k=2` | `r=3` | `Z_1, Z_2, Z_3` | `L_2, L_4` | `L_6` | `~6` |
| `k=3` | `r=5` | `Z_1, ..., Z_5` | `L_2, L_4, L_6` | `L_8` | `~8` |

## Current Implementation

The repository currently includes a deterministic LGR experiment package:

- gzip-based complexity proxy `K(x)`
- instance order parameters `phi(x)`, `lambda_K`, and `h(x)`
- trajectory construction `phi(t)` from answer-step residuals
- LGR functionals `F2`, `F4`, and finite-difference gradients `G1..Gn`
- baseline and full LGR least-squares regression helpers
- a CLI with deterministic mock runs and optional OpenAI-backed runs
- unit tests that do not require network access

This is the first audit-friendly layer. The projective-chart engine,
Hamiltonian driven-qubit realization, and response-fibre descent solver are the
next implementation milestones.

## Installation

```bash
git clone https://github.com/papasop/symmetric-loss-filtration.git
cd symmetric-loss-filtration
python -m pip install -e ".[dev]"
```

Optional OpenAI-backed experiments require:

```bash
python -m pip install -e ".[openai]"
export OPENAI_API_KEY="..."
```

## Quick Start

Run the deterministic mock experiment:

```bash
slf-experiment --provider mock --out outputs/mock.csv
```

The legacy command name is also kept for compatibility:

```bash
lgr-experiment --provider mock --out outputs/mock.csv
```

Use the core metrics directly:

```python
from lgr_experiment import build_phi_t, lgr_functionals, measure_phi_x

problem = "If 3x + 5 = 20, what is x?"
answer = "Step 1: Subtract 5 to get 3x = 15. Step 2: Divide by 3. Final answer: x = 5."

stats = measure_phi_x(problem, answer)
phi_t = build_phi_t(answer)
lgr = lgr_functionals(phi_t, max_order=6)

print(stats["phi_x"])
print(lgr["F2"], lgr["G1"], lgr["G2"])
```

## OpenAI-Backed Runs

```bash
slf-experiment --provider openai --model gpt-4o-mini --out outputs/openai.csv
```

The CLI runs the bundled 30 reasoning tasks in both `FAST` and `CoT` modes,
saves raw rows to CSV, and prints baseline/LGR regression summaries.

## Reproducing Local Audits

```bash
pytest
PYTHONPATH=src python -m lgr_experiment.cli --provider mock --out outputs/mock.csv
```

Expected local status for the current implementation:

| Audit Target | Command | Status |
| --- | --- | --- |
| Core metric tests | `pytest` | Passing |
| Mock 30-task experiment | `slf-experiment --provider mock` | Passing after editable install |
| OpenAI run | `slf-experiment --provider openai` | Requires `OPENAI_API_KEY` |

## Response-Fibre Audit v1.3.1

This repository now includes the validated response-fibre exact-root descent
audit package under `scripts/standalone`, `docs`, and `results`.

At 192-bit Arb precision, the v1.3.1 run certifies:

| Gate | Result |
| --- | ---: |
| Parameter-dependent Krawczyk boxes | 640/640 |
| Shared chart endpoints | 9/9 |
| Exact endpoint root boxes | 11/11 |
| Consecutive endpoint steps with strict `L_6` descent | 10/10 |
| Consecutive endpoint steps certified over the common finite-error window | 2/10 |

The aggregate status remains
`EXACT_ROOT_STEPWISE_DESCENT_INCONCLUSIVE` because the stronger finite-error
window statement closes for only 2/10 endpoint steps. The endpoint-to-endpoint
sixth-order descent gate passes for all ten declared steps.

Compile the standalone audit:

```bash
python -m py_compile scripts/standalone/response_fibre_exact_root_descent_v1_3_1.py
```

Verify the frozen artifact checksums:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

See `docs/response_fibre_v1_3_1.md` for theorem-ready wording and
`results/response_fibre_v1_3_1/report.json` for the compact final report.

## Roadmap

- Add phase-invariant projective chart coordinates.
- Add symbolic symmetric-loss filtration checks for `k=1..3`.
- Add driven-qubit response maps and tensor audit fixtures.
- Add response-fibre tangent projection and descent experiments.
- Publish deterministic protocol digests for paper-level reproducibility.

## Citation

If you use this software or theoretical framework in research, cite the project
paper or preprint associated with symmetric-loss filtration once available.

```bibtex
@misc{li2026symmetriclossfiltration,
  title={Symmetric-Loss Filtration and Projective-Jet Degeneracy},
  author={Li, Y. Y. N.},
  year={2026},
  note={Software implementation and deterministic audit suite}
}
```

## License

Distributed under the MIT License.
