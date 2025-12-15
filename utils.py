import os
import json
from openai import OpenAI
from dotenv import load_dotenv 

# 1. Charger les variables d'environnement (la clé API)
load_dotenv()

# 2. Initialiser le client OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Clé API introuvable. Vérifie ton fichier .env")

client = OpenAI(api_key=api_key)

def transcribe_audio(audio_file_path):
    """
    Envoie un fichier audio à Whisper pour obtenir le texte.
    """
    print(f"🎤 Transcription en cours de : {audio_file_path}...")
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="fr" 
        )
    return transcript.text

def analyze_consultation(transcribed_text, patient_history):
    """
    Envoie le texte brut à GPT-4o-mini pour générer le compte-rendu structuré.
    """
    print("🧠 Analyse médicale en cours...")
    
    system_prompt = f"""
    Tu es un assistant médical expert pour les cabines Tessan.
    Ton rôle est de transformer une transcription brute de consultation en un compte-rendu médical structuré au format JSON.
    
    CONTEXTE PATIENT (Anamnèse récupérée avant la consultation) :
    {patient_history}

    TA TÂCHE :
    1. SYNTHÉTISER la consultation (Motif, Histoire, Examen, Plan).
    2. VÉRIFIER la plausibilité physiologique du CONTEXTE PATIENT. Si une valeur est abberante, signale-le.
    2. COMPARER le traitement proposé avec le CONTEXTE PATIENT pour détecter des contre-indications (Allergies, Grossesse, interactions).
    3. COMPARER le CONTEXTE PATIENT avec le compte-rendu médical pour détecter des incohérences (mal au dos dans le CONTEXTE PATIENT puis mal à la tête dans le compte-rendu, mention de douleur à la gorge dans le CONTEXTE PATEINT mais pas dans le compte-rendu).
    4 REMPLIR le JSON ci-dessous

    FORMAT DE SORTIE (JSON STRICT) :
        {{
            "compte_rendu": {{
                "motif_consultation": "...",
                "histoire_maladie_actuelle": "...",
                "examen_clinique": "...",
                "diagnostic": "...",
                "plan_traitement": "..."
            }},
            "securite": {{
                "alerte_aberration": "NON" ou "OUI : [Détail de la valeur impossible détectée]",
                "alerte_contre_indication": "NON" ou "OUI : [Détail risque contextuel]",
                "alerte_incoherence": "NON" ou "OUI : [Détail de l'incohérence]"
            }}
        }}

    REGLES :
    - Ignore les politesses ("Bonjour", "Au revoir").
    - Sois précis et utilise un vocabulaire médical professionnel (ex: dire "Rhinorrhée" au lieu de "nez qui coule").
    - Si une information est absente, indique "Non mentionné".
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini", # Modèle rapide et économique
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcribed_text}
        ],
        temperature=0.3, # Température basse = résultats plus constants/factuels
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)