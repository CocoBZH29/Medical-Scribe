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
    1. Synthétiser la consultation (Motif, Histoire, Examen, Plan).
    2. COMPARER le traitement proposé avec le CONTEXTE PATIENT pour détecter des contre-indications (Allergies, Grossesse, interactions).
    3. COMPARER le CONTEXTE PATIENT avec le compte-rendu médical pour détecter des incohérences (mal au dos dans le CONTEXTE PATIENT puis mal à la tête dans le compte-rendu, mention de douleur à la gorge dans le CONTEXTE PATEINT mais pas dans le compte-rendu).

    STRUCTURE ATTENDUE DU COMPTE-RENDU:
    - motif_consultation (String)
    - histoire_maladie (String : résumé chronologique)
    - constantes_vitales (String : si mentionnées, sinon "Non mesuré")
    - diagnostic_suspecte (String)
    - plan_traitement (String : médicaments et conseils)

    ALERTE SÉCURITÉ (OBLIGATOIRE):
    - Si tout est OK, écris : "✅ Aucune contre-indication détectée."
    - Si risque détecté (ex: allergie ignorée), écris en GRAS et ROUGE : "🛑 ATTENTION : [Détail du risque]."

    INCOHÉRENCES (OBLIGATOIRE):
    - Si tout est OK, écris : "✅ Aucune incohérence détectée."
    - Si incohérence détectée (ex: douleur non mentionnée), écris en GRAS et NOIR : "⚠️ VIGILANCE : [Détail de l'incohérence]."

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
        temperature=0.3 # Température basse = résultats plus constants/factuels
    )
    
    return response.choices[0].message.content