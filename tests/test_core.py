import numpy as np

from lgr_experiment import (
    ExperimentConfig,
    build_phi_t,
    fit_linear_regression,
    lgr_functionals,
    measure_phi_x,
    run_experiment,
    split_steps,
)


def test_measure_phi_x_returns_expected_keys():
    stats = measure_phi_x("What is 2+2?", "4")

    assert stats["K_solution"] >= stats["K_problem"]
    assert stats["lambda_K"] >= 0
    assert "phi_x" in stats
    assert "h_x" in stats


def test_split_steps_handles_sentences_and_newlines():
    steps = split_steps("Step 1: Add. Step 2: Return.\nFinal: 4")

    assert steps == ["Step 1: Add.", "Step 2: Return.", "Final: 4"]


def test_build_phi_t_is_normalized():
    phi_t = build_phi_t("Step 1: Add two values. Step 2: Return the result.")

    assert phi_t.size == 2
    assert np.isclose(phi_t.max(), 1.0)
    assert np.all(phi_t >= 0)


def test_lgr_functionals_for_linear_trace():
    result = lgr_functionals(np.array([0.0, 0.5, 1.0]), max_order=2)

    assert np.isclose(result["F2"], np.mean(np.array([0.0, 0.5, 1.0]) ** 2))
    assert np.isclose(result["G1"], 0.25)
    assert np.isclose(result["G2"], 0.0)


def test_run_experiment_uses_provider_without_network():
    def provider(problem, mode):
        return "4" if mode == "FAST" else "Step 1: Add. Final answer: 4."

    df = run_experiment(
        ["What is 2+2?"],
        provider,
        ExperimentConfig(experiment_name="test", model="mock", max_grad_order=3),
    )

    assert len(df) == 2
    assert set(df["mode"]) == {"FAST", "CoT"}
    assert {"F2", "F4", "G1", "G2", "G3"}.issubset(df.columns)


def test_fit_linear_regression_recovers_line():
    x = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([1.0, 3.0, 5.0, 7.0])

    coef, r2, pred = fit_linear_regression(y, x, ["x"])

    assert np.isclose(coef["x"], 2.0)
    assert np.isclose(coef["const"], 1.0)
    assert np.isclose(r2, 1.0)
    assert np.allclose(pred, y)
