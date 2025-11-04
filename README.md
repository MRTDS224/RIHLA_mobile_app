# 📱 RIHLA – Application mobile touristique pour le Maroc 🇲🇦

**RIHLA** est une application mobile intelligente développée avec **Kivy** et **KivyMD**, conçue pour enrichir l’expérience touristique au Maroc. Elle combine reconnaissance d’image, traduction multilingue, audio descriptif et recommandations personnalisées pour offrir un compagnon de voyage interactif.

---

## 🚀 Fonctionnalités principales

- 🧭 Recommandations touristiques basées sur les préférences de l’utilisateur
- 📷 Reconnaissance d’images de monuments marocains via un modèle `.h5`
- 🗣️ Traduction multilingue (arabe, français, anglais…)
- 🔊 Audio descriptif des lieux touristiques
- 👤 Authentification et gestion des utilisateurs
- 🎨 Interface moderne avec KivyMD

## 📦 Structure du projet

RIHLA_mobile_app/
├── auth/                                # Gestion des utilisateurs
├── data/Audio/                          # Fichiers audio descriptifs
├── data.moroccan_monuments_model.h5     
├── dataset/                             # Modèle ML (via Git LFS)
├── modules/                             # Modules fonctionnels
├── pictures/                            # Images de monuments
├── main.py                              # Point d’entrée de l’application
├── classUsers.py                        # Classe utilisateur
├── rihla.kv                             # Interface KivyMD
├── requirements.txt                     # Dépendances Python
└── .gitignore                           # Fichiers ignorés par Git


---

## ⚙️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/MRTDS224/RIHLA_mobile_app.git
cd RIHLA_mobile_app

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer l’application
```bash
python main.py
```
### 📁 Modèle de reconnaissance (.h5)
Le fichier moroccan_monuments_model.h5 est abscent. Il va vous falloir entrainner votre propre modèle ou utiliser un autre déjà existant.

### 4. Auteurs
Développé par Mamadou Tahirou Diallo (moi)
