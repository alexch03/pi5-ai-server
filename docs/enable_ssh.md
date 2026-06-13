# Activer SSH sur un Pi 5 fraîchement flashé

> [English version below](#enable-ssh-on-a-fresh-pi-5)

Si ton SSD/SD vient d'être flashé sans cocher "Enable SSH" dans Raspberry Pi
Imager, SSH est désactivé par défaut. Trois méthodes pour l'activer :

## Méthode 1 — Imager (recommandé avant flash)

Dans Raspberry Pi Imager, clique sur le rouage avant de flasher :
- ✅ Enable SSH (avec mot de passe ou clé publique)
- ✅ Set username and password
- ✅ Configure wireless LAN (si pas d'éthernet)

## Méthode 2 — SD/SSD branché sur un PC (post-flash)

Rebranche le support sur un PC. Une partition `bootfs` (~512 Mo) apparaît.
Crée dedans un fichier vide nommé **`ssh`** (sans extension) :

```bash
# Linux / Mac
touch /Volumes/bootfs/ssh

# Windows (PowerShell)
New-Item -ItemType File -Path "D:\ssh" -Force | Out-Null
```

Au prochain boot, SSH est activé. Default user : `pi`, mot de passe par
défaut à changer immédiatement.

Optionnel — pré-créer un user :

```bash
# Mot de passe "raspberry" hashé (à régénérer avec: echo 'monmotdepasse' | openssl passwd -6 -stdin)
echo "pi:$6$rBoByrWRKMY1EHFy$ho.LISnfm83CLBWBE/yuVNvX..." > /Volumes/bootfs/userconf.txt
```

## Méthode 3 — Écran + clavier sur le Pi

```bash
sudo raspi-config
# Interface Options → SSH → Enable → Finish → reboot
```

Ou en une commande :

```bash
sudo systemctl enable --now ssh
```

## Test depuis ton poste

```bash
ssh pi@raspberrypi.local
# ou
ssh pi@<IP_du_Pi>
```

Si `raspberrypi.local` ne résout pas (pas de Bonjour/Avahi), utilise l'IP
directe — ton routeur la liste dans son admin (192.168.1.1).

---

# Enable SSH on a fresh Pi 5

If your SD/SSD was just flashed without ticking "Enable SSH" in Raspberry Pi
Imager, SSH is off by default. Three ways to enable it:

## Method 1 — Imager (recommended pre-flash)

In Raspberry Pi Imager, click the gear icon before flashing:
- ✅ Enable SSH (password or public key)
- ✅ Set username and password
- ✅ Configure wireless LAN (if no ethernet)

## Method 2 — SD/SSD plugged into a PC (post-flash)

Plug the drive into a PC. A `bootfs` partition (~512 MB) shows up. Create
an empty file named **`ssh`** (no extension):

```bash
# Linux / Mac
touch /Volumes/bootfs/ssh

# Windows (PowerShell)
New-Item -ItemType File -Path "D:\ssh" -Force | Out-Null
```

On next boot, SSH is enabled. Default user: `pi`, default password —
change it immediately.

## Method 3 — Screen + keyboard on the Pi

```bash
sudo raspi-config
# Interface Options → SSH → Enable → Finish → reboot
```

Or one-liner:

```bash
sudo systemctl enable --now ssh
```

## Test from your workstation

```bash
ssh pi@raspberrypi.local
# or
ssh pi@<Pi_IP>
```

If `raspberrypi.local` doesn't resolve (no Bonjour/Avahi), use the direct
IP — your router lists it in its admin (192.168.1.1).
