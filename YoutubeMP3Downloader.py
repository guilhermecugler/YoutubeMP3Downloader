# Arquivo: YoutubeMP3Downloader.py
# Autor: Guilherme Cugler
# Descrição: Este é um script Python simples que baixar MP3 do Youtube

import customtkinter as ctk
import yt_dlp as youtube_dl
import threading
import tkinter as tk
import os
import pyperclip
from tkinter import filedialog
import sys

# Caminho relativo para utilizar pyinstaller --one-file


def resource_path(relative_path):
    """Obtém caminho relativo de um arquivo

    Args:
        relative_path (str): Nome do arquivo

    Returns:
        str: Caminho relativo do arquivo
    """

    if hasattr(sys, '_MEIPASS'):
        print(os.path.join(sys._MEIPASS, relative_path))
        return os.path.join(sys._MEIPASS, relative_path)
    print(os.path.join(os.path.abspath("."), relative_path))
    return os.path.join(os.path.abspath("."), relative_path)


FFMPEG_PATH = resource_path("ffmpeg")
DOWNLOAD_FOLDER = os.getcwd()
DEFAULT_DOWNLOAD_FOLDER = os.getcwd()

if os.path.basename(os.getcwd()) == "Arquivos de Programas":
    DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Music")


def truncate_title(title, length=30):
    """Corta tamanho de títulos grandes

    Args:
        title (str): Título do video
        length (int, optional): Tamanho de caracteres para retornar. Defaults to 30.

    Returns:
        str: Título do video cortado
    """
    if len(title) > length:
        return title[:length] + '...'
    return title


def download_audio(yt_url, progress_bar, status_label, title_label, remove_info, download_folder):
    """Faz download do video do youtube e transforma em mp3

    Args:
        yt_url (str): Url do video
        progress_bar (CTkProgressbar): Barra de progresso
        status_label (CTkLabel): Label de status
        title_label (CTkLabel): Label de título do video
        remove_info (Boolean): Remover da tela após concluído
        download_folder (str): Diretório de download
    """

    def progress_hook(d):
        if d['status'] == 'finished':
            progress_bar.set(1)
            status_label.configure("Download concluído")
            title_label.configure("Download concluído")

            if remove_info.get():
                status_label.destroy()
                title_label.destroy()
                progress_bar.destroy()
        elif d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes:
                progress = downloaded_bytes / total_bytes
                progress_bar.set(progress)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [progress_hook],
        'ffmpeg_location': FFMPEG_PATH,
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s')

    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(yt_url, download=False)
            title = info['title']
            truncated_title = truncate_title(title)
            title_label.configure(text=f"Baixando: {truncated_title}")

            # Verificar se o arquivo já existe
            filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(filename)[0] + ".mp3"
            if os.path.exists(mp3_filename):
                status_label.configure(
                    text="O arquivo já foi baixado anteriormente.")
                progress_bar.set(1)
                title_label.configure(
                    text=f"Download concluído: {truncated_title}")

                if remove_info.get():
                    status_label.destroy()
                    title_label.destroy()
                    progress_bar.destroy()
                return

            ydl.download([yt_url])
    except Exception as e:
        status_label.configure(text=f"Erro: {str(e)}")


def start_download(remove_info):
    """Incia uma thread para baixar um áudio a partir do label de URL

    Args:
        remove_info (Boolean): Remover dados da tela após download concluído
    """
    yt_url = url_entry.get()
    if yt_url:
        status_label = ctk.CTkLabel(frame, text="Baixando...")
        status_label.pack()
        progress_bar = ctk.CTkProgressBar(frame)
        progress_bar.pack(pady=5)
        progress_bar.set(0)
        title_label = ctk.CTkLabel(frame, text="")
        title_label.pack(pady=5)

        thread = threading.Thread(target=download_audio, args=(
            yt_url, progress_bar, status_label, title_label, remove_info, download_folder_entry.get()))
        thread.start()
        url_entry.delete(0, tk.END)
    else:
        status_label = ctk.CTkLabel(frame, text="Por favor, insira uma URL.")
        status_label.pack()


def download_from_clipboard(remove_info):
    """Inicia uma thread para baixar áudio a partir da URL Copiada

    Args:
        remove_info (Boolean): Remover dados da tela após download concluído
    """
    yt_url = pyperclip.paste()
    if yt_url:
        status_label = ctk.CTkLabel(frame, text="Baixando...")
        status_label.pack()
        progress_bar = ctk.CTkProgressBar(frame)
        progress_bar.pack(pady=5)
        progress_bar.set(0)
        title_label = ctk.CTkLabel(frame, text="")
        title_label.pack(pady=5)

        thread = threading.Thread(target=download_audio, args=(
            yt_url, progress_bar, status_label, title_label, remove_info, download_folder_entry.get()))
        thread.start()
        url_entry.delete(0, tk.END)
    else:
        status_label = ctk.CTkLabel(
            frame, text="Nenhuma URL copiada encontrada.")
        status_label.pack()


def change_appearance_mode_event(new_appearance_mode):
    """Alterar tema da interface

    Args:
        new_appearance_mode (str): Nome do tema
    """
    if new_appearance_mode == "Escuro":
        new_appearance_mode = "Dark"
    if new_appearance_mode == "Claro":
        new_appearance_mode = "Light"
    if new_appearance_mode == "Sistema":
        new_appearance_mode = "System"

    ctk.set_appearance_mode(new_appearance_mode)


def select_download_folder():
    """Seleciona a pasta de download dos arquivos
    """
    download_folder = filedialog.askdirectory()
    download_folder_entry.delete(0, tk.END)
    download_folder_entry.insert(0, download_folder)


app = ctk.CTk()

app.title("Youtube MP3 Downloader")
app.iconbitmap(resource_path("icon.ico"))

app.resizable(width=False, height=False)

appearance_mode_menu = ctk.CTkOptionMenu(app, values=["Sistema", "Escuro", "Claro"],
                                         command=change_appearance_mode_event)
appearance_mode_menu.pack(padx=10, pady=(10, 0), anchor="e")

frame = ctk.CTkScrollableFrame(app, width=400, height=350)
frame.pack(pady=20, padx=20)

url_label = ctk.CTkLabel(frame, text="Insira a URL do YouTube:")
url_label.pack(pady=10)

url_entry = ctk.CTkEntry(frame, width=400)
url_entry.pack(pady=10, padx=20)

download_folder_label = ctk.CTkLabel(
    frame, text="Selecione a pasta de destino:")
download_folder_label.pack(pady=5)

download_folder_entry = ctk.CTkEntry(frame, width=400)
download_folder_entry.insert(0, DEFAULT_DOWNLOAD_FOLDER)
download_folder_entry.pack(padx=20)

select_folder_button = ctk.CTkButton(
    frame, text="Selecionar Pasta", command=select_download_folder)
select_folder_button.pack(pady=5)

download_button = ctk.CTkButton(
    frame, text="Baixar MP3", command=lambda: start_download(remove_info_var))
download_button.pack(pady=10)

clipboard_button = ctk.CTkButton(
    frame, text="Baixar da URL Copiada", command=lambda: download_from_clipboard(remove_info_var))
clipboard_button.pack(pady=10)

remove_info_var = tk.BooleanVar()
remove_info_checkbox = ctk.CTkCheckBox(
    frame, text="Remover da tela após download concluído", variable=remove_info_var)
remove_info_checkbox.pack(pady=5)

app.mainloop()
