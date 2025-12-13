import streamlit as st
import os
from utils import transcribe_audio, analyze_consultation

# 1. Configuration de la page (Titre, icône, layout)
st.set_page_config(
    page_title="Tessan Scribe PoC",
    page_icon="🩺",
    layout="wide"
)

# Petit style CSS pour ressembler (un peu) à une app médicale
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    h1 {
        color: #004e98; /* Bleu style Tessan */
    }
    .stButton button {
        background-color: #004e98;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. En-tête
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.write("🩺") # Tu pourras mettre une image ici plus tard
with col_title:
    st.title("Assistant de Consultation Intelligent")
    st.caption("Prototype R&D - Transcription & Structuration Automatique")

st.divider()

# 3. Zone d'entrée (Upload ou Micro)
st.subheader("1. Source Audio")
audio_file = st.file_uploader("Télécharger l'enregistrement de la consultation", type=["mp3", "wav", "m4a"])

# Si un fichier est chargé
if audio_file is not None:
    # On joue l'audio pour vérifier
    st.audio(audio_file)
    
    # Bouton d'action
    if st.button("🚀 Lancer l'analyse IA"):
        
        # Création des colonnes pour l'affichage
        col_transcription, col_analyse = st.columns(2)
        
        try:
            with st.spinner('🎧 Transcription de la voix en cours... (Whisper)'):
                # Streamlit a besoin d'un fichier physique, on sauvegarde temporairement l'upload
                temp_filename = audio_file.name
                with open(temp_filename, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                # Appel au Backend (utils.py)
                raw_text = transcribe_audio(temp_filename)
            
            # Affichage Transcription (Gauche)
            with col_transcription:
                st.info("📝 Transcription Brute")
                st.text_area("Ce que l'IA a entendu :", value=raw_text, height=400)

            with st.spinner('🧠 Analyse médicale et structuration... (GPT-4)'):
                # Appel au Backend (utils.py)
                medical_summary = analyze_consultation(raw_text)
                
            # Affichage Analyse (Droite)
            with col_analyse:
                st.success("📋 Compte-Rendu Structuré")
                st.markdown(medical_summary) # Markdown permet d'afficher le gras/titres
                
                # Faux bouton d'export pour le réalisme
                if st.button("Envoyer vers DMP"):
                    st.toast("✅ Dossier patient mis à jour avec succès !", icon="✅")

            # Nettoyage du fichier temporaire
            os.remove(temp_filename)
            
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

# Footer
st.markdown("---")
st.caption("Projet réalisé pour l'entretien Tessan - Proof of Concept v1.0")