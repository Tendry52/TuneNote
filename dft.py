"""Transformée de Fourier Discrète (DFT)

Formule :
    X[k] = somme_{n=0}^{N-1} x[n] * exp(-2*pi*i*k*n / N)

"""
import numpy as np


class DFTBande:
    """DFT restreinte aux indices k_min..k_max (matrice W pré-calculée).

    W[k, n] = exp(-2*pi*i*k*n / N)   donc   X[k] = sum_n W[k, n] * x[n]
    """

    def __init__(self, N, k_min, k_max):
        self.N = N
        self.k_min = k_min
        self.k_max = k_max
        k = np.arange(k_min, k_max + 1)
        n = np.arange(N)
        # (k*n) mod N : évite les grands angles et garde la précision
        kn = np.outer(k, n) % N
        self.W = np.exp(-2j * np.pi * kn / N).astype(np.complex64)

    def __call__(self, x):
        return self.W @ np.asarray(x, dtype=np.float32)


def fenetre_hann(N):
    """Fenêtre de Hann : w[n] = 0.5 * (1 - cos(2*pi*n / (N-1)))."""
    n = np.arange(N)
    return 0.5 * (1.0 - np.cos(2.0 * np.pi * n / (N - 1)))
