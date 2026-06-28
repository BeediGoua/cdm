import math

# Implements FIFA formula: P_new = P_before + I * (W - W_e)
# Where W is result (1 win, 0.5 draw, 0 loss), W_e is expected result
# Expected result W_e = 1 / (10^{-dr/400} + 1) where dr = P_before_A - P_before_B


def expected_result(points_a: float, points_b: float) -> float:
    dr = points_a - points_b
    we = 1.0 / (math.pow(10.0, -dr / 400.0) + 1.0)
    return we


def update_fifa_points(p_before: float, importance: float, w: float, w_e: float) -> float:
    return p_before + importance * (w - w_e)


def match_update(points_a: float, points_b: float, importance: float, score_a: int, score_b: int, neutral: bool = True):
    # determine W values
    if score_a > score_b:
        w_a = 1.0
        w_b = 0.0
    elif score_a == score_b:
        w_a = 0.5
        w_b = 0.5
    else:
        w_a = 0.0
        w_b = 1.0

    # expected results
    we_a = expected_result(points_a, points_b)
    we_b = 1.0 - we_a

    p_new_a = update_fifa_points(points_a, importance, w_a, we_a)
    p_new_b = update_fifa_points(points_b, importance, w_b, we_b)

    return p_new_a, p_new_b


if __name__ == "__main__":
    # simple CLI demo
    import argparse

    parser = argparse.ArgumentParser(description="Apply FIFA rating update for a single match")
    parser.add_argument("--a", type=float, required=True, help="Points team A before")
    parser.add_argument("--b", type=float, required=True, help="Points team B before")
    parser.add_argument("--imp", type=float, default=10.0, help="Match importance (I)")
    parser.add_argument("--sa", type=int, required=True, help="Score A")
    parser.add_argument("--sb", type=int, required=True, help="Score B")

    args = parser.parse_args()
    pa, pb = match_update(args.a, args.b, args.imp, args.sa, args.sb)
    print(f"Updated points: A {pa:.2f}, B {pb:.2f}")
