"""Matrix Multiplication & Attention Kernel - Target File (kernel.py)

The agent is invited to optimize this computational kernel for maximum GFLOPS
while preserving strict mathematical correctness (verified against NumPy reference).
"""

import numpy as np

# Kernel Configuration
BLOCK_SIZE = 16  # Tile size for cache optimization
UNROLL = 1       # Loop unrolling factor


def matmul_kernel(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute C = A @ B.
    
    Baseline: Standard partitioned block multiplication.
    Agent can implement:
      - Cache tiling / block matrix multiplication
      - Vectorized inner products
      - SIMD-friendly access patterns
    """
    M, K = A.shape
    K2, N = B.shape
    assert K == K2, "Dimension mismatch"

    C = np.zeros((M, N), dtype=A.dtype)

    # Baseline implementation
    # Notice: Naive row-by-row iteration with unoptimized block size
    for i in range(0, M, BLOCK_SIZE):
        i_end = min(i + BLOCK_SIZE, M)
        for j in range(0, N, BLOCK_SIZE):
            j_end = min(j + BLOCK_SIZE, N)
            for k in range(0, K, BLOCK_SIZE):
                k_end = min(k + BLOCK_SIZE, K)
                # Sub-block multiplication
                A_sub = A[i:i_end, k:k_end]
                B_sub = B[k:k_end, j:j_end]
                C[i:i_end, j:j_end] += A_sub @ B_sub

    return C
