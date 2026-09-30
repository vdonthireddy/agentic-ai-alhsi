"""Immutable Harness Evaluator for Matrix Kernel Benchmark.

Tests computational throughput (GFLOPS) and strict numerical correctness.
"""

import json
import sys
import time
import numpy as np

sys.dont_write_bytecode = True


def main():
    try:
        import kernel
    except Exception as e:
        sys.stderr.write(f"Failed to import 'kernel.py': {e}\n")
        sys.exit(1)

    if not hasattr(kernel, "matmul_kernel"):
        sys.stderr.write("kernel.py must export 'matmul_kernel(A, B)'\n")
        sys.exit(1)

    # Matrix dimensions for benchmarking
    M, K, N = 256, 256, 256
    np.random.seed(42)
    A = np.random.randn(M, K).astype(np.float32)
    B = np.random.randn(K, N).astype(np.float32)

    # Correctness check against reference
    ref_C = A @ B
    try:
        cand_C = kernel.matmul_kernel(A, B)
    except Exception as e:
        sys.stderr.write(f"Kernel execution crashed: {e}\n")
        sys.exit(2)

    if cand_C.shape != ref_C.shape:
        sys.stderr.write(f"Incorrect shape: expected {ref_C.shape}, got {cand_C.shape}\n")
        sys.exit(3)

    max_err = float(np.max(np.abs(cand_C - ref_C)))
    if max_err > 1e-3:
        sys.stderr.write(f"Correctness failure: max absolute error {max_err:.6f} exceeds 1e-3\n")
        sys.exit(4)

    # Benchmark throughput (warmup + timed runs)
    for _ in range(2):
        _ = kernel.matmul_kernel(A, B)

    iters = 10
    t0 = time.time()
    for _ in range(iters):
        _ = kernel.matmul_kernel(A, B)
    elapsed = (time.time() - t0) / iters

    # 2 * M * N * K operations
    flops = 2.0 * M * N * K
    gflops = (flops / elapsed) / 1e9

    payload = {
        "gflops": round(float(gflops), 3),
        "latency_ms": round(elapsed * 1000, 3),
        "max_err": round(max_err, 6),
        "matrix_dim": f"{M}x{K}x{N}",
    }

    print(f"\n__ALHSI_RESULT__ {json.dumps(payload)}")


if __name__ == "__main__":
    main()
