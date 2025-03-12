from PIL import Image
from tkinter import filedialog
import customtkinter as ctk
import tkinter
import yt_dlp
import os
import threading
import queue

""" Sou iniciante, esse é meu primeiro app em python, utilizei o chatgpt para me ajudar na barra de progresso e também não fazer o app travar
enquanto atualiza o progresso """


""" Variável global para armazenar o diretório de destino"""
download_folder = ""

""" Cores definidas"""
cor1 = '#ff0f0f'  # red
cor2 = '#0f2fff'  # blue
cor3 = '#05f709'  # green
cor4 = '#000000'  # Black
cor5 = '#444544'  # Grey
cor6 = '#ffffff'  # white

""" Fila para receber atualizações de progresso da thread do download"""
progress_queue = queue.Queue()



def progress_hook(d):
    """enviar o progresso do download para a fila.
    """
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        if total_bytes:
            progress = d.get('downloaded_bytes', 0) / total_bytes
            progress_queue.put(progress)
    elif d['status'] == 'finished':
        progress_queue.put(1.0)

def poll_queue():
    """
    Verifica periodicamente  a fila de progresso
    e atualiza a barra de progresso. """
    try:
        while True:
            value = progress_queue.get_nowait()
            progress_bar.set(value)
    except queue.Empty:
        pass
    """Agenda a próxima verificação"""
    app.after(50, poll_queue)

def chooseFolder():
    """Abre a janela para o usuário escolher onde salvar o vídeo."""
    global download_folder
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_folder = folder_selected
        status_label.configure(text=f"📁 Salvar em: {download_folder}", text_color=cor2)
        
def startDownload():
    """Verifica e inicia o download em uma thread separada."""
    global download_folder
    ytlink = url_var.get().strip()

    if not ytlink:
        status_label.configure(text="❌ Insira um link válido!", text_color=cor1)
        return

    if not download_folder:
        status_label.configure(text="❌ Escolha uma pasta para salvar!", text_color=cor1)
        return

    """Exibe a barra de progresso somente quando o download iniciar"""
    progress_bar.place(x=18, y=150)
    progress_bar.set(0)

    """Inicia o download em uma thread separada para não bloquear a interface"""
    threading.Thread(target=download_video, args=(ytlink,), daemon=True).start()

def download_video(ytlink):
    """Executa o download do vídeo (em uma thread separada)e define o caminho completo do arquivo de saída"""
    output_path = os.path.join(download_folder, '%(title)s.%(ext)s')

    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'ffmpeg_location': r'C:\ffmpeg\bin' if os.name == 'nt' else '/usr/bin/ffmpeg',
        'progress_hooks': [progress_hook]  # A cada atualização, progress_hook é chamado
    }

    """Atualiza o status para "Baixando..."""
    app.after(0, lambda: status_label.configure(text="📥 Baixando...", text_color=cor2))
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([ytlink])
        app.after(0, lambda: status_label.configure(text="✅ Download concluído!", text_color=cor3))
    except Exception as e:
        app.after(0, lambda: status_label.configure(text="❌ Link inválido", text_color=cor1))

"""Interface Gráfica usando CustomTkinter"""
app = ctk.CTk()
app.title('Youtube Video Downloader')
app.geometry('530x180')
app.configure(fg_color=cor4)
app.resizable(False, False)
app.iconbitmap("Don_downloader/icon.ico")

"""Carregando o logo"""
logo = ctk.CTkImage(
    light_image=Image.open("Don_downloader/logoApp.png"),
    dark_image=Image.open("Don_downloader/logoApp.png"),
    size=(180, 180)
)

nomeLogo = ctk.CTkImage(
    light_image=Image.open("Don_downloader/logoDon.png"),
    dark_image=Image.open("Don_downloader/logoDon.png"),
    size=(100, 37)
)

logo_nome_label = ctk.CTkLabel(app, image=nomeLogo, text='', width=120, height=120)
logo_nome_label.place(x=230, y=-30)

logo_label = ctk.CTkLabel(app, image=logo, text="")
logo_label.place(x=343, y=-6)

"""Título principal"""
labelLink = ctk.CTkLabel(app, text='cole seu link aqui:', font=("Arial", 11))
labelLink.place(x=23, y=27)

"""Campo para inserir link"""
url_var = ctk.StringVar(value=None)

link = ctk.CTkEntry(app, width=320, height=30, textvariable=url_var, border_color=cor1, text_color=cor6,)
link.place(x=18, y=50)


"""Botão para escolher a pasta"""
btnPasta = ctk.CTkButton(app, text='Escolher Pasta', fg_color=cor1, hover_color=cor5, command=chooseFolder)
btnPasta.place(x=18, y=90)

"""Botão para iniciar o download"""
btnDownload = ctk.CTkButton(app, text='Download', fg_color=cor1, hover_color=cor5, command=startDownload)
btnDownload.place(x=200, y=90)

"""Label de status do download"""
status_label = ctk.CTkLabel(app, text="", font=("Arial", 12), width=50, wraplength=338)
status_label.place(x=18, y=120)

"""Criação da barra de progresso com CTkProgressBar (não é posicionada inicialmente), a barra será posicionada apenas quando o download iniciar"""
progress_bar = ctk.CTkProgressBar(app, width=300, height=15, fg_color='white', border_width=3, border_color=cor1, progress_color=cor5 )
progress_bar.set(0)

poll_queue()
app.mainloop()

