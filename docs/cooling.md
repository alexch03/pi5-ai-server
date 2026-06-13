# Cooling actif — pourquoi c'est non-négociable pour ce setup

> [English version](cooling.en.md)

Sans cooling actif, **n'overclocke pas**. Le Pi 5 à 3 GHz dissipe ~12W sur
une puce de 1.5 cm² ; un dissipateur passif sature en quelques secondes.

## Ce qu'on attend du cooling

- **Fan + dissipateur**, pas un dissipateur seul
- Idle < 50°C dans une pièce à 22°C
- 60s stress-ng matrixprod 4 cœurs : pic < 70°C, throttle 0x0
- Bruit acceptable (le fan officiel Pi 5 est inaudible à 30% PWM)

## Setups validés

- **Cooler actif officiel Raspberry Pi 5** — 10€, montage 30s, c'est ce que
  j'utilise (62°C max sous stress 3 GHz)
- **Argon ONE V5** — boîtier alu massif + fan, dépasse l'officiel sur la durée
  mais plus cher

## Setups à éviter

- Le Pi 5 nu, sans rien
- Un dissipateur passif seul, même un gros — la convection sur 5x5 cm est insuffisante
- Les cases plastique fermées sans ventilation

## Vérifier que ton setup tient

```bash
bash bench/stress_test.sh
```

Output sain :

```
=== Stress 60s @ 3000 MHz (target) ===
t=10s  freq=3000 MHz  temp=56.4'C  volt=1.00V  throttled=0x0
t=20s  freq=3000 MHz  temp=59.8'C  volt=1.00V  throttled=0x0
t=30s  freq=3000 MHz  temp=61.2'C  volt=1.00V  throttled=0x0
t=40s  freq=3000 MHz  temp=61.8'C  volt=1.00V  throttled=0x0
t=50s  freq=3000 MHz  temp=62.0'C  volt=1.00V  throttled=0x0
t=60s  freq=3000 MHz  temp=62.0'C  volt=1.00V  throttled=0x0
```

Si tu vois `throttled=0x4` (throttle actif) ou la freq qui descend sous 3000,
ton cooling ne suit pas → soit améliore-le, soit baisse l'OC (`arm_freq=2800`).
