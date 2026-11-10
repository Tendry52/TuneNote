"""Conversion fréquence -> note (gamme tempérée, La4 = 440 Hz)."""
import math
from dataclasses import dataclass

NOMS = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]


@dataclass
class Note:
    nom: str
    octave: int
    cents: float          # écart à la note idéale (négatif = trop bas)
    frequence_cible: float


def frequence_vers_note(f, la4=440.0):
    """m = 69 + 12*log2(f / 440) est le numéro de la note (norme MIDI).
    La note la plus proche est round(m), l'écart en cents vaut 100*(m - round(m))."""
    m = 69 + 12 * math.log2(f / la4)
    n = round(m)
    cents = 100 * (m - n)
    cible = la4 * 2 ** ((n - 69) / 12)
    return Note(NOMS[n % 12], n // 12 - 1, cents, cible)

