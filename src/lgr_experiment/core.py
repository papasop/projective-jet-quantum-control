"""Core LGR metrics and experiment runner."""

from __future__ import annotations

import gzip
import json
import math
import re
import time
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Mapping, Sequence

import numpy as np
import pandas as pd


DEFAULT_TASKS: List[str] = [
    "You have 5 apples. You give 2 to Alice and 1 to Bob, then buy 4 more. How many apples do you have now?",
    "If a train travels 120 kilometers in 1.5 hours, what is its average speed in kilometers per hour?",
    "A rectangle has length 8 and width 5. If the length is increased by 50% and the width is decreased by 20%, what is the new area?",
    "A store offers a 20% discount on a $50 item, then adds 10% tax on the discounted price. What is the final price?",
    "You flip a fair coin three times. What is the probability of getting exactly two heads?",
    "If 3x + 5 = 20, what is x?",
    "A class has 12 boys and 18 girls. What percentage of the class are girls?",
    "The sum of two numbers is 30 and their difference is 6. What are the two numbers?",
    "You invest $1000 at 5% simple annual interest. How much will you have after 3 years?",
    "If a car uses 8 liters of fuel to travel 120 km, how many liters are needed to travel 300 km?",
    "A tank can be filled by pipe A in 6 hours and by pipe B in 4 hours. If both pipes are used together, how long will it take to fill the tank?",
    "A worker is paid $15 per hour for the first 40 hours in a week and 1.5 times that rate for additional hours. If they worked 46 hours, what is their total pay?",
    "A store sells pencils at 3 for $1.20. How much will 10 pencils cost?",
    "A train leaves City A at 9:00 AM traveling at 80 km/h. Another train leaves City B at 10:00 AM traveling towards City A at 100 km/h. If the distance between the cities is 420 km, at what time do the trains meet?",
    "The average of five numbers is 12. If four of them are 10, 8, 15, and 11, what is the fifth number?",
    "A bag contains 5 red, 3 blue, and 2 green balls. One ball is drawn at random. What is the probability that it is not blue?",
    "If the perimeter of a square is 36 units, what is the area of the square?",
    "The ratio of cats to dogs in a shelter is 3:5. If there are 24 dogs, how many cats are there?",
    "A shop increases the price of an item by 25%, then later offers a 20% discount on the new price. What is the net percentage change from the original price?",
    "A recipe uses 3 cups of flour to make 12 cookies. How many cookies can be made with 5 cups of flour?",
    "In how many different ways can the letters of the word 'LEVEL' be arranged?",
    "Two consecutive integers have a product of 506. What are the integers?",
    "You roll two fair six-sided dice. What is the probability that the sum is 9?",
    "A book is sold at a 30% discount for $14. What was its original price?",
    "If 60% of a number is 48, what is the number?",
    "Three friends split a bill of $72 in the ratio 2:3:4. How much does each pay?",
    "A circular garden has radius 7 meters. What is its area in terms of pi?",
    "A car's value decreases by 20% each year. If its initial value is $25,000, what is its value after 2 years?",
    "A box contains 6 red and 4 blue balls. Two balls are drawn without replacement. What is the probability both are red?",
    "If y varies directly as x and y=18 when x=6, what is y when x=10?",
]


@dataclass(frozen=True)
class ExperimentConfig:
    """Parameters shared by an LGR run."""

    experiment_name: str = "lgr_30tasks"
    model: str = "mock"
    max_grad_order: int = 6
    modes: Sequence[str] = ("FAST", "CoT")


AnswerProvider = Callable[[str, str], str]


def gzip_len(text: str) -> int:
    """Return gzip-compressed byte length as a compact complexity proxy."""

    return len(gzip.compress(text.encode("utf-8"), compresslevel=9))


def measure_phi_x(problem: str, answer: str) -> Dict[str, float]:
    """Measure instance order parameters from a problem/answer pair."""

    k_problem = gzip_len(json.dumps({"problem": problem}, ensure_ascii=False))
    k_solution = gzip_len(
        json.dumps({"problem": problem, "answer": answer}, ensure_ascii=False)
    )
    lambda_k = max(0.0, (k_solution - k_problem) / max(k_problem, 1))
    phi_x = math.log1p(lambda_k)
    return {
        "K_problem": float(k_problem),
        "K_solution": float(k_solution),
        "lambda_K": float(lambda_k),
        "phi_x": float(phi_x),
        "h_x": float(1.0 - lambda_k),
    }


