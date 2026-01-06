import streamlit as st
import os
import json
from utils import transcribe_audio, analyze_consultation

@st.dialog("Confirmation Médicale Requise")
def validation_dialog():
    st.write("Vous êtes sur le point d'envoyer ce document vers le Dossier Médical Partagé (DMP).")
    
    # Message d'avertissement clair
    st.warning("⚠️ Rappel : L'IA est une aide à la rédaction. En tant que médecin, vous êtes seul responsable du diagnostic et de la prescription.")
    
    # Case à cocher obligatoire
    confirmation = st.checkbox("Je certifie avoir relu et validé l'intégralité du contenu généré.")
    
    if st.button("Confirmer l'envoi", type="primary"):
        if confirmation:
            st.session_state['dmp_sent'] = True # On stocke l'état pour afficher le toast après fermeture
            st.rerun() # On recharge la page pour fermer la modale
        else:
            st.error("Veuillez cocher la case pour confirmer la relecture.")


st.set_page_config(page_title="Tessan Scribe PoC", 
                   page_icon="./assests/img/onglet_nabla.png", 
                   layout="wide")

# CSS
st.markdown("""
<style>
    /* 1. Fond de la page principale */
    .main {
        background-color: #f8f9fa;
    }

    /* 2. Titres */
    h1, h2, h3 {
        color: #009EE2; 
    }

    /* 3. Boutons */
    .stButton button {
        background-color: #009EE2;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #007bb0;
        color: white;
    }

    /* 4. Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FEF9D3
    }

    /* Cacher les menus Streamlit inutiles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- DONNÉES STATIQUES (PERSONAS) ---
PATIENT_PROFILES = {
    "Persona 1": {
        "Identité": "M. Thomas DUPONT",
        "Age": "34 ans",
        "Profession": "Comptable",
        "Motif Principal": "Toux sèche et nez bouché", # Oublie du mal de tête pour tester la détection d'incohérences
        "HMA": "Depuis 1 semaine",
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
    st.image('./assets/img/logo_nabla.png', width=200)
    st.header("📂 Dossier Patient")
    
    # 1. Le Sélecteur 
    selected_persona_name = st.radio(
        "Patient détecté :",
        options=list(PATIENT_PROFILES.keys())
    )

    # 2. Récupération des données du profil choisi
    current_profile = PATIENT_PROFILES[selected_persona_name]

    # 3. Affichage des détails 
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
st.markdown("""
    <div style="
        background-color: #12493C;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    ">
        <h1 style="
            color: white;
            margin: 0;
            padding: 0;
            font-size: 36px;
        ">
            Assistant de Consultation Intelligent
        </h1>
    </div>
    """, unsafe_allow_html=True)
st.caption("v2.0 - Projet pour entretien NABLA")

st.divider()

st.subheader("1. Consultation Audio")
audio_file = st.file_uploader("Source Audio", type=["mp3", "wav", "m4a"])

# On test si l'analyse a déjà été faite
if 'analysis_complete' not in st.session_state:
        st.session_state['analysis_complete'] = False
        st.session_state['summary'] = ""

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
                    # génération du compte-rendu avec la transcription et l'anamnèse
                    st.session_state["summary"] = analyze_consultation(raw_text, anamnese_text)
                
                # Zone éditable pour le médecin (Human-in-the-loop)
                st.write("📝 **Édition du Compte-Rendu**")
                
                with st.form("medical_form"):
                    
                    data = st.session_state['summary']
                    # On décompose le JSON en champs séparés
                    motif_val = st.text_input("Motif de consultation", value=data['compte_rendu']['motif_consultation'])
                    histoire_val = st.text_area("Histoire de la maladie", value=data['compte_rendu']['histoire_maladie_actuelle'], height=100)
                    exam_val = st.text_area("Examen Clinique", value=data['compte_rendu']['examen_clinique'])
                    diag_val = st.text_input("Diagnostic", value=data['compte_rendu']['diagnostic'])
                    plan_val = st.text_area("Plan de Traitement", value=data['compte_rendu']['plan_traitement'], height=120)

                    # Reconstitution du rapport final pour le DMP
                    final_report_str = f"""
                    **MOTIF CONSULTATION:** {motif_val}
                    **HISTOIRE MALADIE ACTUELLE:** {histoire_val}
                    **EXAMEN CLINIQUE:** {exam_val}
                    **DIAGNOSTIC:** {diag_val}
                    **PLAN TRAITEMENT:** {plan_val}
                    """
                    
                    submitted = st.form_submit_button("Pré-valider les modifications")
                    if submitted:
                        st.success("Modifications prises en compte pour la validation finale.")

                st.session_state['analysis_complete'] = True

        except Exception as e:
            st.error(f"Erreur : {e}")


if st.session_state['analysis_complete']:
    # Logique de détection visuelle de danger
    data = st.session_state['summary']
    alerts = []
    if data['securite']['alerte_aberration'] != "NON":
        alerts.append(f"📉 **Valeur Aberrante :** {data['securite']['alerte_aberration']}")
    if data['securite']['alerte_contre_indication'] != "NON":
        alerts.append(f"💊 **Contre-indication :** {data['securite']['alerte_contre_indication']}")
    if data['securite']['alerte_incoherence'] != "NON":
        alerts.append(f"⚠️ **Incohérence :** {data['securite']['alerte_incoherence']}")
    
    if alerts:
        st.error("🚨 **ALERTES SÉCURITÉ DÉTECTÉES**")
        for alert in alerts:
            st.markdown(f"- {alert}")
    else:
        st.success("✅ Aucune anomalie physiologique ou médicamenteuse détectée.")

    st.write("")
    
    if st.button("Valider et envoyer au DMP", use_container_width=True):
                    validation_dialog()
                    

# C. GESTION DU FEEDBACK APRÈS FERMETURE DE LA POP-UP
if 'dmp_sent' in st.session_state and st.session_state['dmp_sent']:
    st.toast("✅ Compte-rendu validé, signé et archivé dans le DMP !", icon="🚀")
    # On remet à False pour ne pas réafficher le toast au prochain clic
    st.session_state['dmp_sent'] = False
    st.session_state['summary'] = ""
    st.session_state['analysis_complete'] = False