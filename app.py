import streamlit as st
import os
import json
from utils import transcribe_audio, analyze_consultation

st.set_page_config(page_title="Tessan Scribe PoC", page_icon="🩺", layout="wide")

# CSS
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    h1 { color: #004e98; }
    .stButton button { background-color: #004e98; color: white; }
    .stTextArea textarea { background-color: #ffffff; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# --- DONNÉES STATIQUES (PERSONAS) ---
PATIENT_PROFILES = {
    "Persona 1": {
        "Identité": "M. Thomas DUPONT",
        "Age": "34 ans",
        "Profession": "Comptable",
        "Motif Principal": "Toux sèche et nez bouché", # Oublie du mal de tête pour tester la détection d'incohérences
        "HMA": "Depuis 1 semaine, douleurs: 5/10",
        "Antécédents": "Asthme léger",
        "Allergies": "Aucune",
        "Traitement en cours": "Ventoline si besoin",
        "Habitudes": "Non fumeur, Sportif occasionnel"
    },
    "Persona 2": {
        "Identité": "M. Lucas LEGRAND",
        "Age": "12 ans",
        "Profession": "Etudiant",
        "Motif Principal": "Toux sèche, mal à la gorge, mal de tête et mal au ventre", 
        "HMA": "Depuis 1 jour, douleurs: 7/10",
        "Antécédents": "Aucun",
        "Allergies": "Allergie aux Anti-Inflammatoires Non Stéroïdiens", # Allergie à l'aspirine pour tester les contre-indications lors de la prescription de médicaments
        "Traitement en cours": "Aucun",
        "Habitudes": "Non fumeur, Sportif régulier"
    }
}

# --- SIDEBAR : Simulation des données cabine (Anamnèse) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Parc_des_Princes_logo.svg/1200px-Parc_des_Princes_logo.svg.png", width=50) 
    st.header("📂 Dossier Patient")
    st.info("Données récupérées automatiquement par la cabine avant la consultation.")
    
    # 1. Le Sélecteur (Radio Button)
    selected_persona_name = st.radio(
        "Patient détecté :",
        options=list(PATIENT_PROFILES.keys())
    )

    # 2. Récupération des données du profil choisi
    current_profile = PATIENT_PROFILES[selected_persona_name]

    # 3. Affichage des détails (Déroulant)
    st.divider()
    st.subheader(f"👤 {current_profile['Identité']}")
    
    with st.expander("Voir l'anamnèse complète", expanded=True):
        st.write(f"**Âge :** {current_profile['Age']}")
        st.write(f"**Profession :** {current_profile['Profession']}")
        st.write(f"**Motif Cabine :** {current_profile['Motif Principal']}")
        st.write(f"**Histoire de la Maladie Actuelle :** {current_profile['HMA']}")
        st.markdown("---")
        # On met les points critiques en évidence
        if current_profile['Allergies'] != "Aucune":
            st.error(f"⚠️ **Allergies :** {current_profile['Allergies']}")
        else:
            st.write(f"**Allergies :** {current_profile['Allergies']}")
            
        st.warning(f"💊 **TTT Actuel :** {current_profile['Traitement en cours']}")
        st.info(f"🏥 **Antécédents :** {current_profile['Antécédents']}")
        st.write(f"**Habitudes :** {current_profile['Habitudes']}")

    # 4. Préparation du texte pour l'IA
    # On transforme le dictionnaire en texte propre pour le prompt GPT
    anamnese_text = json.dumps(current_profile, indent=2, ensure_ascii=False)

# --- PAGE PRINCIPALE ---
st.title("Assistant de Consultation Intelligent")
st.caption("v2.0 - Projet pour entretien TESSAN")
st.divider()

st.subheader("1. Consultation Audio")
audio_file = st.file_uploader("Source Audio", type=["mp3", "wav", "m4a"])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("🚀 Analyser la consultation"):
        col1, col2 = st.columns(2)
        
        try:
            # 1. TRANSCRIPTION
            with col1:
                st.info("📝 Transcription (Whisper)")
                with st.spinner("Écoute en cours..."):
                    temp_filename = audio_file.name
                    with open(temp_filename, "wb") as f:
                        f.write(audio_file.getbuffer())
                    
                    raw_text = transcribe_audio(temp_filename)
                    st.text_area("Texte transcrit", value=raw_text, height=400, disabled=True)
                    os.remove(temp_filename)

            # 2. ANALYSE & SÉCURITÉ
            with col2:
                st.success("🛡️ Analyse & Sécurité (GPT-4)")
                with st.spinner("Vérification des interactions médicamenteuses..."):
                    # On envoie le texte + l'anamnèse de la sidebar
                    medical_summary = analyze_consultation(raw_text, anamnese_text)
                
                # Zone éditable pour le médecin (Human-in-the-loop)
                final_report = st.text_area(
                    "Validez ou modifiez le compte-rendu :", 
                    value=medical_summary, 
                    height=400
                )
                
                # Logique de détection visuelle de danger
                if "ATTENTION" in final_report in final_report:
                    st.error("⚠️ ALERTE : L'IA a détecté un risque potentiel !")

                if "VIGILANCE" in final_report in final_report:
                    st.error("⚠️ VIGILANCE : L'IA a détecté une incohérence potentiel !")
                
                if st.button("✅ Valider et Envoyer au DMP"):
                    st.toast("Compte-rendu validé et archivé !", icon="🎉")
                    # Ici, on enverrait 'final_report' (la version modifiée) à la base de données
                    
        except Exception as e:
            st.error(f"Erreur : {e}")