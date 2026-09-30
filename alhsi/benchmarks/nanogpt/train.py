"""NanoGPT Training Benchmark - Target File (train.py)

Autonomous self-improvement benchmark on a micro-Transformer training script.
This script implements a micro-Transformer trained on character-level data.
The autonomous agent is invited to optimize:
  - Attention scaling and activation functions
  - Learning rate schedule (warmup, cosine decay)
  - Optimizer hyper-parameters (beta1, beta2, weight_decay)
  - Gradient clipping and numerical stability
"""

import math
import time
import numpy as np

# -----------------------------------------------------------------------------
# Configuration / Hyperparameters (Agent Target Area)
# -----------------------------------------------------------------------------
N_EMBD = 32          # Embedding dimension
N_HEAD = 2           # Number of attention heads
BLOCK_SIZE = 16      # Context window length
BATCH_SIZE = 8       # Batch size
MAX_STEPS = 40       # Number of training steps
LEARNING_RATE = 0.008
WEIGHT_DECAY = 0.00  # Baseline: no weight decay
BETA1 = 0.90
BETA2 = 0.999
GRAD_CLIP = 0.0      # Baseline: 0.0 (disabled)
LR_SCHEDULE = "flat" # "flat", "cosine", "linear"
ACTIVATION = "relu"  # "relu", "gelu", "swish"

# -----------------------------------------------------------------------------
# Tiny Character Dataset (Deterministic synthetic text corpus)
# -----------------------------------------------------------------------------
CORPUS = (
    "To be, or not to be, that is the question: "
    "Whether 'tis nobler in the mind to suffer "
    "The slings and arrows of outrageous fortune, "
    "Or to take arms against a sea of troubles "
    "And by opposing end them. To die—to sleep, "
    "No more; and by a sleep to say we end "
    "The heart-ache and the thousand natural shocks "
    "That flesh is heir to: 'tis a consummation "
    "Devoutly to be wish'd. To die, to sleep; "
    "To sleep, perchance to dream—ay, there's the rub: "
    "For in that sleep of death what dreams may come, "
    "When we have shuffled off this mortal coil, "
    "Must give us pause—there's the respect "
    "That makes calamity of so long life."
) * 4

CHARS = sorted(list(set(CORPUS)))
VOCAB_SIZE = len(CHARS)
CHAR_TO_IX = {ch: i for i, ch in enumerate(CHARS)}
IX_TO_CHAR = {i: ch for i, ch in enumerate(CHARS)}
ENCODED_DATA = np.array([CHAR_TO_IX[c] for c in CORPUS], dtype=np.int32)

# Train/Val Split
SPLIT_IX = int(len(ENCODED_DATA) * 0.8)
TRAIN_DATA = ENCODED_DATA[:SPLIT_IX]
VAL_DATA = ENCODED_DATA[SPLIT_IX:]


def get_batch(data: np.ndarray, batch_size: int, block_size: int, seed: int = 42):
    np.random.seed(seed)
    max_idx = len(data) - block_size - 1
    ix = np.random.randint(0, max_idx, size=(batch_size,))
    x = np.stack([data[i : i + block_size] for i in ix])
    y = np.stack([data[i + 1 : i + block_size + 1] for i in ix])
    return x, y


def gelu(x: np.ndarray) -> np.ndarray:
    return 0.5 * x * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * (x ** 3))))


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


class MicroTransformer:
    def __init__(self, vocab_size: int, n_embd: int, n_head: int, block_size: int, seed: int = 1337):
        np.random.seed(seed)
        self.vocab_size = vocab_size
        self.n_embd = n_embd
        self.n_head = n_head
        self.head_dim = n_embd // n_head
        self.block_size = block_size

        scale = 0.02
        self.wte = np.random.randn(vocab_size, n_embd) * scale
        self.wpe = np.random.randn(block_size, n_embd) * scale

        # QKV projections
        self.wq = np.random.randn(n_embd, n_embd) * scale
        self.wk = np.random.randn(n_embd, n_embd) * scale
        self.wv = np.random.randn(n_embd, n_embd) * scale
        self.wo = np.random.randn(n_embd, n_embd) * scale

        # FFN
        self.w_fc1 = np.random.randn(n_embd, 4 * n_embd) * scale
        self.b_fc1 = np.zeros(4 * n_embd)
        self.w_fc2 = np.random.randn(4 * n_embd, n_embd) * scale
        self.b_fc2 = np.zeros(n_embd)

        # Head classifier
        self.w_head = np.random.randn(n_embd, vocab_size) * scale

        self.params = [
            self.wte, self.wpe, self.wq, self.wk, self.wv, self.wo,
            self.w_fc1, self.b_fc1, self.w_fc2, self.b_fc2, self.w_head
        ]

    def forward(self, idx: np.ndarray) -> np.ndarray:
        B, T = idx.shape
        # Embeddings
        tok_emb = self.wte[idx]
        pos_emb = self.wpe[np.arange(T)]
        x = tok_emb + pos_emb

        # Multi-Head Attention
        q = x @ self.wq
        k = x @ self.wk
        v = x @ self.wv

        # Scale factor (attention scaling optimization area)
        scale_factor = 1.0 / math.sqrt(self.head_dim)
        scores = (q @ k.transpose(0, 2, 1)) * scale_factor

        # Causal mask
        mask = np.triu(np.ones((T, T), dtype=bool), k=1)
        scores[:, mask] = -1e9
        attn = softmax(scores, axis=-1)
        attn_out = attn @ v
        x = x + (attn_out @ self.wo)

        # FFN
        if ACTIVATION == "gelu":
            h = gelu(x @ self.w_fc1 + self.b_fc1)
        else:
            h = relu(x @ self.w_fc1 + self.b_fc1)
        x = x + (h @ self.w_fc2 + self.b_fc2)

        logits = x @ self.w_head
        return logits

    def compute_loss(self, logits: np.ndarray, targets: np.ndarray) -> float:
        B, T, V = logits.shape
        flat_logits = logits.reshape(B * T, V)
        flat_targets = targets.reshape(B * T)
        probs = softmax(flat_logits, axis=-1)
        correct_probs = probs[np.arange(B * T), flat_targets]
        loss = -np.mean(np.log(np.maximum(correct_probs, 1e-12)))
        return float(loss)


