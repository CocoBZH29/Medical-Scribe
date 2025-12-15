from utils import analyze_consultation

# On simule un texte comme si Whisper l'avait déjà transcrit
faux_texte_consultation = """
Médecin : Bonjour. Qu'est-ce qui vous amène ?
Patient : J'ai mal au crâne depuis hier matin et j'ai vomi deux fois.
Médecin : Avez-vous de la fièvre ?
Patient : Oui, j'ai pris ma température, j'avais 38.5. La lumière me fait mal aux yeux.
Médecin : D'accord, c'est probablement une migraine ophtalmique ou un début de syndrome méningé, je vais vous examiner.
"""

print("--- Démarrage du test ---")
try:
    # On teste seulement la fonction d'analyse (pas besoin de fichier audio pour l'instant)
    resultat = analyze_consultation(faux_texte_consultation)
    print("\n✅ SUCCÈS ! Voici ce que l'IA a généré :\n")
    print(resultat)
except Exception as e:
    print(f"\n❌ ERREUR : {e}")