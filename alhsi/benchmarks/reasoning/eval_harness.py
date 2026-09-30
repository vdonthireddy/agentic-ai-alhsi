"""Immutable Harness Evaluator for Reasoning Benchmark Suite."""

import json
import sys
import time

sys.dont_write_bytecode = True

TEST_SUITE = [
    # Math sequences
    {"category": "math_sequence", "data": [2, 4, 6, 8], "expected": 10},
    {"category": "math_sequence", "data": [3, 9, 27], "expected": 81},
    {"category": "math_sequence", "data": [1, 1, 2, 3, 5], "expected": 8},
    {"category": "math_sequence", "data": [10, 20, 30], "expected": 40},
    # Balanced brackets
    {"category": "balanced_brackets", "data": "([])", "expected": True},
    {"category": "balanced_brackets", "data": "([)]", "expected": False},
    {"category": "balanced_brackets", "data": "((()))", "expected": True},
    {"category": "balanced_brackets", "data": "(()", "expected": False},
    {"category": "balanced_brackets", "data": "{[()]}", "expected": True},
    # Palindromes
    {"category": "longest_palindrome", "data": "babad", "expected": 3},
    {"category": "longest_palindrome", "data": "cbbd", "expected": 2},
    {"category": "longest_palindrome", "data": "racecar", "expected": 7},
]


def main():
    try:
        import prompt_solver
    except Exception as e:
        sys.stderr.write(f"Failed to import 'prompt_solver.py': {e}\n")
        sys.exit(1)

    if not hasattr(prompt_solver, "solve_reasoning_task"):
        sys.stderr.write("prompt_solver.py must export solve_reasoning_task(problem)\n")
        sys.exit(1)

    t0 = time.time()
    passed = 0
    total = len(TEST_SUITE)

    for item in TEST_SUITE:
        try:
            pred = prompt_solver.solve_reasoning_task(item)
            if pred == item["expected"]:
                passed += 1
        except Exception as e:
            sys.stderr.write(f"Error on problem {item}: {e}\n")

    accuracy = (passed / total) * 100.0
    elapsed = time.time() - t0

    payload = {
        "accuracy": round(accuracy, 2),
        "passed": passed,
        "total": total,
        "eval_time_sec": round(elapsed, 4),
    }

    print(f"\n__ALHSI_RESULT__ {json.dumps(payload)}")


if __name__ == "__main__":
    main()
