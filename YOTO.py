import os
import requests
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from bs4 import BeautifulSoup
import json
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import messagebox, filedialog
import re
from mutagen.id3 import ID3, APIC, ID3NoHeaderError, TIT2, TPE1, TALB, TCON, TRCK
import threading
import time
import traceback
import py7zr
from datetime import datetime
import shutil
import base64

ctk.set_appearance_mode("system")
silent_mode = True
threads_can_run = True
MESSAGE_TYPES = {"info": "Info", "warning": "Warning", "error": "Error"}
STATUS = {"ok": 1, "retry": 2, "fail": 3}
ICON = "AAABAAUAEBAAAAEAIABoBAAAVgAAABgYAAABACAAiAkAAL4EAAAgIAAAAQAgAKgQAABGDgAAMDAAAAEAIACoJQAA7h4AABAQAAABACAAaAQAAJZEAAAoAAAAEAAAACAAAAABACAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArr4c/66+HP+uvhz/rr4c/66+HP+uvhz/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACuvhz/rr4c/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP+uvhz/AAAAAAAAAAAAAAAAAAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP8AAAAAAAAAAAAAAAAAAAAArr4c/2dyAP9ncgD/rr4c/66+HP+uvhz/rr4c/66+HP+uvhz/Z3IA/2dyAP+uvhz/AAAAAAAAAAAAAAAArr4c/2dyAP9ncgD/rr4c/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP9ncgD/Z3IA/66+HP8AAAAAAAAAAK6+HP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/AAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/wAAAAAAAAAArr4c/2dyAP+uvhz/Z3IA/66+HP9ncgD/rr4c/2dyAP9ncgD/rr4c/66+HP+uvhz/Z3IA/66+HP8AAAAAAAAAAK6+HP9ncgD/Z3IA/66+HP9ncgD/Z3IA/66+HP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/AAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/wAAAAAAAAAAAAAAAK6+HP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/wAAAAAAAAAAAAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP8AAAAAAAAAAAAAAAAAAAAAAAAAAK6+HP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/66+HP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAK6+HP+uvhz/rr4c/66+HP+uvhz/rr4c/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//AAD4HwAA4AcAAMADAADAAwAAgAEAAIABAACAAQAAgAEAAIABAACAAQAAwAMAAMADAADgBwAA+B8AAP//AAAoAAAAGAAAADAAAAABACAAAAAAAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACzwx4As8MeALPDHj6zwx58s8MefLPDHnuzwx57s8Mee7PDHnuzwx58s8MefLPDHj6zwx4As8MeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACxwR0AscEdALHBHRWywh4pssIdKqS0GJWisRf/orEX/6KxF/+isRf/orEX/6KxF/+isRf/orEX/6S0GJWywh0qssIeKbHBHRWxwR0AscEdAAAAAAAAAAAAAAAAAAAAAACvvxwAr78cAK+/HGqvvxzVr78c1o6cD+pzfwX/c38F/3N/Bf9zfwX/c38F/3N/Bf9zfwX/c38F/46cD+qvvxzWr78c1a+/HGqvvxwAr78cAAAAAAAAAAAAAAAAAK6+HACxwR0Ur78caZimE8SMmQ//jJkP/3eDB/9ibAD/YmwA/2JtAP9ibQD/Ym0A/2JtAP9ibAD/YmwA/3eDB/+MmQ//jJkP/5imE8SvvxxpscEdFK6+HAAAAAAAAAAAAK+/HACywh0rr78c1IyZD/9mcQD/ZXAA/214Av90fwX/dH8F/3N/Bf9zfwX/c38F/3N/Bf90fwX/dH8F/214Av9lcAD/ZnEA/4yZD/+vvxzUssIdK6+/HAAAAAAAAAAAAK6+HACywh0rr78c1IyZD/9lcAD/ZXAA/4SRDP+jshj/o7IY/6OyF/+jshf/o7IX/6OyF/+jshj/o7IY/4SRDP9lcAD/ZXAA/4yZD/+vvxzUssIdK66+HAAAAAAArr4cALPEHjmktBiWjpwP63eDBv9teQL/hpQM/46cD/+Nmw//jZsP/4yZDv+KmA7/ipgO/4yZDv+Nmw//jZsP/46cD/+GlAz/bXkC/3eDBv+OnA/rpLQYlrPEHjmuvhwArr4cALPDHnuisRf/c38F/2JtAP9xfQT/macU/4eUDf9mcQD/ZnEA/2x4Av9zfwX/c38F/214Av9mcQD/ZnEA/4eUDf+ZpxT/cX0E/2JtAP9zfwX/orEX/7PDHnuuvhwArr4cALPDHnuisRf/c38F/2RvAP9pdAH/cX0E/215A/9mcQD/ZnEA/4SRDP+ishf/o7IY/4SRDP9mcQD/ZnEA/215A/9xfQT/aXQB/2RvAP9zfwX/orEX/7PDHnuuvhwArr4cALPDHnuisRf/c38F/2NuAP9lbwD/ZW8A/2RvAP9kbwD/ZnEA/42bD/+ruxv/lKIS/3mFB/9mcQD/ZXAA/2NuAP9ibQD/ZG8A/2NuAP9zfwX/orEX/7PDHnuuvhwArr4cALPDHnuisRf/c38F/2t2Av9xfQT/aXQB/214Av9xfQT/aXQB/42aD/+ishf/c38F/2RvAP9pdAH/cX0E/3SABf90fwX/dH8F/2t2Af9zfwX/orEX/7PDHnuuvhwArr4cALPDHnuisRf/c38F/4SRDP+YpxT/cXwE/4WSDP+YpxP/cX0E/4uYDv+ishf/c38F/2JtAP9xfQT/macU/6W0GP+jshj/o7IY/4KPC/9zfwX/orEX/7PDHnuuvhwArr4cALPDHnuisRf/c38F/3iEB/+Nmw//jZsP/46cD/+Gkwz/bXgC/4yZDv+jshf/c38F/2NuAP9teQP/h5QM/46cD/+Nmw//jZsP/3iEB/9zfwX/orEX/7PDHnuuvhwArr4cALPDHnuisRf/c38F/2JtAP9xfQT/macU/4eUDf9mcQD/ZnEA/42bD/+jshj/dH8F/2VvAP9ncgD/Z3IA/2dxAP9ncgD/Z3IA/2RvAP9zfwX/orEX/7PDHnuuvhwArr4cALPD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AP9lcAD/ZXAA/3mFB/+frRb/rr4c/6W0GP+RnxD/dIAF/2VwAP9lcAD/ZnAA/2VvAP9lbwD/ZnAA/2VwAP9lcAD/eYUH/52sFf+wwB2/ssMePK6+HACuvhwAssMePLDAHb+drBX/eYUH/2VwAP9lcAD/ZXAA/2ZxAP9mcQD/ZXAA/2VvAP9lcAD/eYYH/5+uFv+ksxj/iJUN/3R/Bf9rdgH/ZnEA/2VwAP9lcAD/ZG8A/2RvAP9lcAD/ZXAA/2VwAP95hQf/nawV/7DAHb+ywx48rr4cAK6+HACywx48sMAdv52sFf94hQf/anUB/3SABf91gQb/anYC/2p2Av91gQb/dIAF/2p1Af95hQf/nq0W/56tFv94hAf/ZG8A/2VwAP9rdwL/dYEF/3qGB/95hgf/eYYH/3qGB/90gAX/anUB/3iFB/+drBX/sMAdv7LDHjyuvhwArr4cALLDHjywwB2/nKsV/3iEB/90fwX/kZ8R/5GfEf9zfgX/c34F/5GfEf+RnxH/dH8F/3iEB/+erRb/nq0W/3iFB/9kbgD/ZG8A/3SABf+RnxH/oK8W/5+uFv+frhb/oK8W/5CeEP9zfwX/eIQH/5yrFf+wwB2/ssMePK6+HACuvhwAssMePLDAHb+cqxX/eIQH/3N/Bf+RnxH/lqUT/4KPC/+Cjwv/lqUT/5GfEf9zfwX/eIQH/56tFv+frRb/eYUH/2VvAP9lbwD/dIAF/5GfEf+grxb/n64W/5+uFv+grxb/kJ4Q/3N/Bf94hAf/nKsV/7DAHb+ywx48rr4cAK6+HACywx48sMAdv52sFf94hQf/aXQB/3N/Bf+DkAv/l6UT/5elE/+DkAv/c38F/2l0Af95hQf/nq0W/5+tFv95hQf/ZXAA/2ZwAP9rdwL/dYEF/3qGB/95hgf/eYYH/3qGB/90gAX/anUB/3iFB/+drBX/sMAdv7LDHjyuvhwArr4cALLDHjywwB2/nawV/3iEB/9jbgD/Y24A/3SABv+SoBH/kqAR/3SABv9jbgD/ZG8A/3mGB/+frhb/n64W/3mGB/9lcAD/ZnEA/2dyAP9mcQD/ZXAA/2VwAP9lcAD/ZXAA/2RvAP9kbwD/eIQH/52sFf+wwB2/ssMePK6+HACuvhwAssMePLDAHb+drBX/eIQH/2NuAP9kbwD/a3YC/3WBBv91gQb/a3YC/2Vw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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///////8AAP/4AAAf/wAA//gAAB//AAD/+AAAH/8AAP4AAAAAfwAA/gAAAAB/AAD+AAAAAH8AAPQAAAAALwAA8AAAAAAPAADwAAAAAA8AAPAAAAAADwAA8AAAAAAPAADwAAAAAA8AAKAAAAAABQAAgAAAAAABAACAAAAAAAEAAIAAAAAAAQAAgAAAAAABAACAAAAAAAEAAIAAAAAAAQAAgAAAAAABAACAAAAAAAEAAIAAAAAAAQAAgAAAAAABAACAAAAAAAEAAIAAAAAAAQAAgAAAAAABAACAAAAAAAEAAIAAAAAAAQAAgAAAAAABAACAAAAAAAEAAIAAAAAAAQAAgAAAAAABAACAAAAAAAEAAKAAAAAABQAA8AAAAAAPAADwAAAAAA8AAPAAAAAADwAA8AAAAAAPAADwAAAAAA8AAPQAAAAALwAA/gAAAAB/AAD+AAAAAH8AAP4AAAAAfwAA//gAAB//AAD/+AAAH/8AAP/4AAAf/wAA////////AAAoAAAAEAAAACAAAAABACAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArr4c/66+HP+uvhz/rr4c/66+HP+uvhz/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACuvhz/rr4c/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP+uvhz/AAAAAAAAAAAAAAAAAAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP8AAAAAAAAAAAAAAAAAAAAArr4c/2dyAP9ncgD/rr4c/66+HP+uvhz/rr4c/66+HP+uvhz/Z3IA/2dyAP+uvhz/AAAAAAAAAAAAAAAArr4c/2dyAP9ncgD/rr4c/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP9ncgD/Z3IA/66+HP8AAAAAAAAAAK6+HP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/AAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/wAAAAAAAAAArr4c/2dyAP+uvhz/Z3IA/66+HP9ncgD/rr4c/2dyAP9ncgD/rr4c/66+HP+uvhz/Z3IA/66+HP8AAAAAAAAAAK6+HP9ncgD/Z3IA/66+HP9ncgD/Z3IA/66+HP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/AAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/wAAAAAAAAAAAAAAAK6+HP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/wAAAAAAAAAAAAAAAAAAAACuvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/Z3IA/66+HP8AAAAAAAAAAAAAAAAAAAAAAAAAAK6+HP+uvhz/Z3IA/2dyAP9ncgD/Z3IA/2dyAP9ncgD/rr4c/66+HP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAK6+HP+uvhz/rr4c/66+HP+uvhz/rr4c/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//AAD4HwAA4AcAAMADAADAAwAAgAEAAIABAACAAQAAgAEAAIABAACAAQAAwAMAAMADAADgBwAA+B8AAP//AAA="

