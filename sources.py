"""Source du signal : le micro."""
import numpy as np


class SourceMicro:


    ORDRE_PILOTES = ["Windows WASAPI", "Windows DirectSound", "MME", "Windows WDM-KS"]

    def __init__(self, device=None, duree=0.37):
        import sounddevice as sd  # import tardif
        self.duree = duree
        self.flux = None
        erreurs = []
        for idx in self._candidats(sd, device):
            info = sd.query_devices(idx)
            pilote = sd.query_hostapis(info["hostapi"])["name"]
            try:
                self._ouvrir(sd, idx, info)
            except Exception as e:  # PortAudioError, ValueError...
                erreurs.append(f"  [{idx}] {info['name']} ({pilote}) : {e}")
                continue
            print(f"Micro : [{idx}] {info['name']} ({pilote}), {self.fs} Hz, N = {self.N}")
            return
        raise RuntimeError(
            "Aucun micro n'a pu être ouvert. Vérifiez Paramètres > Confidentialité > "
            "Microphone (accès activé, y compris pour les applications de bureau).\n"
            + "\n".join(erreurs))

    def _candidats(self, sd, device):
        if device is not None:
            return [device]
        entrees = [i for i, d in enumerate(sd.query_devices()) if d["max_input_channels"] > 0]
        defaut = sd.default.device[0]
        ordre = lambda i: (self.ORDRE_PILOTES.index(
            sd.query_hostapis(sd.query_devices(i)["hostapi"])["name"])
            if sd.query_hostapis(sd.query_devices(i)["hostapi"])["name"] in self.ORDRE_PILOTES
            else 99)
        autres = sorted((i for i in entrees if i != defaut), key=ordre)
        return ([defaut] if defaut is not None and defaut >= 0 else []) + autres

    def _ouvrir(self, sd, idx, info):
        self.fs = int(info["default_samplerate"])
        # N = puissance de 2 la plus proche de duree*fs (environ 0,37 s de son)
        self.N = 1 << int(round(np.log2(self.duree * self.fs)))
        self.buf = np.zeros(self.N, dtype=np.float32)

        def callback(indata, frames, temps, statut):
            self.buf = np.roll(self.buf, -frames)
            self.buf[-frames:] = indata[:, 0]

        derniere = None
        for canaux in sorted({1, int(info["max_input_channels"])}):
            try:
                flux = sd.InputStream(device=idx, samplerate=self.fs, channels=canaux,
                                      callback=callback)
                flux.start()
                self.flux = flux
                return
            except Exception as e:
                derniere = e
        raise derniere

    def lire(self):
        return self.buf.copy()

    def fermer(self):
        if self.flux is not None:
            self.flux.stop()
            self.flux.close()
