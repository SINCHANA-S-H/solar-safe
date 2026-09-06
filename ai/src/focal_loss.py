"""
focal_loss.py
-------------
Numerically stable Focal Loss implementation for Keras.

Reference:
    Lin et al. (2017), "Focal Loss for Dense Object Detection"
    https://arxiv.org/abs/1708.02002

Design:
    - Subclasses tf.keras.losses.Loss for full Keras compatibility
    - Supports per-class alpha weighting (list or scalar)
    - Supports model serialization via get_config()
    - Clips probabilities to avoid log(0) instability
    - Works with categorical (one-hot) label mode
"""

import tensorflow as tf
import numpy as np


class FocalLoss(tf.keras.losses.Loss):
    """Focal loss for multi-class classification with categorical labels.

    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)

    Args:
        gamma (float): Focusing exponent. gamma=0 reduces to cross-entropy.
                       gamma=2.0 recommended (Lin et al., 2017).
        alpha (list or float): Per-class weighting factors. When a list, must
                               match the number of classes. Higher alpha weights
                               a class more in the loss. None means no weighting.
        name (str): Name of the loss.
        reduction: Keras loss reduction strategy.
    """

    def __init__(
        self,
        gamma: float = 2.0,
        alpha=None,
        name: str = "focal_loss",
        reduction=tf.keras.losses.Reduction.SUM_OVER_BATCH_SIZE,
    ):
        super().__init__(name=name, reduction=reduction)
        self.gamma = float(gamma)

        if alpha is None:
            self.alpha = None
        elif isinstance(alpha, (list, tuple, np.ndarray)):
            self.alpha = tf.constant(alpha, dtype=tf.float32)
        else:
            # Scalar alpha — apply uniformly
            self.alpha = float(alpha)

    def call(self, y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
        """Compute focal loss.

        Args:
            y_true: One-hot encoded labels, shape (batch, num_classes).
            y_pred: Softmax probabilities, shape (batch, num_classes).

        Returns:
            Per-sample focal loss tensor.
        """
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)

        # Clip predictions for numerical stability
        epsilon = tf.keras.backend.epsilon()   # ~1e-7
        y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)

        # Cross-entropy term: -log(p_t) where p_t = probability of true class
        cross_entropy = -y_true * tf.math.log(y_pred)   # (batch, num_classes)

        # Modulating factor: (1 - p_t)^gamma
        p_t = tf.reduce_sum(y_true * y_pred, axis=-1, keepdims=True)   # (batch, 1)
        modulating_factor = tf.pow(1.0 - p_t, self.gamma)              # (batch, 1)

        # Apply per-class alpha weighting
        if self.alpha is not None:
            if isinstance(self.alpha, tf.Tensor):
                # Per-class weights — broadcast across batch
                alpha_tensor = tf.reshape(self.alpha, [1, -1])   # (1, num_classes)
                alpha_weight = tf.reduce_sum(y_true * alpha_tensor, axis=-1, keepdims=True)
            else:
                alpha_weight = tf.constant(self.alpha, dtype=tf.float32)
        else:
            alpha_weight = 1.0

        # Focal loss: sum over classes (only true class contributes via y_true mask)
        focal = modulating_factor * cross_entropy                  # (batch, num_classes)
        loss = alpha_weight * tf.reduce_sum(focal, axis=-1)        # (batch,)

        return loss

    def get_config(self) -> dict:
        """Returns serializable config for model saving/loading."""
        config = super().get_config()
        config.update({
            "gamma": self.gamma,
            "alpha": (
                self.alpha.numpy().tolist()
                if isinstance(self.alpha, tf.Tensor)
                else self.alpha
            ),
        })
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


# -----------------------------------------------------------------------
# Convenience factory
# -----------------------------------------------------------------------
def get_focal_loss(gamma: float = 2.0, alpha=None) -> FocalLoss:
    """Factory for FocalLoss with standard defaults for SolarSafe.

    Default alpha = [0.4, 0.4, 0.2] means:
        Cell_Crack (idx 0): weight 0.4 — hard class, few confident correct samples
        Hotspot    (idx 1): weight 0.4 — hard class, small support
        Normal     (idx 2): weight 0.2 — easy class, dominant in correct predictions

    NOTE: Do NOT combine this alpha with sklearn compute_class_weight simultaneously.
    Choose one weighting strategy. V2-B uses focal loss alpha only (no class_weight dict).
    """
    if alpha is None:
        alpha = [0.4, 0.4, 0.2]
    return FocalLoss(gamma=gamma, alpha=alpha)


if __name__ == "__main__":
    # Quick sanity test
    import numpy as np

    print("Testing FocalLoss...")
    fl = FocalLoss(gamma=2.0, alpha=[0.4, 0.4, 0.2])

    y_true = tf.constant([[1, 0, 0], [0, 0, 1]], dtype=tf.float32)
    y_pred = tf.constant([[0.8, 0.1, 0.1], [0.1, 0.2, 0.7]], dtype=tf.float32)

    loss = fl(y_true, y_pred)
    print(f"  Focal loss (confident correct): {loss.numpy():.6f}")

    y_pred_hard = tf.constant([[0.4, 0.3, 0.3], [0.3, 0.3, 0.4]], dtype=tf.float32)
    loss_hard = fl(y_true, y_pred_hard)
    print(f"  Focal loss (uncertain):         {loss_hard.numpy():.6f}")

    assert loss_hard > loss, "Focal loss should be higher for uncertain predictions"
    print("  [OK] Focal loss correctly penalizes uncertain predictions more.")

    # Test get_config round-trip
    config = fl.get_config()
    fl2 = FocalLoss.from_config(config)
    loss2 = fl2(y_true, y_pred)
    assert abs(loss.numpy() - loss2.numpy()) < 1e-5, "Config round-trip failed!"
    print("  [OK] get_config() round-trip is consistent.")

    print("\nFocalLoss tests passed.")
