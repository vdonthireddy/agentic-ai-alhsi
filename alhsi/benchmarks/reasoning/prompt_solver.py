"""Reasoning Agent Pipeline - Target File (prompt_solver.py)

The agent optimizes prompt strategy, chain-of-thought verification, and heuristic search
to maximize accuracy on algorithmic and logical reasoning challenges.
"""

from typing import Dict, Any, List

# Pipeline Configuration
PROMPT_STRATEGY = "direct"  # "direct", "chain_of_thought", "plan_and_solve", "self_consistency"
ENABLE_SANITY_CHECK = False
TEMPERATURE_HEURISTIC = 0.7


def solve_reasoning_task(problem: Dict[str, Any]) -> Any:
    """Solve an algorithmic reasoning puzzle.
    
    Baseline: Naive greedy heuristic without verification.
    Agent can implement:
      - Multi-step decomposition
      - Edge-case verification
      - Backtracking search
    """
    category = problem.get("category")
    data = problem.get("data")

    if category == "math_sequence":
        # Predict next number
        # Baseline only checks arithmetic progression
        seq = data
        if len(seq) >= 2:
            diff = seq[1] - seq[0]
            # Baseline fails on geometric or fibonacci sequences
            if PROMPT_STRATEGY == "chain_of_thought":
                # Check geometric
                if seq[0] != 0 and (seq[1] / seq[0]) == (seq[2] / seq[1]):
                    ratio = seq[1] // seq[0]
                    return seq[-1] * ratio
                # Check fibonacci-like
                if len(seq) >= 3 and seq[2] == seq[1] + seq[0]:
                    return seq[-1] + seq[-2]
            return seq[-1] + diff
        return 0

    elif category == "balanced_brackets":
        # Check if parentheses/brackets are balanced
        text = str(data)
        if PROMPT_STRATEGY in ("chain_of_thought", "plan_and_solve"):
            stack = []
            matching = {')': '(', ']': '[', '}': '{'}
            for char in text:
                if char in matching.values():
                    stack.append(char)
                elif char in matching.keys():
                    if not stack or stack[-1] != matching[char]:
                        return False
                    stack.pop()
            return len(stack) == 0
        else:
            # Baseline: naive counting that fails on nested order like "([)]"
            return text.count("(") == text.count(")") and text.count("[") == text.count("]")

    elif category == "longest_palindrome":
        # Find length of longest palindromic substring
        s = str(data)
        if not s:
            return 0
        if PROMPT_STRATEGY in ("chain_of_thought", "plan_and_solve", "self_consistency"):
            max_len = 1
            for i in range(len(s)):
                # odd
                l, r = i, i
                while l >= 0 and r < len(s) and s[l] == s[r]:
                    max_len = max(max_len, r - l + 1)
                    l -= 1
                    r += 1
                # even
                l, r = i, i + 1
                while l >= 0 and r < len(s) and s[l] == s[r]:
                    max_len = max(max_len, r - l + 1)
                    l -= 1
                    r += 1
            return max_len
        else:
            # Baseline naive assumption
            return 1 if len(s) > 0 else 0

    return None
