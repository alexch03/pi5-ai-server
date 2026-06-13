# Overclock du Pi 5 — 3.0 GHz stable

> [English version](overclock.en.md)

Le Pi 5 tourne à 2.4 GHz d'usine. Avec du **vrai refroidissement actif**
(ventilateur + dissipateur, idéalement un bloc alu), on peut monter à
**3.0 GHz** sans throttle et avec ~25% de gain sur le décodage des petits LLM
en CPU.

## TL;DR

```bash
bash install/02_active_cooling_check.sh   # vérifie l'idle temp
bash install/01_overclock.sh              # patche config.txt avec backup
sudo reboot
bash bench/stress_test.sh                 # 60s stress + télémétrie
```

Si quelque chose part de travers : `bash install/rollback_overclock.sh && sudo reboot`.

## Ce que fait le patch

Dans `/boot/firmware/config.txt`, le script ajoute un bloc délimité :

```ini
# --- OC block pi5-ai-server ---
arm_freq=3000
gpu_freq=1000
over_voltage_delta=60000
# --- /OC block pi5-ai-server ---
```

- `arm_freq=3000` — fréquence cible CPU (MHz)
- `gpu_freq=1000` — VideoCore VII à 1.0 GHz
- `over_voltage_delta=60000` — +60 mV sur le rail SoC pour stabiliser le 3 GHz

Le fichier original est sauvegardé dans `config.txt.bak.preoc` la première fois.
Le bloc est idempotent : relancer le script ne le duplique pas.

## Résultats observés (Pi 5 16GB + bloc alu actif)

| Charge       | Fréquence | Tension load | Temp max | Throttle |
|--------------|-----------|--------------|----------|----------|
| Idle         | 1500 MHz  | ~0.76 V      | 38°C     | 0x0      |
| 60s stress-ng matrixprod (4 cœurs) | 3000 MHz | ~1.00 V | 62°C | 0x0 |

Le seuil de throttle thermique du Pi 5 est à 80°C → on a 18°C de marge.
Si ton silicium est bon, tu peux tenter `arm_freq=3100` + `over_voltage_delta=70000`,
mais teste à chaque palier avec `bench/stress_test.sh`.

## Pourquoi le check cooling est obligatoire

Sans refroidissement actif, le SoC va :
1. Atteindre 80°C en quelques secondes à 3 GHz
2. Descendre la fréquence (throttle) → perfs pires qu'à stock
3. À long terme, dégrader la longévité de la puce

Le script `02_active_cooling_check.sh` mesure la temp idle. Si elle dépasse
55°C, il refuse d'aller plus loin — c'est un signal fort que le refroidissement
ne suit pas, ou que la Pi n'est pas vraiment idle au moment du run.

## Cooling recommandé

- **Bloc alu actif officiel Raspberry Pi 5** (~10€) — c'est ce que j'utilise
- Alternatives correctes : Argon ONE V5, Pironman 5
- À éviter pour un OC : dissipateurs passifs seuls (même les gros)

## Rollback

```bash
bash install/rollback_overclock.sh
sudo reboot
```

Si le backup est présent, il restaure l'original ; sinon il enlève juste le bloc
ajouté. Tu retombes à 2.4 GHz stock.

## Diagnostic à chaud

```bash
vcgencmd measure_clock arm     # fréquence courante en Hz
vcgencmd measure_temp          # température SoC
vcgencmd measure_volts core    # tension
vcgencmd get_throttled         # 0x0 = parfait
```

Codes de `get_throttled` à connaître :

| Bit  | Sens                               |
|------|------------------------------------|
| 0x1  | under-voltage actuel               |
| 0x2  | freq capée actuellement            |
| 0x4  | throttle actif                     |
| 0x10000 | under-voltage **est arrivé**    |
| 0x40000 | throttle **est arrivé**         |

`0x50000` veut dire "ça a throttle dans le passé mais c'est OK maintenant" —
souvent un coup de chaud lors d'un test. Reboot puis relance le stress test.