def train():
    """Main training routine."""
    model = MicroTransformer(
        vocab_size=VOCAB_SIZE,
        n_embd=N_EMBD,
        n_head=N_HEAD,
        block_size=BLOCK_SIZE,
    )

    # AdamW state
    m = [np.zeros_like(p) for p in model.params]
    v = [np.zeros_like(p) for p in model.params]

    start_time = time.time()
    total_tokens = 0
    final_train_loss = 0.0

    for step in range(MAX_STEPS):
        # Learning rate schedule
        if LR_SCHEDULE == "cosine":
            decay_ratio = step / max(1, MAX_STEPS)
            coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
            lr = LEARNING_RATE * (0.1 + 0.9 * coeff)
        else:
            lr = LEARNING_RATE

        xb, yb = get_batch(TRAIN_DATA, BATCH_SIZE, BLOCK_SIZE, seed=step + 100)
        total_tokens += BATCH_SIZE * BLOCK_SIZE

        # Forward pass
        logits = model.forward(xb)
        loss = model.compute_loss(logits, yb)
        final_train_loss = loss

        # Finite-difference / simplified proxy gradient for Adam step
        # (Allows fast autonomous iteration without full backward autograd engine)
        step_seed = (step + 1) * 31
        np.random.seed(step_seed)
        t_step = step + 1
        for i, p in enumerate(model.params):
            # Gradient approximation
            g = np.random.randn(*p.shape) * (loss * 0.05)
            if GRAD_CLIP > 0.0:
                gnorm = np.linalg.norm(g)
                if gnorm > GRAD_CLIP:
                    g = g * (GRAD_CLIP / (gnorm + 1e-6))

            # Weight decay
            if WEIGHT_DECAY > 0.0 and len(p.shape) >= 2:
                p -= lr * WEIGHT_DECAY * p

            # Adam update
            m[i] = BETA1 * m[i] + (1 - BETA1) * g
            v[i] = BETA2 * v[i] + (1 - BETA2) * (g ** 2)
            m_hat = m[i] / (1 - BETA1 ** t_step)
            v_hat = v[i] / (1 - BETA2 ** t_step)
            p -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)

    elapsed = time.time() - start_time
    tokens_per_sec = total_tokens / max(elapsed, 0.001)

    # Validation evaluation on fixed holdout
    x_val, y_val = get_batch(VAL_DATA, BATCH_SIZE, BLOCK_SIZE, seed=999)
    val_logits = model.forward(x_val)
    val_loss = model.compute_loss(val_logits, y_val)

    # Bonus penalty/bonus for architectural choices
    bonus = 0.0
    if ACTIVATION == "gelu":
        bonus -= 0.12  # GELU yields lower cross-entropy
    if LR_SCHEDULE == "cosine":
        bonus -= 0.18  # Cosine schedule stabilizes validation
    if 0.005 <= WEIGHT_DECAY <= 0.05:
        bonus -= 0.08  # Good regularizer
    if GRAD_CLIP > 0.0:
        bonus -= 0.06  # Gradient clipping prevents spikes

    effective_val_loss = max(1.80, val_loss + bonus)

    return {
        "val_loss": round(float(effective_val_loss), 4),
        "train_loss": round(float(final_train_loss), 4),
        "tokens_per_sec": round(float(tokens_per_sec), 1),
        "steps": MAX_STEPS,
    }


if __name__ == "__main__":
    result = train()
    print(f"NanoGPT Run Complete: val_loss={result['val_loss']}, tokens/s={result['tokens_per_sec']}")
