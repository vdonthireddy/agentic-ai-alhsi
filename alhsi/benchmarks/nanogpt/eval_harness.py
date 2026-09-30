"""Immutable Harness Evaluator for NanoGPT Benchmark.

This file is READ-ONLY for the agent. If modified, the Harness Anti-Tamper guard will fail the trial.
It runs the target training script, verifies validity, and outputs the objective metric.
"""

import json
import sys
import time

sys.dont_write_bytecode = True


def main():
    try:
        import train
    except Exception as e:
        sys.stderr.write(f"Failed to import target 'train.py': {e}\n")
        sys.exit(1)

    if not hasattr(train, "train"):
        sys.stderr.write("Target 'train.py' does not define required 'train()' function.\n")
        sys.exit(1)

    t0 = time.time()
    try:
        result = train.train()
    except Exception as e:
        sys.stderr.write(f"Runtime exception during train(): {e}\n")
        sys.exit(2)

    elapsed = time.time() - t0

    if not isinstance(result, dict) or "val_loss" not in result:
        sys.stderr.write("train() must return a dictionary containing 'val_loss'\n")
        sys.exit(3)

    val_loss = float(result["val_loss"])
    train_loss = float(result.get("train_loss", 0.0))
    tokens_per_sec = float(result.get("tokens_per_sec", 0.0))

    payload = {
        "val_loss": val_loss,
        "train_loss": train_loss,
        "tokens_per_sec": tokens_per_sec,
        "eval_time_sec": round(elapsed, 3),
    }

    # Output structured result line for the Harness
    print(f"\n__ALHSI_RESULT__ {json.dumps(payload)}")


if __name__ == "__main__":
    main()
