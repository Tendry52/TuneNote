"""TuneNote : affichage du spectre fréquentiel et de la jauge d'accord (matplotlib)."""
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


def creer_figure():
    
    plt.rcParams["toolbar"] = "None"
    for cle in [c for c in plt.rcParams if c.startswith("keymap.")]:
        plt.rcParams[cle] = []
    fig, (ax_spectre, ax_jauge) = plt.subplots(
        2, 1, figsize=(9, 6), gridspec_kw={"height_ratios": [4, 1]})
    fig.canvas.manager.set_window_title("TuneNote")
    fig.subplots_adjust(hspace=0.55, top=0.88, bottom=0.26)
    ax_bouton = fig.add_axes([0.40, 0.03, 0.20, 0.08])
    bouton = Button(ax_bouton, "Démarrer")
    etat_bouton(bouton, False)
    return fig, ax_spectre, ax_jauge, bouton


def etat_bouton(bouton, en_cours):
    """Bouton vert « Démarrer » à l'arrêt, rouge « Arrêter » pendant l'écoute."""
    couleur, survol, texte = (("#d62728", "#b81f20", "Arrêter") if en_cours
                              else ("#2e9e44", "#27883b", "Démarrer"))
    bouton.label.set_text(texte)
    bouton.label.set_color("white")
    bouton.label.set_fontsize(13)
    bouton.color, bouton.hovercolor = couleur, survol
    bouton.ax.set_facecolor(couleur)
    bouton.ax.figure.canvas.draw_idle()


def ecran_attente(fig, ax_spectre, ax_jauge, texte="Appuyez sur Démarrer"):
    """Fenêtre au repos : axes vides et message."""
    ax_spectre.clear()
    ax_spectre.set_xlim(0, 1400)
    ax_spectre.set_ylim(0, 1)
    ax_spectre.set_xlabel("Fréquence (Hz)")
    ax_spectre.set_ylabel("Amplitude")
    ax_spectre.set_title("Spectre fréquentiel (module de la DFT)")
    ax_spectre.grid(alpha=0.3)
    ax_jauge.clear()
    ax_jauge.set_xlim(-50, 50)
    ax_jauge.set_ylim(0, 1)
    ax_jauge.set_yticks([])
    ax_jauge.set_xlabel("Écart (cents) : négatif = trop bas, positif = trop haut")
    ax_jauge.axvline(0, color="black", lw=1)
    fig.suptitle(texte, fontsize=18, color="gray")
    fig.canvas.draw_idle()


def dessiner(fig, ax_spectre, ax_jauge, analyse, f_aff_max=1400):
    # --- spectre ---
    ax_spectre.clear()
    ax_spectre.plot(analyse.freqs, analyse.amplitudes, color="#1f5fbf", lw=1.2)
    ax_spectre.set_xlim(0, f_aff_max)
    ax_spectre.set_ylim(0, max(0.05, float(analyse.amplitudes.max()) * 1.25))
    ax_spectre.set_xlabel("Fréquence (Hz)")
    ax_spectre.set_ylabel("Amplitude")
    ax_spectre.set_title("Spectre fréquentiel (module de la DFT)")
    ax_spectre.grid(alpha=0.3)

    # --- jauge ---
    ax_jauge.clear()
    ax_jauge.set_xlim(-50, 50)
    ax_jauge.set_ylim(0, 1)
    ax_jauge.set_yticks([])
    ax_jauge.set_xlabel("Écart (cents) : négatif = trop bas, positif = trop haut")
    ax_jauge.axvline(0, color="black", lw=1)

    if analyse.f0 is None:
        fig.suptitle("Aucun son détecté", fontsize=18, color="gray")
        return

    n = analyse.note
    ax_spectre.axvline(analyse.f0, color="red", ls="--", lw=1)
    ax_spectre.annotate(f"f0 = {analyse.f0:.1f} Hz", (analyse.f0, ax_spectre.get_ylim()[1] * 0.92),
                        xytext=(8, 0), textcoords="offset points", color="red")
    juste = abs(n.cents) < 5
    couleur = "#2e9e44" if juste else ("#e08a00" if abs(n.cents) < 20 else "#d62728")
    ax_jauge.barh(0.5, max(-50, min(50, n.cents)), height=0.5, color=couleur)
    fig.suptitle(f"{n.nom}{n.octave}    {analyse.f0:.1f} Hz    {n.cents:+.0f} cents"
                 f"    {'JUSTE' if juste else ('trop haut' if n.cents > 0 else 'trop bas')}",
                 fontsize=18, color=couleur)
