import streamlit as st
import os
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

# --- SIDEBAR : Simulation des données cabine (Anamnèse) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Parc_des_Princes_logo.svg/1200px-Parc_des_Princes_logo.svg.png", width=50) # Logo fictif ou vide
    st.header("📂 Dossier Patient")
    st.info("Données récupérées automatiquement par la cabine avant la consultation.")
    
    # Simulation des antécédents
    patient_age = st.slider("Âge", 18, 90, 34)
    patient_allergies = st.multiselect(
        "Allergies Connues", 
        ["Pénicilline", "Amoxicilline", "Aspirine", "Ibuprofène", "Arachide"],
        default=["Pénicilline"] # Par défaut, on met une allergie pour tester la sécurité
    )
    patient_conditions = st.multiselect(
        "Antécédents / Conditions",
        ["Diabète", "Hypertension", "Asthme", "Grossesse"],
        default=[]
    )
    
    # On formate ces infos pour l'IA
    anamnese_text = f"""
    - Âge : {patient_age} ans
    - Allergies : {', '.join(patient_allergies) if patient_allergies else "Aucune"}
    - Antécédents : {', '.join(patient_conditions) if patient_conditions else "Aucun"}
    """

# --- PAGE PRINCIPALE ---
st.title("Assistant de Consultation Intelligent")
st.caption("v2.0 - Avec Sécurisation & Human-in-the-loop")
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
                if "ATTENTION" in final_report or "contre-indication" in final_report:
                    st.error("⚠️ ALERTE : L'IA a détecté un risque potentiel !")
                
                if st.button("✅ Valider et Envoyer au DMP"):
                    st.toast("Compte-rendu validé et archivé !", icon="🎉")
                    # Ici, on enverrait 'final_report' (la version modifiée) à la base de données
                    
        except Exception as e:
            st.error(f"Erreur : {e}")