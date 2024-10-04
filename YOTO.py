import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import os
import re
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCON, TYER
import threading

ctk.set_appearance_mode("system")

def clean_filename(filename):
    filename = re.sub(r'[\t]', '', filename)
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

def choose_directory():
    folder_selected = tk.filedialog.askdirectory()
    if folder_selected:
        save_dir_label.configure(text=f"Save to: {folder_selected}")
        os.chdir(folder_selected)

def download_and_process_json():
    urls = url_text.get("1.0", tk.END).strip().splitlines()
    
    if not urls:
        messagebox.showwarning("Warning", "Please enter at least one URL.")
        return
    
    messagebox.showinfo("Info", "A folder will be created for each URL, containing subfolders for audio files and images.")

    progress_bar.pack(pady=10)
    progress_bar.set(0)
    download_button.configure(state=tk.DISABLED, text="Processing...")

    thread = threading.Thread(target=process_urls, args=(urls,))
    thread.start()

def ensure_https(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url

def process_urls(urls):
    total_urls = len(urls)
    completed_urls = 0
    
    for url in urls:
        if url:
            url = ensure_https(url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.find('meta', attrs={'name': 'title'})
                    title = clean_filename(title_tag['content']) if title_tag and 'content' in title_tag.attrs else None
                    
                    if title is None:
                        messagebox.showwarning("Error", "No 'title' meta tag found.")
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
                        messagebox.showwarning("Error", "No script found with ID '__NEXT_DATA__'.")
                else:
                    messagebox.showerror("Error", f"Failed to access the URL: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                continue

        completed_urls += 1
        progress_bar.set(completed_urls / total_urls)
        download_button.configure(text=f"Processing... {total_urls - completed_urls} URLs left")

    download_button.configure(state=tk.NORMAL, text="Extract files")
    progress_bar.pack_forget()
    messagebox.showinfo("Success", "All downloads and processing completed successfully.")

def process_json(data, title):
    downloads_dir = os.path.join(save_directory, clean_filename(title))
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
            audio_format = track.get('format', 'aac')

            audio_file_name = clean_filename(f"{track_counter:02d} - {track['title']}.{audio_format}")
            track_counter += 1
            if audio_url:
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    audio_file_path = os.path.join(audio_dir, audio_file_name)
                    with open(audio_file_path, 'wb') as audio_file:
                        audio_file.write(audio_response.content)

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

                        audio.save()
                    else:
                        print(f"Unsupported format: {audio_format}")

            display_info = chapter.get('display')
            if display_info:
                icon_url = display_info.get('icon16x16')

                if len(key) > 4:
                    icon_file_name = clean_filename(f"{image_counter:02d}.png")
                    image_counter += 1
                else:
                    icon_file_name = clean_filename(f"{key}.png")
                
                if icon_url:
                    icon_response = requests.get(icon_url)
                    if icon_response.status_code == 200:
                        with open(os.path.join(image_dir, icon_file_name), 'wb') as icon_file:
                            icon_file.write(icon_response.content)
                    else:
                        print(f"Failed to download icon: {icon_response.status_code}")
                else:
                    print(f"No icon URL found in display for track: {track['title']}.")

# Main window
root = ctk.CTk()
root.title("YOTO Json Extractor")
root.geometry("450x450")
root.wm_iconbitmap("YOTO json extractor\img\YJE.ico")

save_directory = ''

# Save directory selection
current_dir = os.getcwd()  # Get the current directory
save_dir_label = ctk.CTkLabel(root, text=f"Save files to: {current_dir}")
save_dir_label.pack(pady=5)

choose_dir_button = ctk.CTkButton(root, text="Choose a different folder", command=choose_directory)
choose_dir_button.pack(pady=10)

divider = ctk.CTkFrame(root, height=2, width=380, fg_color="#3a7ebf")
divider.pack(pady=10)

label = ctk.CTkLabel(root, text="Enter URLs (one per line):")
label.pack(pady=2)

url_text = ctk.CTkTextbox(root, width=380, height=200, corner_radius=10, border_color="#3a7ebf", border_width=2, fg_color="#FAF9F6", text_color="black", scrollbar_button_color="#D3D3D3", wrap=tk.WORD)
url_text.pack(pady=5)

progress_bar = ctk.CTkProgressBar(root, width=300)
progress_bar.set(0)
progress_bar.pack_forget()

download_button = ctk.CTkButton(root, text="Extract files", command=download_and_process_json)
download_button.pack(pady=12)

root.mainloop()