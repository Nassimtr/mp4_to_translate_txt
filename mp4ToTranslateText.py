import os
import subprocess
import whisper
import openai

# Extraction de l'audio d'une vidéo
def extract_audio_from_video(video_path, audio_output_path):
    # Construction de la commande ffmpeg pour extraire l'audio
    command = f"ffmpeg -i \"{video_path}\" -ab 160k -ar 44100 -vn \"{audio_output_path}\""
    # Exécution de la commande dans le shell
    subprocess.run(command, shell=True, check=True)

# Transcription de l'audio en texte
def transcribe_audio(file_path):
    # Chargement du modèle de transcription 'whisper'
    model = whisper.load_model("base")
    # Transcription de l'audio en texte
    result = model.transcribe(file_path)
    return result["text"]

# Traduction du texte avec GPT-3 Turbo
def translate_text_with_gpt3_turbo(text, target_language):
    # Définition de la clé API pour OpenAI
    openai.api_key = 'METTRE Clé API'
    # Préparation de la demande de traduction
    request_prompt = (
        f"Please translate this text to {target_language}: '{text}'"
    )
    # Envoi de la demande à OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a highly capable assistant."},
            {"role": "user", "content": request_prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# Traitement du fichier vidéo
def process_video_file(video_file, target_language, output_folder, original_lang, translated_lang):
    # Remplacement de l'extension du fichier vidéo par .wav pour l'audio
    audio_file = video_file.replace(".mp4", ".wav")
    # Extraction de l'audio de la vidéo
    extract_audio_from_video(video_file, audio_file)
    # Transcription de l'audio en texte
    transcribed_text = transcribe_audio(audio_file)

    if original_lang:
        save_transcript(output_folder, video_file, transcribed_text, "original")

    # Traduction et sauvegarde du transcript si demandé
    if translated_lang:
        translated_text = translate_text_with_gpt3_turbo(transcribed_text, target_language)
        save_transcript(output_folder, video_file, translated_text, target_language)

    # Suppression du fichier audio
    os.remove(audio_file)

# Sauvegarde du transcript dans un fichier
def save_transcript(output_folder, video_file, text, lang_suffix):
    # Obtention du nom de base du fichier vidéo
    video_base_name = os.path.basename(video_file).replace(".mp4", "")
    # Construction du chemin du fichier de sortie pour le transcript
    text_output_path = os.path.join(output_folder, video_base_name, f"script-{lang_suffix}.txt")
    # Création des dossiers nécessaires
    os.makedirs(os.path.dirname(text_output_path), exist_ok=True)
    # Écriture du texte dans le fichier
    with open(text_output_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)

# Fonction principale
def main():
    # Choix du mode de traitement (une seule vidéo ou plusieurs)
    mode = input("Voulez-vous traiter une seule vidéo (1) ou plusieurs vidéos (2) ? [1/2] : ")
    # Entrée du code de la langue cible pour la traduction
    target_language = input("Entrez le code de la langue cible pour la traduction (par exemple, 'fr' pour le français) : ")
    # Choix de la langue du script (original, traduit, ou les deux)
    lang_choice = input("Voulez-vous le script dans la langue originale (1), traduit (2), ou les deux (3) ? [1/2/3] : ")

    # Détermination si le script original ou traduit est requis
    original_lang = lang_choice in ["1", "3"]
    translated_lang = lang_choice in ["2", "3"]

    # Traitement d'une seule vidéo
    if mode == "1":
        video_file = input("Entrez le chemin du fichier vidéo (MP4) : ")
        output_folder = input("Entrez le chemin du dossier pour les fichiers texte : ")
        process_video_file(video_file, target_language, output_folder, original_lang, translated_lang)
    # Traitement de plusieurs vidéos
    else:
        folder_path = input("Entrez le chemin du dossier contenant les vidéos : ")
        output_folder = input("Entrez le chemin du dossier pour les fichiers texte : ")
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(".mp4"):
                video_file = os.path.join(folder_path, file_name)
                print(f"Traitement de la vidéo : {video_file}")
                process_video_file(video_file, target_language, output_folder, original_lang, translated_lang)

    print("Traitement terminé.")

if __name__ == "__main__":
    main()
