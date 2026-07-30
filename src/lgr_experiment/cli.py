"""Command-line entry point for LGR experiments."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

import numpy as np

from .core import (
    DEFAULT_TASKS,
    ExperimentConfig,
    fit_linear_regression,
    run_experiment,
    summarize_by_mode,
)


def mock_provider(problem: str, mode: str) -> str:
    """Deterministic provider for local smoke runs."""

    if mode == "FAST":
        return "Final answer only."
    return (
        "Step 1: Identify the quantities in the problem. "
        "Step 2: Apply the relevant arithmetic relationship. "
        "Step 3: State the final answer."
    )


def openai_provider(model: str):
    """Create an OpenAI chat-completions provider."""

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the optional dependency with: pip install -e '.[openai]'") from exc

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for --provider openai")

    client = OpenAI(api_key=api_key)

    def call(problem: str, mode: str) -> str:
        if mode == "FAST":
            system = "Answer concisely with the final result. Avoid unnecessary explanation."
            max_tokens = 256
            temperature = 0.2
        else:
            system = "Solve the problem step by step with short numbered steps, then give the final answer."
            max_tokens = 512
            temperature = 0.4

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": problem},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    return call


def build_lgr_matrix(df, max_order: int):
    """Build a regression matrix from standard LGR feature columns."""

    feature_names = ["phi_x", "phi_x^2", "F2", "F4"]
    columns = [
        df["phi_x"].values,
        df["phi_x"].values**2,
        df["F2"].values,
        df["F4"].values,
    ]
    for order in range(1, max_order + 1):
        feature_names.append(f"G{order}")
        columns.append(df[f"G{order}"].values)
    return feature_names, np.vstack(columns).T


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LGR reasoning trace experiments.")
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--max-grad-order", type=int, default=6)
    parser.add_argument("--out", type=Path, default=Path("outputs/lgr_results.csv"))
    args = parser.parse_args(argv)

    provider = mock_provider if args.provider == "mock" else openai_provider(args.model)
    config = ExperimentConfig(
        experiment_name=f"{args.provider}_{args.model}",
        model=args.model if args.provider == "openai" else "mock",
        max_grad_order=args.max_grad_order,
    )

    df = run_experiment(DEFAULT_TASKS, provider, config)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    print(f"Saved {len(df)} rows to {args.out}")
    print("\nMode-wise means:")
    print(summarize_by_mode(df, max_order=args.max_grad_order).round(4))

    valid = df[df["T_sec"] > 0].copy()
    if len(valid) >= 2:
        y = valid["log2T"].values
        feature_names, x_lgr = build_lgr_matrix(valid, args.max_grad_order)
        _, r2_lgr, _ = fit_linear_regression(y, x_lgr, feature_names)
        _, r2_phi, _ = fit_linear_regression(y, valid[["phi_x"]].values, ["phi_x"])
        print("\nRegression R2:")
        print(f"phi_x baseline: {r2_phi:.4f}")
        print(f"LGR full:       {r2_lgr:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