def compress_folder(folder_path, output_path):
    with py7zr.SevenZipFile(output_path, 'w') as archive:
        archive.writeall(folder_path, os.path.basename(folder_path))

def announce_message(message, type=MESSAGE_TYPES['info'], e=None):
    # TODO: add an option to set logging level (info, warning, error)
    # TODO: add logging to a file in addition to the log window
    log_text.insert(index=ctk.END, text=f"{message}\n") #write the message to the log
    if e is not None: #if there's an exception passed in, record that to the log too
        log_text.insert(index=ctk.END, text=f"Exception: {e}\n{traceback.print_exception()}\n")

    if not silent_mode: #if user wants alerts, pop the message in a box for them
        #BUG: this doesn't pop the message boxes. I don't know why. All the messages coming into this function are logged into the Log textbox though, so that's good. but when silent_mode is false, every message coming in here should trigger a popup
        if type is MESSAGE_TYPES['info']:
            messagebox.showinfo(type, message)
        elif type is MESSAGE_TYPES['warning']:
            messagebox.showwarning(type, message)
        elif type is MESSAGE_TYPES['error']:
            messagebox.showerror(type, message)
            #CTkMessagebox(title=type, message=message, icon=type.lower())

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
        announce_message(f"Working directory changed: {folder_selected}", MESSAGE_TYPES['info'])

