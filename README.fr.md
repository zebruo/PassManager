# PassManager

> [Read in English](README.md)

Un gestionnaire de mots de passe local et hors-ligne, développé avec Python et CustomTkinter. Toutes les données sont chiffrées et stockées sur votre machine — rien n'est envoyé à un serveur.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Plateforme](https://img.shields.io/badge/Plateforme-Windows%2010%2F11-lightgrey)
![Licence](https://img.shields.io/badge/Licence-MIT-green)

---

## Fonctionnalités

- **Mot de passe maître** — un seul mot de passe pour déverrouiller le coffre, dérivé avec PBKDF2HMAC (SHA-256, 480 000 itérations)
- **Chiffrement AES** — toutes les entrées sont chiffrées avec Fernet (AES-128-CBC) avant d'être écrites sur le disque
- **Base de données SQLite locale** — stockée dans `%APPDATA%\PassManager\` sous Windows, jamais dans le dossier de l'application
- **Générateur de mots de passe** — longueur configurable, majuscules, minuscules, chiffres, symboles
- **Recherche insensible aux accents** — rechercher `email` trouve `émail`
- **Copie en un clic** — copier le nom d'utilisateur ou le mot de passe dans le presse-papiers en un seul clic
- **Afficher / masquer** — révéler les mots de passe individuellement ou tous en même temps
- **Déconnexion automatique** — verrouillage automatique après 1 heure d'inactivité
- **Export chiffré** — exporter la base de données sous forme de fichier de sauvegarde `.db` chiffré
- **Export CSV / TXT** — exporter toutes les entrées en clair dans un fichier CSV ou TXT (à utiliser avec précaution)
- **Icônes Font Awesome** — icônes vectorielles nettes, sans artefacts visuels
- **Mode sombre** — thème sombre intégré

---

## Installation

### Option 1 — Exécutable portable (recommandé)

1. Télécharger `PassManager-x.x.x-portable.zip` depuis la page [Releases](../../releases)
2. Extraire le zip
3. Lancer `PassManager.exe` — aucune installation requise

### Option 2 — Lancer depuis les sources

**Prérequis :** Python 3.11+

```bash
git clone https://github.com/votre-utilisateur/PassManager.git
cd PassManager
pip install -r requirements.txt
python PassManager.py
```

---

## Build

L'exécutable est généré automatiquement via GitHub Actions à chaque push d'un tag `v*`.

Pour builder en local :

```bash
pip install -r requirements.txt
pyinstaller PassManager.spec
# Résultat : dist/PassManager.exe
```

---

## Sécurité

| Couche | Détail |
|---|---|
| Dérivation de clé | PBKDF2HMAC · SHA-256 · 480 000 itérations |
| Chiffrement | Fernet (AES-128-CBC + HMAC-SHA256) |
| Stockage | SQLite local · `%APPDATA%\PassManager\` |
| Mémoire | Le mot de passe maître n'est jamais stocké en clair |
| Verrouillage auto | La session se verrouille après 1 heure d'inactivité |

> **Le fichier de base de données est exclu du dépôt** (voir `.gitignore`). Ne jamais committer `passwords.db`.

---

## Structure du projet

```
PassManager/
├── PassManager.py          # Application principale
├── PassManager.spec        # Configuration de build PyInstaller
├── requirements.txt        # Dépendances Python
├── passmanager_icon.ico    # Icône de l'application
├── fa-solid-900.ttf        # Font Awesome (icônes)
└── .github/
    └── workflows/
        └── build-release.yml
```

---

## Publier une release

Pousser un tag de version pour déclencher un build automatique et une release GitHub :

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## Auteur

Développé par edurel avec [Claude AI](https://claude.ai) (Anthropic).

---

## Licence

MIT
