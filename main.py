"""TuneNote : accordeur chromatique en temps réel basé sur la DFT.

Lancement :  python main.py
"""
import matplotlib.pyplot as plt

from analyse import Detecteur
from sources import SourceMicro
import ui


def main():
    fig, ax_s, ax_j, bouton = ui.creer_figure()

    # Le micro n'est ouvert qu'au clic sur « Démarrer ».
    etat = {"source": None, "detecteur": None}
    minuteur = fig.canvas.new_timer(interval=150)

    def maj():
        a = etat["detecteur"].analyser(etat["source"].lire())
        ui.dessiner(fig, ax_s, ax_j, a)
        fig.canvas.draw_idle()

    minuteur.add_callback(maj)

    def demarrer():
        try:
            source = SourceMicro()
        except Exception as e:  # micro absent, accès refusé...
            print(e)
            ui.ecran_attente(fig, ax_s, ax_j, "Micro indisponible (voir la console)")
            return
        etat["source"], etat["detecteur"] = source, Detecteur(source.fs, source.N)
        minuteur.start()
        ui.etat_bouton(bouton, True)

    def arreter():
        minuteur.stop()
        etat["source"].fermer()
        etat["source"] = etat["detecteur"] = None
        ui.etat_bouton(bouton, False)
        ui.ecran_attente(fig, ax_s, ax_j)

    bouton.on_clicked(lambda _: arreter() if etat["source"] else demarrer())
    ui.ecran_attente(fig, ax_s, ax_j)
    try:
        plt.show()
    finally:
        if etat["source"]:
            etat["source"].fermer()


if __name__ == "__main__":
    main()