def split_steps(text: str, limit: int = 80) -> List[str]:
    """Split an answer into coarse reasoning steps."""

    cleaned = text.replace("**", " ").replace("__", " ").strip()
    if not cleaned:
        return [""]

    parts = re.split(r"\n+|(?<=[.!?])\s+", cleaned)
    steps = [part.strip() for part in parts if part.strip()]
    return steps[:limit] if steps else [cleaned]


def build_phi_t(answer: str) -> np.ndarray:
    """Build a normalized trace signal from incremental gzip residuals."""

    steps = split_steps(answer)
    prefix = ""
    previous = gzip_len(prefix)
    values: List[float] = []

    for step in steps:
        prefix = f"{prefix}\n{step}"
        current = gzip_len(prefix)
        values.append(float(max(0, current - previous)))
        previous = current

    arr = np.array(values, dtype=float)
    max_value = float(arr.max()) if arr.size else 0.0
    if max_value > 0:
        return arr / max_value
    return np.ones_like(arr)


def lgr_functionals(phi_t: np.ndarray, max_order: int = 6) -> Dict[str, float]:
    """Compute F2, F4, and finite-difference gradient functionals G1..Gn."""

    values = np.asarray(phi_t, dtype=float)
    result: Dict[str, float] = {
        "F2": float(np.mean(values**2)) if values.size else 0.0,
        "F4": float(np.mean(values**4)) if values.size else 0.0,
    }

    for order in range(1, max_order + 1):
        if values.size > order:
            diff = np.diff(values, order)
            result[f"G{order}"] = float(np.mean(diff**2))
        else:
            result[f"G{order}"] = 0.0

    return result


def run_experiment(
    tasks: Iterable[str],
    provider: AnswerProvider,
    config: ExperimentConfig | None = None,
) -> pd.DataFrame:
    """Run tasks through a provider and return row-level LGR measurements."""

    cfg = config or ExperimentConfig()
    rows: List[Mapping[str, object]] = []

    for task_id, problem in enumerate(tasks):
        for mode in cfg.modes:
            start = time.perf_counter()
            answer = provider(problem, mode)
            elapsed = time.perf_counter() - start

            phi_stats = measure_phi_x(problem, answer)
            phi_t = np.array([1.0], dtype=float) if mode == "FAST" else build_phi_t(answer)
            lgr = lgr_functionals(phi_t, max_order=cfg.max_grad_order)

            row: Dict[str, object] = {
                "experiment": cfg.experiment_name,
                "model": cfg.model,
                "mode": mode,
                "task_id": task_id,
                "problem": problem,
                "answer": answer,
                "T_sec": elapsed,
                "log2T": math.log2(elapsed) if elapsed > 0 else float("-inf"),
                "phi_t_len": int(len(phi_t)),
                "phi_t_mean": float(phi_t.mean()) if phi_t.size else 0.0,
            }
            row.update(phi_stats)
            row.update(lgr)
            rows.append(row)

    return pd.DataFrame(rows)


def summarize_by_mode(df: pd.DataFrame, max_order: int = 6) -> pd.DataFrame:
    """Return mode-wise mean statistics for common LGR columns."""

    columns = ["T_sec", "phi_x", "lambda_K", "h_x", "phi_t_len", "F2", "F4"]
    columns.extend(f"G{order}" for order in range(1, max_order + 1))
    present = [column for column in columns if column in df.columns]
    return df.groupby("mode")[present].mean()


def fit_linear_regression(
    y: np.ndarray, x: np.ndarray, feature_names: Sequence[str]
) -> tuple[Dict[str, float], float, np.ndarray]:
    """Fit least-squares linear regression and return coefficients, R2, predictions."""

    if x.ndim != 2:
        raise ValueError("x must be a 2D feature matrix")
    if x.shape[1] != len(feature_names):
        raise ValueError("feature_names must match the feature count")
    if x.shape[0] != y.shape[0]:
        raise ValueError("x and y must have the same row count")

    design = np.hstack([x, np.ones((x.shape[0], 1))])
    names = list(feature_names) + ["const"]
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    y_pred = design @ coef
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {name: float(value) for name, value in zip(names, coef)}, r2, y_pred
