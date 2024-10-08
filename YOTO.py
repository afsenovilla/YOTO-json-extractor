import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import requests
from bs4 import BeautifulSoup
import json
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, ID3, TIT2, TALB, TPE1, TCON, TRCK, APIC
import threading
import time
import traceback
import py7zr
from datetime import datetime
import shutil

ctk.set_appearance_mode("system")
debug_mode = True

def compress_folder(folder_path, output_path):
    with py7zr.SevenZipFile(output_path, 'w') as archive:
        archive.writeall(folder_path, os.path.basename(folder_path))

def announce_message(message, type="Error", e="\nException object not provided."):
    if debug_mode:
        print(message, e)
        traceback.print_exc()
    else:
        if type == "Info":
            messagebox.showinfo(type, message)
        elif type == "Warning":
            messagebox.showwarning(type, message)
        elif type == "Error":
            messagebox.showerror(type, message)

def convert_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

def convert_bytes(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G']:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

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
        CTkMessagebox(title="Warning", message="Please enter at least one URL.", 
                      icon="warning", option_1="Ok")
        return
    
    CTkMessagebox(title="Info", message="A compressed file will be created for each URL, containing folders for audio files and images.")

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
    index = 0
    attempts = 0

    while index < len(urls):
        attempts += 1 # keep track of how many times a URL has been tried, skip it if we have tried it too many times.
        url = urls[index]
        if url: 
            if attempts < 10:
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
                            
                            try:
                                process_json(json_data, title, url) #passing the URL only so it can get logged in the library
                                os.remove(json_file_name)
                                index += 1 # move to the next item if this one processed fine
                                attempts = 0 # reset the attempt counter
                            except Exception as e:
                                announce_message("An uncaught error occured parsing a playlist:\n\tURL: '" + url +"'\n\tTitle:" + title + "\n\t", "Error", e)
                                # don't progress the index if there was an error, just retry it
                        else:
                            messagebox.showwarning("Error", "No script found with ID '__NEXT_DATA__'.")
                    else:
                        messagebox.showerror("Error", f"Failed to access the URL: {response.status_code}")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
                    #continue # when there's an error, this just causes the numbers to tick up
            else:
                messagebox.showerror("Error", f"URL has been tried 10 times and not able to complete: {url}")

        completed_urls += 1
        progress_bar.set(completed_urls / total_urls)
        download_button.configure(text=f"Processing... {total_urls - completed_urls} URLs left")

    download_button.configure(state=tk.NORMAL, text="Extract files")
    progress_bar.pack_forget()
    CTkMessagebox(message="All downloads and processing completed successfully.",
                  icon="check")

def process_json(data, title, url):
    downloads_dir = os.path.join(save_directory, clean_filename(title))
    os.makedirs(downloads_dir, exist_ok=True)

    audio_dir = os.path.join(downloads_dir, 'audio_files')
    image_dir = os.path.join(downloads_dir, 'images')
    meta_card_file = open(os.path.join(downloads_dir,  'card.txt'), 'w', encoding="utf-8") # file for metadata about the card
    meta_tracks_file = open(os.path.join(downloads_dir,  'tracks.txt'), 'w', encoding="utf-8") # file for metadata about the tracks on the card
    meta_tracks_file.write('Track Details\n================\n') # write the file header here. in a previous version this was appended after the card details in a single file
    
    meta_library_path = os.path.join(save_directory,  'YJE-library.csv') # library file to drop info about all the cards we've explored
    meta_library_file = "x"
    if(os.path.exists(meta_library_path)): #if file exists, just append to it, starting with a new line (to ensure we are writing on a fresh line)
        meta_library_file = open(meta_library_path, 'a', encoding="utf-8")
        meta_library_file.write('\n')
    else: # if file doesn't exist, give it a header line
        meta_library_file = open(meta_library_path, 'w', encoding="utf-8")
        meta_library_file.write('cardId;title;author;version;languages;slug;category;duration;readableDuration;fileSize;readableFileSize;tracks;createdAt;updatedAt;url,shareCount,availability,sharelinkURL\n')

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    ### get the card info and dump it to a file
    # Yoto is totally unreliable in the fields that they populate so everything needs to be checked before attempting to write it to a text file
    metaundef = '__undefined__'
    meta_card_file.write('Basic Details\n================\n')
    title = author = description = 'tbd'

    try:
        title = data['props']['pageProps']['card']['title']
    except:
        title = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/title \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('Title:: ' + title + '\n')
    
    try:
        author = data['props']['pageProps']['card']['metadata']['author']
        if author == "": 
            author = "MYO" # because 'author' only exsists for official cards
        announce_message("Metadata parse error: object not found: props/pageProps/card/metadata/author \n\tTitle: " + title + "\n\tURL: " + url)
    except:
        author = metaundef
    meta_card_file.write('Author:: ' + author + '\n') 
    
    try:
        description = data['props']['pageProps']['card']['metadata']['description']
    except:
        description = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/metadata/description \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('Description:: ' + description + '\n')
    meta_card_file.write('\n')


    version = category = languages = playbackType = cardID = createdAt = updatedAt = slug = sortkey = duration = readableDuration = fileSize = readableFileSize = 'tbd'    
    meta_card_file.write('Extended Details\n================\n')
    try:
        version = str(data['props']['pageProps']['card']['content']['version'])
    except:
        version = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/content/version \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('Version:: '+ version + '\n')
    
    try:
        category = data['props']['pageProps']['card']['metadata']['category']
        if category == "":
            category = metaundef
            announce_message("Metadata parse error: object not found: props/pageProps/card/metadata/category \n\tTitle: " + title + "\n\tURL: " + url)
    except:
        category = metaundef
    meta_card_file.write('Category:: ' + category +'\n') # only exsists for official cards
    
    try:
        languages_array = data['props']['pageProps']['card']['metadata']['languages']
        languages = languages_array.join(",")
    except:
        languages = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/metadata/languages \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('Languages:: '+ languages + '\n') # This is an array, so it needs to be forced into a string.

    try:
        playbackType = data['props']['pageProps']['card']['content']['playbackType']
    except:
        playbackType = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/content/playbackType \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('PlaybackType:: ' + playbackType + '\n')

    try:
        cardID = data['props']['pageProps']['card']['cardId']
    except:
        cardID = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/cardId \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('CardID:: '+ cardID + '\n')

    try:
        createdAt = data['props']['pageProps']['card']['createdAt']
    except:
        createdAt = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/createdAt \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('CreatedAt:: '+ createdAt + '\n')

    try:
        updatedAt = data['props']['pageProps']['card']['updatedAt']
    except:
        updatedAt = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/updatedAt \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('UpdatedAt:: '+ updatedAt + '\n')

    try:
        slug = data['props']['pageProps']['card']['slug']
    except: 
        slug = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/slug \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('slug:: '+ slug + '\n') # only exsists for official cards

    try:
        sortkey = data['props']['pageProps']['card']['sortkey']
    except:
        sortkey = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/sortkey \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('Sortkey:: ' + sortkey + '\n') # only exsists for official cards

    try:
        duration = data['props']['pageProps']['card']['metadata']['media']['duration']
        readableDuration = convert_seconds(int(duration))
    except:
        duration = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/metadata/media/duration \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('Duration:: ' + str(duration) + '\n')
    meta_card_file.write('ReadableDuration:: ' + readableDuration + '\n') # not always available, so let's just calculate it to be easier

    try:
        fileSize = data['props']['pageProps']['card']['metadata']['media']['fileSize']
        readableFileSize = convert_bytes(int(fileSize))
    except:
        fileSize = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/media/fileSize \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('FileSize:: ' + str(fileSize) + '\n')
    meta_card_file.write('ReadableFileSize:: ' + readableFileSize + '\n') # not always available, so let's just calculate it to be easier
    meta_card_file.write('\n')

    sharecount = availability = shareLinkURL = 'tbd'
    meta_card_file.write('Share Statistics\n================\n')
    try:
        sharecount = str(data['props']['pageProps']['card']['shareCount'])
    except:
        sharecount = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/shareCount \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('ShareCount:: ' + sharecount + '\n') # only exists in MYO cards3

    try:
        availability = data['props']['pageProps']['card']['availability']
    except:
        availability = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/availability \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('Availability:: ' + availability + '\n') # only exists in MYO cards

    try:
        shareLinkURL = data['props']['pageProps']['card']['shareLinkUrl'] 
    except:
        shareLinkURL = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/shareLinkUrl \n\tTitle: " + title + "\n\tURL: " + url)
    meta_card_file.write('ShareLinkUrl:: ' + shareLinkURL + '\n') # only exists in MYO cards
    meta_card_file.write('\n')
    meta_card_file.close()

    # fetch cover/card art file
    try:
        cover_image_url = data['props']['pageProps']['card']['metadata']['cover']['imageL']
        cover_image_path = os.path.join(image_dir, 'cover_image.png')
        image_response = requests.get(cover_image_url)

        if image_response.status_code == 200:
            with open(cover_image_path, 'wb') as img_file:
                img_file.write(image_response.content)
    except:
        cover_image_url = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/metadata/cover/imageL \n\tTitle: " + title + "\n\tURL: " + url)
        
    track_counter = 0
    chapters = data['props']['pageProps']['card']['content']['chapters']
    
    # figure out padding length then reset the track counter
    pad_length = 0
    for chapter in chapters:
        for track in chapter['tracks']:
            track_counter +=1 # count up the number of tracks so we know how long to pad the index

    meta_library_file.write(cardID +';'+ title +';'+ author +';'+ version +';'+ languages +';'+ slug +';'+ category +';'+ str(duration) +';'+ readableDuration +';'+ str(fileSize) +';'+ readableFileSize +';'+ str(track_counter) +';'+ createdAt +';'+ updatedAt +';'+ url +';'+ sharecount +';'+ availability +';'+ shareLinkURL +';'+ '\n')
    
    while track_counter != 0:
        track_counter //= 10
        pad_length += 1

    # BUG -- Every so often there will be an 'access denied' error when writing a file, usually an audio file. I think this is caused by overloading the servers with file requests and the server just responds slowly but i couldn't figure it out yet. In any case, when this error pops up what we want to do is retry the file and then continue, but what the user needs to do is just identify the culprit by spotting the .json file that was not cleaned up then delete the json and folder and try that url again on its own
    track_counter = 0
    for chapter in chapters:
        for track in chapter['tracks']:
            track_counter += 1 # to make sure we can use only one numerical index, this needs to be at the top or bottom of the loop
            
            # get the audio file
            audio_url = track.get('trackUrl')
            key = track.get('key', '')
            if len(key) > 4:
                key = f"{track_counter:0{pad_length}d}"
            audio_format = track.get('format', 'aac')
            audio_file_name = clean_filename(f"{track_counter:0{pad_length}d} - {track['title']}.{audio_format}")
            if audio_url:
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    audio_file_path = os.path.join(audio_dir, audio_file_name)
                    with open(audio_file_path, 'wb') as audio_file:
                        audio_file.write(audio_response.content)
                        audio = None

                    cardauthor = 'Yoto'
                    if author != metaundef:
                        cardauthor = author
                        try:
                            audio = ID3(audio_file_path)
                        except ID3NoHeaderError:
                            audio = ID3()
                        except Exception as e:
                            print(f"Error loading the audio file: {e}")
            if audio is not None:
                audio['TIT2'] = TIT2(encoding=3, text=[str(track['title'])])  # Title
                audio['TPE1'] = TPE1(encoding=3, text=data['props']['pageProps']['card']['metadata']['author'])  # Artist
                audio['TALB'] = TALB(encoding=3, text=data['props']['pageProps']['card']['title'])  # Album
                audio['TCON'] = TCON(encoding=3, text=data['props']['pageProps']['card']['metadata']['category'])  # Genre
                audio['TRCK'] = TRCK(encoding=3, text=[str(track['key'])])  # Track number
                audio['COMM'] = TRCK(encoding=3, text=data['props']['pageProps']['card']['cardId'])  # Comment

                if os.path.exists(cover_image_path):
                            with open(cover_image_path, 'rb') as cover_file:
                                cover_data = cover_file.read()
                            audio['APIC'] = APIC(
                            encoding=3, 
                            mime='image/png', 
                            type=3, 
                            desc='Cover', 
                            data=cover_data
                        )
                            audio.save(audio_file_path)
                else:
                    print(f"Unable to get metadata from file {audio_file_path}")
            elif audio_format == 'mp3':
                        audio['TIT2'] = TIT2(encoding=3, text=[str(track['title'])])  # Title
                        audio['TPE1'] = TPE1(encoding=3, text=data['props']['pageProps']['card']['metadata']['author'])  # Artist
                        audio['TALB'] = TALB(encoding=3, text=data['props']['pageProps']['card']['title'])  # Album
                        audio['TCON'] = TCON(encoding=3, text=data['props']['pageProps']['card']['metadata']['category'])  # Genre
                        audio['TRCK'] = TRCK(encoding=3, text=[str(track['key'])])  # Track number
                        audio['COMM'] = TRCK(encoding=3, text=data['props']['pageProps']['card']['cardId'])  # Comment

                        if os.path.exists(cover_image_path):
                            with open(cover_image_path, 'rb') as cover_file:
                                cover_data = cover_file.read()
                            audio['APIC'] = APIC(
                            encoding=3, 
                            mime='image/png', 
                            type=3, 
                            desc='Cover', 
                            data=cover_data
                        )
                            audio.save(audio_file_path)
            else:
                        print(f"Unsupported format: {audio_format}; Card: {title}; File: {audio_file_name}")
                        #Note: 'pcm_s16le' is one unsupported format see on the 'Make Your Own Guide' playlist
        else:
                    # BUG: Figure out a way to retry if the file is not fetched
                print(f"Failed to download track: {audio_response.status_code}")

            # get the icon for the track
                display_info = chapter.get('display')
        if display_info:
                icon_url = display_info.get('icon16x16')
                # Note: If Yoto ever releases a new device with a larger screen, or decides to support larger format icons, this will break immediately. The 'display' json object is prepared to suport other files as well, perhaps we should reformat this to just fetch everything and dump them into different folders based on the identifier (e.g. 'icon16x16/filename.ext, icon32x32/filename.ext')
                
                if len(key) > 4:
                    # Use the track number as the index, sometimes there may not be icons for every track
                    icon_file_name = clean_filename(f"{track_counter:0{pad_length}d}.png")
                else:
                    icon_file_name = clean_filename(f"{key}.png")
                
                if icon_url:
                    icon_response = requests.get(icon_url)
                    if icon_response.status_code == 200:
                        with open(os.path.join(image_dir, icon_file_name), 'wb') as icon_file:
                            icon_file.write(icon_response.content)
                    else:
                        #BUG: figure out a way to retry just this icon if the download fails
                        print(f"Failed to download icon: {icon_response.status_code}")
                        
                else:
                    print(f"No icon URL found in display for track: {track['title']}.")
            
            # Write the track info to the metadata file
        trackTitle = type = trackDuration = trackReadableDuration = trackFileSize = trackReadableFileSize = channels = 'tbd'    
        meta_tracks_file.write('TrackNumber:: ' + f"{track_counter:0{pad_length}d}" + '\n')
            
        try:
                trackTitle = track['title']
        except:
                trackTitle = metaundef
                announce_message("Metadata parse error: object not found: props/pageProps/card/content/cover/chapters/tracks/title \n\tTitle: " + title + "\n\tURL: " + url)
        meta_tracks_file.write('Title:: ' + trackTitle + '\n')
            
        try:
                type = track['type']
        except:
                type = metaundef
                announce_message("Metadata parse error: object not found: props/pageProps/card/content/cover/chapters/tracks/type \n\tTitle: " + title + "\n\tURL: " + url)
        meta_tracks_file.write('Type:: ' + type + '\n')

        try:
                #Podcasts like don't always have this data available
                trackDuration = str(track['duration'])
                trackReadableDuration = convert_seconds(int(trackDuration))
        except:
                trackDuration = metaundef
                trackReadableDuration = metaundef
                announce_message("Metadata parse error: object not found: props/pageProps/card/content/cover/chapters/tracks/duration \n\tTitle: " + title + "\n\tURL: " + url)
        meta_tracks_file.write('Duration:: ' + trackDuration + '\n') 
        meta_tracks_file.write('ReadableDuration:: ' + trackReadableDuration + '\n')

        try:
                trackFileSize = str(track['fileSize'])
                trackReadableFileSize = convert_bytes(int(trackFileSize))
        except:
                trackFileSize = metaundef
                trackReadableFileSize = metaundef
        announce_message("Metadata parse error: object not found: props/pageProps/card/content/cover/chapters/tracks/fileSize \n\tTitle: " + title + "\n\tURL: " + url)
        meta_tracks_file.write('FileSize:: ' + trackFileSize + '\n')
        meta_tracks_file.write('ReadableFileSize:: ' + trackReadableFileSize + '\n')
                                   
        try:
                channels = track['channels']
        except:
                channels = metaundef
                announce_message("Metadata parse error: object not found: props/pageProps/card/content/cover/chapters/tracks/channels \n\tTitle: " + title + "\n\tURL: " + url)
        meta_tracks_file.write('Channels:: ' + channels + '\n')
        meta_tracks_file.write('\n')
    meta_tracks_file.close()

    # zip up the completed package
    zipname = clean_filename(title) + " (" + datetime.today().strftime('%Y-%m-%d') + ').7z'
    try:
        compress_folder(downloads_dir, zipname) #add the current date for archive safety
    except:
        announce_message("Error compressing folder to 7zip file\\n\tTitle: " + title + "\n\tURL: " + url + "\n\tFilename: " + zipname)

    # delete the source folder if the zip was successful
    try:
        shutil.rmtree(downloads_dir)
    except:
        announce_message("Error removing folder \\n\tTitle: " + title + "\n\tURL: " + url + "\n\tFolder: " + downloads_dir)

# Main window
root = ctk.CTk()
root.title("YOTO Json Extractor")
root.geometry("450x450")
root.iconbitmap(r"YOTO json extractor\YJE.ico")

save_directory = ''

# Save directory selection
current_dir = os.getcwd()  # Get the current directory
save_dir_label = ctk.CTkLabel(root, text=f"Save files to: {current_dir}")
save_dir_label.pack(pady=5)

choose_dir_button = ctk.CTkButton(root, text="Select a different folder", command=choose_directory)
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