def download_and_process_json():
    announce_message(f"URL processing initiated.", MESSAGE_TYPES['info'])
    urls = url_queue_text.get("1.0", tk.END).strip().splitlines()
    
    if not urls:
        announce_message(f"Please enter at least one URL.", MESSAGE_TYPES['warning'])
        return
    
    announce_message(f"A compressed file will be created for each URL, containing folders for audio files and images.", MESSAGE_TYPES['info'])

    progress_bar.pack(pady=10)
    progress_bar.set(0)
    download_button.configure(state=tk.DISABLED, text="Processing...")

    thread = threading.Thread(target=process_urls, args=(urls,))
    thread.start()

def ensure_https(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        announce_message(f"Ensure_https: URL was not formatted as expected.", MESSAGE_TYPES['warning'])
    return url

def remove_string(textbox, text):
    start_index = textbox.search(text, "1.0", stopindex="end")
    if start_index:
        end_index = f"{start_index}+{len(text)+1}c" #one extra character to make sure we get the newline character too
        textbox.delete(start_index, end_index)

def stop_threads(): # currently this doesn't work so i've just disabled/removed the stop button
    announce_message(f"Stoping all threads...", MESSAGE_TYPES['warning'])
    threads_can_run = False     
    all_threads = threading.active_children()
     
    for thread in all_threads:
        announce_message(f"Thread {thread.name} has been killed.", MESSAGE_TYPES['warning'])
        thread.terminate()
        
    announce_message(f"All threads stopped.", MESSAGE_TYPES['warning'])
    threasd_can_run = True
    download_button.configure(state=tk.NORMAL, text="Extract Files")
    # Need kill all the threads somehow and then re-enable the "extract files" button too

def toggle_silent_mode():
    if silent_mode_toggle.get() == "on":
        announce_message("Settings changed: Silent Mode Enabled.", MESSAGE_TYPES['info'])
        silent_mode = True
    if silent_mode_toggle.get() == "off":
        announce_message("Settings changed: Silent Mode Disabled.", MESSAGE_TYPES['info'])
        silent_mode = False

def process_urls(urls):
    total_urls = len(urls)
    completed_urls = 0
    index = 0
    attempts = 0
    announce_message(f"Found {total_urls} URLs.", MESSAGE_TYPES['info'])

    while (index < len(urls)) & threads_can_run:
        announce_message(f"Now procesing {index} of {total_urls}", MESSAGE_TYPES['info'])
        attempts += 1 # keep track of how many times a URL has been tried, skip it if we have tried it too many times.
        url = urls[index] #BUG: this line keeps throwing out of bounds exceptions
        url_status = STATUS['ok']

        if url: 
            announce_message(f"\tAttempt {attempts} for {url}", MESSAGE_TYPES['info'])
            if attempts < 10:
                url = ensure_https(url)
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        title_tag = soup.find('meta', attrs={'name': 'title'})
                        title = clean_filename(title_tag['content']) if title_tag and 'content' in title_tag.attrs else None
                    
                        if title is None:
                            announce_message(f"\tNo 'title' meta tag found in JSON blob.", MESSAGE_TYPES['error'])
                            url_status = STATUS['fail']
                            #continue # I'm not sure if we need the continue here or not. I think with the new error handling logic, its not needed
                        else:
                            announce_message(f"\tTitle: {title}", MESSAGE_TYPES['info'])

                        script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
                        card = script_tag['card'] if script_tag and 'card' in script_tag else None

                        if card is None:
                            url_status = STATUS['fail']
                            announce_message(f"\tNo 'card' object found in JSON blob.", MESSAGE_TYPES['error'])
                        else:
                            announce_message(f"\tCard object found.", MESSAGE_TYPES['info'])
                        
                        if script_tag:
                            json_data = json.loads(script_tag.string)
                            json_file_name = f"{title}.json"
                            
                            with open(json_file_name, 'w') as json_file:
                                json.dump(json_data, json_file, indent=4)
                                announce_message(f"\tJSON data temporarily stored in {json_file}", MESSAGE_TYPES['info'])
                            
                            announce_message(f"\tCleaning up temporary JSON file.", MESSAGE_TYPES['info'])
                            try:
                                process_json(json_data, title, url) #passing the URL only so it can get logged in the library
                                os.remove(json_file_name)
                                announce_message(f"\tTemporary JSON file deleted.", MESSAGE_TYPES['info'])
                                url_status = STATUS['ok']
                            except Exception as e:
                                announce_message(f"\tAn uncaught error occured parsing a playlist.", MESSAGE_TYPES['error'], e)
                                url_status = STATUS['retry'] # don't progress the index if there was an error, just retry it
                        else:
                            announce_message(f"\tNo script found with ID '__NEXT_DATA__'.", MESSAGE_TYPES['error'])
                            url_status = STATUS['fail']
                    else:
                        announce_message(f"\tFailed to access the URL: {response.status_code}", MESSAGE_TYPES['error'])
                        url_status = STATUS['fail']
                except Exception as e:
                    announce_message(f"\tAn uncaught error occured.", MESSAGE_TYPES['error'], e)
                    url_status = STATUS['fail']
            else:
                announce_message(f"\tURL has been tried 10 times and not able to complete",MESSAGE_TYPES['error'])
                url_status = STATUS['fail']
        else:
            announce_message("An error occured. Unable to process this URL:\n\tURL: " + url + "\n", "Error")
            url_status = STATUS['fail']
                
        if url_status == STATUS['ok']:
            attempts = 0 # reset the error counter
            index += 1 # move to the next URL
            completed_urls += 1 # count the success
            # update the UI
            progress_bar.set(completed_urls / total_urls) 
            download_button.configure(text=f"Processing... {total_urls - completed_urls} URLs left")
            remove_string(textbox=url_queue_text, text=url) # Remove the URL/line from the queue
            url_success_text.insert(index=ctk.END, text=f"{url}\n") # Add URL into the Completed tab
        elif url_status == STATUS['retry']:
            attempts += 1 # increase the error counterand repeat the same URL
        elif url_status == STATUS['fail']:
            attempts = 0 # reset the error counter
            index += 1 # move to the next URL
            remove_string(textbox=url_queue_text, text=url) # Remove the URL/line from the queue
            url_fail_text.insert(index=ctk.END, text=f"{url}\n") # Add URL into the Failed tab
        announce_message(f"Finished procesing {index} of {total_urls}", MESSAGE_TYPES['info'])

    #after processing, return the UI to normal state
    download_button.configure(state=tk.NORMAL, text="Extract files")
    progress_bar.pack_forget()
    announce_message(f"All downloads and processing completed successfully.", MESSAGE_TYPES['info'])

def process_json(data, title, url):
    announce_message(f"New URL started...", MESSAGE_TYPES['info'])
    announce_message(f"\tTitle: {title}", MESSAGE_TYPES['info'])
    announce_message(f"\tURL: {url}", MESSAGE_TYPES['info'])

    downloads_dir = os.path.join(save_directory, clean_filename(title))
    os.makedirs(downloads_dir, exist_ok=True)

    announce_message(f"\tSetting up playlist workspace.", MESSAGE_TYPES['info'])
    audio_dir = os.path.join(downloads_dir, 'audio_files')
    announce_message(f"\t\tCreating audio folder: {audio_dir}", MESSAGE_TYPES['info'])
    os.makedirs(audio_dir, exist_ok=True)

    image_dir = os.path.join(downloads_dir, 'images')
    announce_message(f"\t\tCreating images folder: {image_dir}", MESSAGE_TYPES['info'])
    os.makedirs(image_dir, exist_ok=True)

    meta_card_file = open(os.path.join(downloads_dir,  'card.txt'), 'w', encoding="utf-8") # file for metadata about the card
    announce_message(f"\t\tCreated card metadata file: {meta_card_file}", MESSAGE_TYPES['info'])
    
    meta_tracks_file = open(os.path.join(downloads_dir,  'tracks.txt'), 'w', encoding="utf-8") # file for metadata about the tracks on the card
    announce_message(f"\t\tCreating tracks metadata file: {meta_tracks_file}", MESSAGE_TYPES['info'])
    meta_tracks_file.write('Track Details\n================\n') # write the file header here. in a previous version this was appended after the card details in a single file
    
    meta_library_path = os.path.join(save_directory,  'YJE-library.csv') # library file to drop info about all the cards we've explored
    meta_library_file = "x"
    if(os.path.exists(meta_library_path)): #if file exists, just append to it, starting with a new line (to ensure we are writing on a fresh line)
        meta_library_file = open(meta_library_path, 'a', encoding="utf-8")
        meta_library_file.write('\n')
        announce_message(f"\t\tLibrary file already found: {meta_library_file}", MESSAGE_TYPES['info'])
    else: # if file doesn't exist, give it a header line
        meta_library_file = open(meta_library_path, 'w', encoding="utf-8")
        announce_message(f"\t\tLibrary file not already found, creating a new one: {meta_tracks_file}", MESSAGE_TYPES['info'])
        meta_library_file.write('cardId;title;author;version;languages;slug;category;duration;readableDuration;fileSize;readableFileSize;tracks;createdAt;updatedAt;url,shareCount,availability,sharelinkURL\n') 
    announce_message(f"\tWorkspace setup complete.", MESSAGE_TYPES['info'])

    ### get the card info and dump it to a file
    # Yoto is totally unreliable in the fields that they populate so everything needs to be checked before attempting to write it to a text file
    metaundef = '__undefined__'
    announce_message(f"\tFetching 'Basic Details' from playlist.", MESSAGE_TYPES['info'])
    meta_card_file.write('Basic Details\n================\n')
    title = author = description = 'tbd'

    try:
        title = data['props']['pageProps']['card']['title']
        announce_message(f"\t\t\tTitle: {title}", MESSAGE_TYPES['info'])
    except Exception as ex:
        title = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/title", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Title:: ' + title + '\n')
    
    try:
        author = data['props']['pageProps']['card']['metadata']['author']
        if author == "":
            author = "MYO" # because 'author' only exists for official cards
        announce_message(f"\t\t\tAuthor: {author}", MESSAGE_TYPES['info'])
    except Exception as ex: #consider changing this to 'except KeyError:' for logging
        author = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/metadata/author", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Author:: ' + author + '\n') 
    
    try:
        description = data['props']['pageProps']['card']['metadata']['description']
        announce_message(f"\t\t\tDescription: {description}", MESSAGE_TYPES['info'])
    except Exception as ex:
        description = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/metadata/description", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Description:: ' + description + '\n')
    meta_card_file.write('\n')
    announce_message(f"\t\t'Basic' metadata complete.", MESSAGE_TYPES['info'])

    version = category = languages = playbackType = cardID = createdAt = updatedAt = slug = sortkey = duration = readableDuration = fileSize = readableFileSize = 'tbd'    
    announce_message(f"\t\tFetching 'Extended' metadata for playlist.", MESSAGE_TYPES['info'])
    meta_card_file.write('Extended Details\n================\n')
    try:
        version = str(data['props']['pageProps']['card']['content']['version'])
        announce_message(f"\t\t\tVersion: {version}", MESSAGE_TYPES['info'])
    except Exception as ex:
        version = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/content/version", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Version:: '+ version + '\n')
    
    try:
        category = data['props']['pageProps']['card']['metadata']['category']
        if category == "":
            raise Exception("Category is blank.")
        announce_message(f"\t\t\tCategory: {category}", MESSAGE_TYPES['info'])
    except Exception as ex:
        category = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/metadata/category", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Category:: ' + category +'\n') # only exsists for official cards
    
    try:
        languages_list = data['props']['pageProps']['card']['metadata']['languages']
        languages = ", ".join(languages_list)
        announce_message(f"\t\t\tLanguages: {languages}", MESSAGE_TYPES['info'])
    except Exception as ex:
        languages = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/metadata/languages", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Languages:: '+ languages + '\n') # This is an array, so it needs to be forced into a string.

    try:
        playbackType = data['props']['pageProps']['card']['content']['playbackType']
        announce_message(f"\t\t\tPlayback Type: {playbackType}", MESSAGE_TYPES['info'])
    except Exception as ex:
        playbackType = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/content/playbackType", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('PlaybackType:: ' + playbackType + '\n')

    try:
        cardID = data['props']['pageProps']['card']['cardId']
        announce_message(f"\t\t\tCard ID: {cardID}", MESSAGE_TYPES['info'])
    except Exception as ex:
        cardID = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/cardId", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('CardID:: '+ cardID + '\n')

    try:
        createdAt = data['props']['pageProps']['card']['createdAt']
        announce_message(f"\t\t\tDate Created: {createdAt}", MESSAGE_TYPES['info'])
    except Exception as ex:
        createdAt = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/createdAt", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('CreatedAt:: '+ createdAt + '\n')

    try:
        updatedAt = data['props']['pageProps']['card']['updatedAt']
        announce_message(f"\t\t\tDate Updated: {updatedAt}", MESSAGE_TYPES['info'])
    except Exception as ex:
        updatedAt = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/updatedAt", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('UpdatedAt:: '+ updatedAt + '\n')

    try:
        slug = data['props']['pageProps']['card']['slug']
        announce_message(f"\t\t\tStore Slug: {slug}", MESSAGE_TYPES['info'])
    except Exception as ex: 
        slug = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/slug", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('slug:: '+ slug + '\n') # only exsists for official cards

    try:
        sortkey = data['props']['pageProps']['card']['sortkey']
        announce_message(f"\t\t\tSort Key: {sortkey}", MESSAGE_TYPES['info'])
    except Exception as ex:
        sortkey = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/sortkey", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Sortkey:: ' + sortkey + '\n') # only exsists for official cards

    try:
        duration = data['props']['pageProps']['card']['metadata']['media']['duration']
        announce_message(f"\t\t\tDuration (seconds): {duration}", MESSAGE_TYPES['info'])
        readableDuration = convert_seconds(int(duration))        
        announce_message(f"\t\t\tHuman Readable Duration: {readableDuration}", MESSAGE_TYPES['info'])
    except Exception as ex:
        duration = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/metadata/media/duration", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Duration:: ' + str(duration) + '\n')
    meta_card_file.write('ReadableDuration:: ' + readableDuration + '\n') # not always available, so let's just calculate it to be easier

    try:
        fileSize = data['props']['pageProps']['card']['metadata']['media']['fileSize']
        announce_message(f"\t\t\tfileSize (bytes): {fileSize}", MESSAGE_TYPES['info'])
        readableFileSize = convert_bytes(int(fileSize))
        announce_message(f"\t\t\tHuman Readable File Size: {readableFileSize}", MESSAGE_TYPES['info'])
    except Exception as ex:
        fileSize = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/metadata/media/fileSize", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('FileSize:: ' + str(fileSize) + '\n')
    meta_card_file.write('ReadableFileSize:: ' + readableFileSize + '\n') # not always available, so let's just calculate it to be easier
    meta_card_file.write('\n')
    announce_message(f"\t\t'Extended' metadata complete.", MESSAGE_TYPES['info'])

    sharecount = availability = shareLinkURL = 'tbd'
    announce_message(f"\t\tFetching 'Sharing' metadata for playlist.", MESSAGE_TYPES['info'])
    meta_card_file.write('Share Statistics\n================\n')
    try:
        sharecount = data['props']['pageProps']['card'].get('shareCount', metaundef)
        announce_message(f"\t\t\tShare Count: {sharecount}", MESSAGE_TYPES['info'])
    except Exception as ex:
        sharecount = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/shareCount", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('ShareCount:: ' + sharecount + '\n') # only exists in MYO cards3

    try:
        availability = data['props']['pageProps']['card']['content'].get('availability', metaundef)
        announce_message(f"\t\t\tAvailability: {availability}", MESSAGE_TYPES['info'])
    except Exception as ex:
        availability = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/availability", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('Availability:: ' + availability + '\n') # only exists in MYO cards

    try:
        shareLinkURL = str(data['props']['pageProps']['card'].get('shareLinkUrl', metaundef))
        announce_message(f"\t\t\tShareable URL: {shareLinkURL}", MESSAGE_TYPES['info'])
    except Exception as ex:
        shareLinkURL = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/shareLinkUrl", MESSAGE_TYPES['error'], e=ex)
    meta_card_file.write('ShareLinkUrl:: ' + shareLinkURL + '\n') # only exists in MYO cards
    announce_message(f"\t\t'Sharing' metadata complete.", MESSAGE_TYPES['info'])

    meta_card_file.write('\n')
    meta_card_file.close()
    announce_message(f"\tCard Metadata complete", MESSAGE_TYPES['info'])

    # fetch cover/card art file
    announce_message(f"\tFetching card artwork.", MESSAGE_TYPES['info'])
    try:
        cover_image_url = data['props']['pageProps']['card']['metadata']['cover']['imageL']
        cover_image_path = os.path.join(image_dir, 'cover_image.png')
        image_response = requests.get(cover_image_url)

        if image_response.status_code == 200:
            with open(cover_image_path, 'wb') as img_file:
                img_file.write(image_response.content)
                announce_message(f"\t\tFound artwork file: {img_file}", MESSAGE_TYPES['info'])
    except Exception as ex:
        cover_image_url = metaundef
        announce_message(f"\t\t\tMetadata parse error: object not found: props/pageProps/card/metadata/cover/imageL", MESSAGE_TYPES['error'], e=ex)
    announce_message(f"\tArtwork complete.", MESSAGE_TYPES['info'])
    
    announce_message(f"\tCounting number of tracks.", MESSAGE_TYPES['info'])
    track_counter = 0
    chapters = data['props']['pageProps']['card']['content']['chapters']
    
    # figure out padding length then reset the track counter
    pad_length = 0
    for chapter in chapters:
        for track in chapter['tracks']:
            track_counter +=1 # count up the number of tracks so we know how long to pad the index
    announce_message(f"\tFound {track_counter} tracks.", MESSAGE_TYPES['info'])

    announce_message(f"\tWriting metadata to the Library file.", MESSAGE_TYPES['info'])
    meta_library_file.write(f"{cardID};{title};{author};{version};{languages};{slug};{category};{str(duration)};{readableDuration};{str(fileSize)};{readableFileSize};{str(track_counter)};{createdAt};{updatedAt};{url};{sharecount};{availability};{shareLinkURL};\n")    
    
    while track_counter != 0:
        track_counter //= 10
        pad_length += 1

    # BUG -- Every so often there will be an 'access denied' error when writing a file, usually an audio file. I think this is caused by overloading the servers with file requests and the server just responds slowly but i couldn't figure it out yet. In any case, when this error pops up what we want to do is retry the file and then continue, but what the user needs to do is just identify the culprit by spotting the .json file that was not cleaned up then delete the json and folder and try that url again on its own
    announce_message(f"\tStarting to process all tracks.", MESSAGE_TYPES['info'])
    track_counter = 0
    for chapter in chapters:
        announce_message(f"\t\tNew chapter found.", MESSAGE_TYPES['info'])
        for track in chapter['tracks']:
            announce_message(f"\t\t\tNew track found", MESSAGE_TYPES['info'])
            track_counter += 1 # to make sure we can use only one numerical index, this needs to be at the top or bottom of the loop
            
            # get the audio file
            audio_url = track.get('trackUrl')
            announce_message(f"\t\t\t\tAudio source: {audio_url}", MESSAGE_TYPES['info'])
            key = track.get('key', '')
            #if len(key) > 4:
            key = f"{track_counter:0{pad_length}d}"
            audio_format = track['format']
            audio_file_name = clean_filename(f"{track_counter:0{pad_length}d} - {track['title']}.{track['format']}")
            announce_message(f"\t\t\t\tSaving to file: {audio_file_name}", MESSAGE_TYPES['info'])
            if audio_url:
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    audio_file_path = os.path.join(audio_dir, audio_file_name)
                    with open(audio_file_path, 'wb') as audio_file:
                        audio_file.write(audio_response.content)
                        audio = None
                        announce_message(f"\t\t\t\tTrack download complete.", MESSAGE_TYPES['info'])
                        # This is where the in-file metadata tags should get written
                else:
                    # BUG: Figure out a way to retry if the file is not fetched
                    announce_message(f"\t\t\t\tFailed to download track. Response code {audio_response.status_code}", MESSAGE_TYPES['error'])
            
            announce_message(f"\t\t\t\tLooking for icon file.", MESSAGE_TYPES['info'])
            display_info = chapter.get('display') # get the icon for the track
            if display_info:
                icon_url = display_info.get('icon16x16')
                announce_message(f"\t\t\t\tFound Icon (16x16): {icon_url}", MESSAGE_TYPES['info'])
                # Note: If Yoto ever releases a new device with a larger screen, or decides to support larger format icons, this will break immediately. The 'display' json object is prepared to suport other files as well, perhaps we should reformat this to just fetch everything and dump them into different folders based on the identifier (e.g. 'icon16x16/filename.ext, icon32x32/filename.ext')
                
                if len(key) > 4:
                    # Use the track number as the index, there may not be icons for every track but we want to keep the icon aligned with the track regardless
                    icon_file_name = clean_filename(f"{track_counter:0{pad_length}d}.png")
                else:
                    icon_file_name = clean_filename(f"{key}.png")
                
                if icon_url:
                    icon_response = requests.get(icon_url)
                    if icon_response.status_code == 200:
                        with open(os.path.join(image_dir, icon_file_name), 'wb') as icon_file:
                            icon_file.write(icon_response.content)
                            announce_message(f"\t\t\t\tIcon download complete: {icon_file}", MESSAGE_TYPES['info'])
                    else:
                        #BUG: figure out a way to retry just this icon if the download fails
                        announce_message(f"\t\t\t\tIcon file download failed: {icon_response.status_code}", MESSAGE_TYPES['error'])                        
                else:
                    announce_message(f"\t\t\t\tNo icon URL found in the 'display' object for this track.", MESSAGE_TYPES['warning'])
            
            # Write the track info to the metadata file
            trackTitle = type = trackDuration = trackReadableDuration = trackFileSize = trackReadableFileSize = channels = 'tbd'
            announce_message(f"\t\t\t\t\tWriting Track info into card metadata file.", MESSAGE_TYPES['info'])
            meta_tracks_file.write('TrackNumber:: ' + f"{track_counter:0{pad_length}d}" + '\n')
                
            try:
                trackTitle = track['title']
                announce_message(f"\t\t\t\t\tTrack: {trackTitle}", MESSAGE_TYPES['info'])
            except Exception as ex:
                trackTitle = metaundef
                announce_message(f"\t\t\t\t\tMetadata parse error: object not found: props/pageProps/card/content/chapters/tracks/title", MESSAGE_TYPES['error'], e=ex)
            meta_tracks_file.write('Title:: ' + trackTitle + '\n')
                
            try:
                type = track['type']
                announce_message(f"\t\t\t\t\tType: {type}", MESSAGE_TYPES['info'])
            except Exception as ex:
                type = metaundef
                announce_message(f"\t\t\t\t\tMetadata parse error: object not found: props/pageProps/card/content/chapters/tracks/type", MESSAGE_TYPES['error'], e=ex)
            meta_tracks_file.write('Type:: ' + type + '\n')

            try:
                #Podcasts like don't always have this data available
                trackDuration = str(track['duration'])
                announce_message(f"\t\t\t\t\tDuration (Seconds): {trackDuration}", MESSAGE_TYPES['info'])
                trackReadableDuration = convert_seconds(int(trackDuration))
                announce_message(f"\t\t\t\t\tHuman Readable Duration: {trackReadableDuration}", MESSAGE_TYPES['info'])
            except Exception as ex:
                trackDuration = metaundef
                trackReadableDuration = metaundef
                announce_message(f"\t\t\t\t\tMetadata parse error: object not found: props/pageProps/card/content/chapters/tracks/duration", MESSAGE_TYPES['error'], e=ex)
            meta_tracks_file.write('Duration:: ' + trackDuration + '\n') 
            meta_tracks_file.write('ReadableDuration:: ' + trackReadableDuration + '\n')

            try:
                trackFileSize = str(track['fileSize'])
                announce_message(f"\t\t\t\t\tFile Size (bytes): {trackFileSize}", MESSAGE_TYPES['info'])
                trackReadableFileSize = convert_bytes(int(trackFileSize))
                announce_message(f"\t\t\t\t\tHuman Readable File Size: {trackReadableFileSize}", MESSAGE_TYPES['info'])
            except Exception as ex:
                trackFileSize = metaundef
                trackReadableFileSize = metaundef
                announce_message(f"\t\t\t\t\tMetadata parse error: object not found: props/pageProps/card/content/chapters/tracks/fileSize", MESSAGE_TYPES['error'], e=ex)
            meta_tracks_file.write('FileSize:: ' + trackFileSize + '\n')
            meta_tracks_file.write('ReadableFileSize:: ' + trackReadableFileSize + '\n')
                                    
            try:
                channels = track['channels']
                announce_message(f"\t\t\t\t\tAudio Channels {channels}", MESSAGE_TYPES['info'])
            except Exception as ex:
                channels = metaundef
                announce_message(f"\t\t\t\t\tMetadata parse error: object not found: props/pageProps/card/content/chapters/tracks/channels", MESSAGE_TYPES['error'], e=ex)
            meta_tracks_file.write('Channels:: ' + channels + '\n')
            announce_message(f"\t\t\t\tTrack info done.", MESSAGE_TYPES['info'])
            meta_tracks_file.write('\n')
            announce_message(f"\t\t\tTrack finished.", MESSAGE_TYPES['info'])
        announce_message(f"\t\tChapter finished.", MESSAGE_TYPES['info'])
    meta_tracks_file.close()

    # zip up the completed package
    zipname = clean_filename(title) + " (" + datetime.today().strftime('%Y-%m-%d') + ').7z'
    announce_message(f"\tZipping files into 7zip archive.", MESSAGE_TYPES['info'])
    try:
        compress_folder(downloads_dir, zipname) #add the current date for archive safety
        announce_message(f"\t7zip successful: {zipname}", MESSAGE_TYPES['info'])
    except Exception as ex:
        announce_message("f\tError compressing folder to 7zip.", MESSAGE_TYPES['error'], e=ex)

    # delete the source folder if the zip was successful
    announce_message(f"\tRemoving temp files.", MESSAGE_TYPES['info'])
    try:
        shutil.rmtree(downloads_dir)
        announce_message(f"\tTemp files removed.", MESSAGE_TYPES['info'])
    except Exception as ex:
        announce_message(f"Error removing folder", MESSAGE_TYPES['error'], e=ex)
     
# Main window
root = ctk.CTk()
root.title("YOTO Json Extractor")
root.geometry("450x525")
try:
    root.iconbitmap(r"YOTO json extractor\YJE.ico")
except Exception as ex:
    #announce_message(f"Icon file not found.", MESSAGE_TYPES['warning'], e=ex) #can't send messages to the log textbox when it hasn't been created yet.
    icon_data = base64.b64decode(ICON) # Decode base64 string to bytes
    icon_image = Image.open(BytesIO(icon_data)) # Load icon data into an Image object
    root.iconphoto(True, ImageTk.PhotoImage(icon_image))

# Save directory selection
save_directory = ''
current_dir = os.getcwd()  # Get the current directory
save_dir_label = ctk.CTkLabel(root, text=f"Save files to: {current_dir}")
save_dir_label.pack(pady=5)

choose_dir_button = ctk.CTkButton(root, text="Select a different folder", command=choose_directory)
choose_dir_button.pack(pady=10)

divider = ctk.CTkFrame(root, height=2, width=380, fg_color="#3a7ebf")
divider.pack(pady=10)

silent_mode_toggle = ctk.StringVar(value="on")
logview_switch = ctk.CTkSwitch(root, text="Silent Mode", command=toggle_silent_mode, variable=silent_mode_toggle, onvalue="on", offvalue="off")
logview_switch.pack()

label = ctk.CTkLabel(root, text="Enter URLs into the Queue (one per line):")
label.pack(pady=2)

tabview = ctk.CTkTabview(root) # Build a set of tabs for the URLs to sit in
tabview.pack(pady=5)
# TODO: make the textbox resizable when the window is resized

tabview.add("Queue") # Intake - list of URLS to process
url_queue_text = ctk.CTkTextbox(master=tabview.tab("Queue"), width=380, height=200, corner_radius=10, border_color="#3a7ebf", border_width=2, fg_color="#FAF9F6", text_color="black", scrollbar_button_color="#D3D3D3", wrap=tk.WORD)
url_queue_text.pack()

tabview.add("Completed") # Output successful URLS over to here
url_success_text = ctk.CTkTextbox(master=tabview.tab("Completed"), width=380, height=200, corner_radius=10, border_color="#3a7ebf", border_width=2, fg_color="#FAF9F6", text_color="black", scrollbar_button_color="#D3D3D3", wrap=tk.WORD)
url_success_text.pack()

tabview.add("Failed") # Output failed URLs over to here
url_fail_text = ctk.CTkTextbox(master=tabview.tab("Failed"), width=380, height=200, corner_radius=10, border_color="#3a7ebf", border_width=2, fg_color="#FAF9F6", text_color="black", scrollbar_button_color="#D3D3D3", wrap=tk.WORD)
url_fail_text.pack()

tabview.add("Log") # another tab to show the output/erros
log_text = ctk.CTkTextbox(tabview.tab("Log"), width=380, height=200, corner_radius=10, border_color="#3a7ebf", border_width=2, fg_color="#FAF9F6", text_color="black", scrollbar_button_color="#D3D3D3", wrap=tk.WORD)
log_text.pack()

progress_bar = ctk.CTkProgressBar(root, width=300)
progress_bar.set(0)
progress_bar.pack_forget()

download_button = ctk.CTkButton(root, text="Extract files", command=download_and_process_json)
download_button.pack(pady=12)
#cancel_button = ctk.CTkButton(root, text="Stop!", command=stop_threads)
#cancel_button.pack(pady=12)  # button won't display for some reason

root.mainloop()
