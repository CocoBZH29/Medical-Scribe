# 🩺 Tessan Scribe - Assistant Médical Intelligent (PoC)

> **Projet réalisé dans le cadre du processus de recrutement Tessan.**
> *Objectif : Optimiser le temps médical et fluidifier la téléconsultation grâce à l'IA.*

## 📋 Présentation

**Tessan Scribe** est un Proof of Concept (PoC) démontrant comment l'intelligence artificielle générative peut soulager les médecins de la charge administrative. 

L'application écoute la consultation en temps réel (ou via un fichier audio), transcrit les échanges et génère automatiquement un **compte-rendu médical structuré** (Format SOAP), prêt à être intégré dans le Dossier Médical Partagé (DMP).

### 🚀 Fonctionnalités Clés
* **Transcription Audio (ASR) :** Utilisation du modèle **Whisper** pour une transcription fidèle, même avec des termes médicaux complexes.
* **Structuration Intelligente :** Analyse via **GPT-4o** pour extraire :
    * Motif de consultation
    * Histoire de la maladie
    * Constantes vitales
    * Diagnostic suspecté
    * Plan de traitement
* **Interface Intuitive :** Dashboard interactif développé avec **Streamlit** pour simuler l'écran médecin.

---

## 🛠️ Stack Technique

* **Langage :** Python 3.9+
* **Frontend :** Streamlit
* **IA Audio :** OpenAI Whisper-1
* **IA NLP :** OpenAI GPT-4o-mini
* **Versionning :** Git / GitHub

---

## Lancement du streamlit
* Depuis un terminal lancer la commande `streamlit run .\app.py`

👤 Auteur : [Corentin] [Le Gall]
