"""Extraction de la fréquence fondamentale à partir d'un bloc de signal audio."""
from dataclasses import dataclass
from typing import Optional

import numpy as np

from dft import DFTBande, fenetre_hann
from notes import Note, frequence_vers_note


@dataclass
class Analyse:
    freqs: np.ndarray                 # fréquences (Hz) des indices calculés
    amplitudes: np.ndarray            # spectre d'amplitude
    f0: Optional[float] = None        # fréquence fondamentale (Hz) ou None
    note: Optional[Note] = None


class Detecteur:
    def __init__(self, fs, N=8192, f_min=60.0, f_max=1400.0,
                 seuil_rms=0.01, seuil_sous_harmonique=0.3):
        self.fs = fs
        self.N = N
        self.seuil_rms = seuil_rms
        self.seuil_sh = seuil_sous_harmonique
        # indices k correspondant à la bande [f_min, f_max] : f = k * fs / N
        self.k_min = max(3, int(f_min * N / fs))
        self.k_max = int(f_max * N / fs) + 1
        self.dft = DFTBande(N, self.k_min, self.k_max)
        self.fenetre = fenetre_hann(N)
        self.freqs = np.arange(self.k_min, self.k_max + 1) * fs / N

    def analyser(self, signal):
        x = np.asarray(signal, dtype=np.float64)[-self.N:]
        if len(x) < self.N or np.sqrt(np.mean(x ** 2)) < self.seuil_rms:
            return Analyse(self.freqs, np.zeros(len(self.freqs)))

        # 1) retirer la composante continue, puis fenêtrer
        x = (x - x.mean()) * self.fenetre
        # 2) DFT -> spectre d'amplitude (normalisé : une sinusoïde d'amplitude A donne A)
        amp = np.abs(self.dft(x)) / (self.fenetre.sum() / 2)

        # 3) pic maximal
        i = int(np.argmax(amp))

        # 4) le pic max est parfois un harmonique : on cherche la fondamentale
        #    à f/4, f/3, f/2 (si un pic assez fort s'y trouve, c'est elle)
        for d in (4, 3, 2):
            j = int(round((self.k_min + i) / d)) - self.k_min
            if j - 2 >= 0:
                voisinage = amp[j - 2:j + 3]
                jm = j - 2 + int(np.argmax(voisinage))
                if amp[jm] >= self.seuil_sh * amp[i]:
                    i = jm
                    break

        # 5) interpolation parabolique (précision meilleure que la résolution fs/N)
        delta = 0.0
        if 0 < i < len(amp) - 1:
            a, b, c = np.log(amp[i - 1:i + 2] + 1e-12)
            den = a - 2 * b + c
            if den != 0:
                delta = 0.5 * (a - c) / den

        f0 = (self.k_min + i + delta) * self.fs / self.N
        return Analyse(self.freqs, amp, f0, frequence_vers_note(f0))
