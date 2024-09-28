import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import re
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCON, TYER

ctk.set_appearance_mode("system")

def clean_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

def download_and_process_json():
    urls = url_text.get("1.0", tk.END).strip().splitlines()

    for url in urls:
        if url:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.find('meta', attrs={'name': 'title'})
                    title = clean_filename(title_tag['content']) if title_tag and 'content' in title_tag.attrs else None
                    
                    if title is None:
                        messagebox.showwarning("Error", "No se encontró el meta tag con el nombre 'title'.")
                        continue

                    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
                    if script_tag:
                        json_data = json.loads(script_tag.string)
                        json_file_name = f"{title}.json"
                        
                        with open(json_file_name, 'w') as json_file:
                            json.dump(json_data, json_file, indent=4)
                        
                        process_json(json_data, title)
                        os.remove(json_file_name)
                    else:
                        messagebox.showwarning("Error", "No se encontró el script con el ID '__NEXT_DATA__'.")
                else:
                    messagebox.showerror("Error", f"Error al acceder a la URL: {response.status_code}")

            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
                continue

    messagebox.showinfo("Éxito", "Todas las descargas y el procesamiento se han completado correctamente.")

def process_json(data, title):
    downloads_dir = clean_filename(title)
    os.makedirs(downloads_dir, exist_ok=True)

    audio_dir = os.path.join(downloads_dir, 'audio_files')
    image_dir = os.path.join(downloads_dir, 'images')

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    cover_image_url = data['props']['pageProps']['card']['content']['cover']['imageL']
    cover_image_path = os.path.join(image_dir, 'cover_image.jpg')
    image_response = requests.get(cover_image_url)
    
    if image_response.status_code == 200:
        with open(cover_image_path, 'wb') as img_file:
            img_file.write(image_response.content)

    track_counter = 1
    image_counter = 1
    chapters = data['props']['pageProps']['card']['content']['chapters']
    
    for chapter in chapters:
        for track in chapter['tracks']:
            audio_url = track.get('trackUrl')
            key = track.get('key', '')
            audio_format = track.get('format', 'aac')  # Suponiendo que 'aac' es el formato por defecto

            # Determina el nombre del archivo de audio
            if len(key) > 4:
                audio_file_name = f"{track_counter:02d}_{track['title']}.{audio_format}"
                track_counter += 1
            else:
                audio_file_name = clean_filename(f"{key}_{track['title']}.{audio_format}")

            if audio_url:
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    audio_file_path = os.path.join(audio_dir, audio_file_name)
                    with open(audio_file_path, 'wb') as audio_file:
                        audio_file.write(audio_response.content)

                    # Añadir metadatos al archivo de audio
                    if audio_format == 'aac':
                        audio = MP4(audio_file_path)
                        audio['\xa9nam'] = track['title']
                        audio['\xa9ART'] = ['Yoto']
                        audio['\xa9alb'] = data['props']['pageProps']['card']['title']
                        audio['\xa9gen'] = ['Children']
                        audio['\xa9day'] = ['2024']

                        if os.path.exists(cover_image_path):
                            with open(cover_image_path, 'rb') as cover_file:
                                cover_data = cover_file.read()
                                audio['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_JPEG)]
                        
                        audio.save()
                    
                    elif audio_format == 'mp3':
                        audio = MP3(audio_file_path, ID3=ID3)
                        audio.tags.add(TIT2(encoding=3, text=track['title']))
                        audio.tags.add(TPE1(encoding=3, text='Yoto'))
                        audio.tags.add(TALB(encoding=3, text=data['props']['pageProps']['card']['title']))
                        audio.tags.add(TCON(encoding=3, text='Children'))
                        audio.tags.add(TYER(encoding=3, text='2024'))

                        audio.save()  # Guardar cambios en el archivo MP3
                    else:
                        print(f"Formato no soportado: {audio_format}")

                else:
                    print(f"Error al descargar el audio: {audio_response.status_code}")

            # Descargar icono
            display_info = chapter.get('display')
            if display_info:
                icon_url = display_info.get('icon16x16')
                
                # Determina el nombre del archivo de icono
                if len(key) > 4:
                    icon_file_name = f"{image_counter:02d}.png"
                    image_counter += 1
                else:
                    icon_file_name = clean_filename(f"{key}.png")
                
                if icon_url:
                    icon_response = requests.get(icon_url)
                    if icon_response.status_code == 200:
                        with open(os.path.join(image_dir, icon_file_name), 'wb') as icon_file:
                            icon_file.write(icon_response.content)
                    else:
                        print(f"Error al descargar el icono: {icon_response.status_code}")
                else:
                    print(f"No se encontró URL del icono en display para la pista: {track['title']}.")

# Crear la ventana principal
root = ctk.CTk()
root.title("YOTO Downloader")
root.geometry("450x300")

# Crear etiqueta y campo de entrada
label = ctk.CTkLabel(root, text="Introduce las URLs (una por línea):")
label.pack(pady=5)

url_text = scrolledtext.ScrolledText(root, width=60, height=15, wrap=tk.WORD)
url_text.pack(pady=5)

# Crear botón para descargar el JSON y procesarlo
download_button = ctk.CTkButton(root, text="Descargar y Procesar JSON", command=download_and_process_json)
download_button.pack(pady=10)

# Ejecutar el bucle de la interfaz gráfica
root.mainloop()
