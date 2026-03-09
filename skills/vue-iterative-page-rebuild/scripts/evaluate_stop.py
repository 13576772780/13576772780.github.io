#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate iterative-stop conditions")
    parser.add_argument("--history", default="scores.json", help="JSON array of global scores by round")
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument("--target", type=float, default=0.92)
    parser.add_argument("--min-improve", type=float, default=0.01)
    args = parser.parse_args()

    scores = json.loads(Path(args.history).read_text(encoding="utf-8"))
    if not isinstance(scores, list) or not scores:
        print("continue: no valid score history")
        return 0

    rounds = len(scores)
    latest = float(scores[-1])

    if latest >= args.target:
        print(f"stop: reached target score ({latest:.3f} >= {args.target:.3f})")
        return 0

    if rounds >= args.max_rounds:
        print(f"stop: reached max rounds ({rounds} >= {args.max_rounds})")
        return 0

    if rounds >= 3:
        improve1 = scores[-1] - scores[-2]
        improve2 = scores[-2] - scores[-3]
        if improve1 < args.min_improve and improve2 < args.min_improve:
            print(
                "stop: convergence detected "
                f"(last improvements {improve2:.3f}, {improve1:.3f} < {args.min_improve:.3f})"
            )
            return 0

    print("continue: keep iterating")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
