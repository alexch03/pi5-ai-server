# pi5-ai-server

> [🇬🇧 English version](README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Raspberry Pi 5](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-c51a4a.svg)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black.svg)](https://ollama.com)
[![Status: validated on real hardware](https://img.shields.io/badge/status-validated-brightgreen.svg)](https://github.com/alexch03/pi5-ai-server)

Transforme un Raspberry Pi 5 en serveur d'IA local et agentique, avec
installation 1-commande, overclock stable à 3 GHz, et un mini-agent en Python
qui appelle des outils via Ollama.

**Pas de Hailo, pas de GPU, pas de cloud.** Juste le CPU du Pi 5 + Ollama +
qwen3. Le tout exposé sur le LAN pour que tes autres machines tapent dedans.

---

## Ce que ça fait

- ✅ Installe Ollama et l'expose sur le LAN (port `11434`)
- ✅ Pull les modèles qui tournent vraiment bien sur Pi 5 (qwen3:1.7b, qwen3:4b)
- ✅ Applique un overclock 3.0 GHz **stable et réversible** (backup automatique
  de `config.txt`, validé 60s stress-ng matrixprod sous 62°C)
- ✅ Refuse l'overclock si ton refroidissement n'est pas adéquat
- ✅ Installe un mini-agent (`mini_agent.py`) qui boucle sur `/api/chat` avec
  des outils (`write_file`, `read_file`, `run_command` whitelistée)
- ✅ Clients LAN pour tester depuis Windows/Mac/Linux (SSH, SFTP, bench)

## Pré-requis

- Raspberry Pi 5 (8 ou 16 GB)
- **Refroidissement actif** (bloc alu + fan officiel ou équivalent) — non
  négociable pour l'OC, voir [docs/cooling.md](docs/cooling.md)
- Debian 12 Bookworm ou 13 Trixie, kernel 6.6+
- Connexion internet (pour pull Ollama + les modèles)
- ~5 GB d'espace disque libre

## Installation en 1 commande

Sur le Pi, fraîchement flashé :

```bash
curl -fsSL https://raw.githubusercontent.com/alexch03/pi5-ai-server/main/install/bootstrap.sh | bash
```

Ce que ça fait :
1. Clone ce repo dans `~/pi5-ai-server`
2. Vérifie ton refroidissement (temp idle < 55°C)
3. Applique l'overclock 3.0 GHz avec backup de `config.txt`
4. Installe Ollama + le configure en service systemd LAN
5. Pull `qwen3:1.7b` et `qwen3:4b`
6. Installe `~/mini_agent.py`

Puis :

```bash
sudo reboot                    # active l'OC
bash bench/stress_test.sh      # vérifie que ça tient (60s stress, doit rester throttle=0x0)
```

## Installation pas à pas (alternative)

```bash
git clone https://github.com/alexch03/pi5-ai-server.git
cd pi5-ai-server
chmod +x install/*.sh bench/*.sh
bash install/install_all.sh
```

Chaque étape est dans son propre script (`install/01_*.sh` à `install/05_*.sh`),
tu peux les lancer indépendamment.

## Tester l'agent

Depuis le Pi (SSH) :

```bash
python3 ~/mini_agent.py "écris hello.txt avec 'hi pi' puis affiche son contenu"
```

Sortie attendue (qwen3:1.7b, ~15s en tout) :

```
[  3.4s] step 1: write_file({"path":"hello.txt","content":"hi pi"}) -> "OK, wrote: hello.txt"
[  8.1s] step 2: read_file({"path":"hello.txt"}) -> "hi pi"
[ 12.9s] AGENT: DONE: fichier hello.txt créé et lu, contenu "hi pi".
--- total: 12.9s, model: qwen3:1.7b
```

## Tester depuis une autre machine du LAN

```bash
git clone https://github.com/alexch03/pi5-ai-server.git
cd pi5-ai-server
pip install -r client/requirements.txt
cp .env.example .env       # puis édite avec ton IP de Pi
python client/test_ollama_lan.py
```

## Performance mesurée (Pi 5 16GB @ 3.0 GHz, active cooling)

| Modèle      | Prefill (court) | Decode    | Verdict                        |
|-------------|-----------------|-----------|--------------------------------|
| qwen3:1.7b  | 65 tok/s        | 11 tok/s  | Idéal agentique sur Pi 5       |
| qwen3:4b    | 22 tok/s        | 4 tok/s   | Mieux écrit, lent en tool-call |

Mini-agent qwen3:1.7b sur une tâche multi-outils : ~17s end-to-end.

## Pourquoi pas Hailo AI HAT ?

Le Hailo est excellent pour la **vision** (YOLOv8 en 30fps tranquille) mais
n'a pas de backend pour les LLM (pas de support llama.cpp). Pour de l'IA
textuelle/agentique, il sert à rien sur ce setup. C'est CPU + Ollama, point.

## Sécurité

- Ollama est exposé sur le LAN seulement (`0.0.0.0:11434`). **N'ouvre pas** le
  port 11434 sur ton routeur. Si tu veux y accéder hors LAN, mets-le derrière
  un VPN (Tailscale, WireGuard).
- Les credentials SSH des scripts client/ se lisent dans `.env` (gitignored),
  pas en dur dans le code.
- Le mini-agent restreint `run_command` à une whitelist (`ls`, `cat`, `echo`,
  ...). Les écritures fichier sont confinées à `~/agent-workdir` via
  vérification de chemin.

## Module optionnel — Hailo AI HAT

Si tu as un Hailo-8L (AI HAT/HAT+), un module **séparé** active le PCIe et
installe le driver/runtime. Il ne touche **pas** à la stack LLM (Ollama
reste sur CPU, Hailo dédié à la vision).

```bash
cd ~/pi5-ai-server/install/hailo_optional
bash 06_install_hailo.sh && sudo reboot
bash test_hailo_yolo.sh
```

Détails : [install/hailo_optional/README.md](install/hailo_optional/README.md).

## Documentation

- [docs/overclock.md](docs/overclock.md) — détails sur l'OC, mesures, rollback
- [docs/cooling.md](docs/cooling.md) — pourquoi le cooling actif est obligatoire
- [docs/architecture.md](docs/architecture.md) — schéma + raison de chaque choix
- [docs/enable_ssh.md](docs/enable_ssh.md) — activer SSH sur un Pi fraîchement flashé

## Désinstallation / rollback

```bash
# Revenir à 2.4 GHz stock
bash install/rollback_overclock.sh && sudo reboot

# Couper Ollama
sudo systemctl disable --now ollama.service

# Supprimer les modèles (libère ~4 GB)
ollama rm qwen3:1.7b qwen3:4b
```

## Licence

MIT — voir [LICENSE](LICENSE).
