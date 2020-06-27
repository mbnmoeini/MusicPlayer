import os, threading, time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory   #To specify the dir of your playlist
from tkinter import ttk
from ttkthemes import themed_tk as tk
from mutagen.mp3 import MP3
from pygame import mixer



root = tk.ThemedTk()
root.set_theme("black")         # Sets an available theme

#vars
muted = FALSE
paused = FALSE
playlist = []     #contains the full path + filename
filename_path =''
# playlistbox - contains just the filename
# Fullpath + filename is required to play the music inside play_music load function

def browse_file():
    global filename_path
    filename_path = filedialog.askopenfilename()
    add_to_playlist(filename_path)

    mixer.music.queue(filename_path)


def add_to_playlist(filename):
    filename = os.path.basename(filename)
    index = 0
    playlistbox.insert(index, filename)
    playlist.insert(index, filename_path)
    index += 1


def play_music():
    global paused

    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = FALSE
    else:
        try:
            stop_music()
            time.sleep(1)
            selected_song = playlistbox.curselection()
            selected_song = int(selected_song[0])
            play_it = playlist[selected_song]
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
            show_details(play_it)
        except:
            tkinter.messagebox.showerror('File not found', 'Please check again.')


def stop_music():
    mixer.music.stop()
    statusbar['text'] = "Music Stopped"


def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music Paused"


def rewind_music():
    play_music()
    statusbar['text'] = "Music Rewinded"


def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)


def mute_music():
    global muted
    if muted:  # Unmute the music
        mixer.music.set_volume(0.7)
        scale.set(70)
        muted = FALSE
    else:  # mute the music
        mixer.music.set_volume(0)
        scale.set(0)
        muted = TRUE


def on_closing():
    stop_music()
    root.destroy()


##########designing widgets#############

statusbar = ttk.Label(root, text="Welcome to Music Player", relief=SUNKEN, anchor=W, font='Times 10 italic')
statusbar.pack(side=BOTTOM, fill=X)


mixer.init()  # initializing the mixer

root.title("Music player")

# Root Window - StatusBar, LeftFrame, RightFrame
# LeftFrame - The listbox (playlist)
# RightFrame - TopFrame,MiddleFrame and the BottomFrame

leftframe = Frame(root)
leftframe.pack(side=LEFT, padx=30, pady=30)

playlistbox = Listbox(leftframe, bg = 'mistyrose2')
playlistbox.pack()

addBtn = ttk.Button(leftframe, text="+ Add Song", command=browse_file)
addBtn.pack(side=LEFT)

rightframe = Frame(root)
rightframe.pack(pady=30)


topframe = Frame(rightframe)
topframe.pack()


middleframe = Frame(rightframe)
middleframe.pack(pady=30, padx=30)

playBtn = ttk.Button(middleframe, text='Play', command=play_music)
playBtn.grid(row=0, column=0, padx=10)

stopBtn = ttk.Button(middleframe, text='Stop', command=stop_music)
stopBtn.grid(row=0, column=1, padx=10)

pauseBtn = ttk.Button(middleframe, text = 'pause', command=pause_music)
pauseBtn.grid(row=0, column=2, padx=10)


bottomframe = Frame(rightframe)
bottomframe.pack()


rewindBtn = ttk.Button(bottomframe, text='Rewind', command=rewind_music)
rewindBtn.grid(row=0, column=0)

volumeBtn = ttk.Button(bottomframe, text='Mute', command=mute_music)
volumeBtn.grid(row=0, column=1)

scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # implement the default value of scale when music player starts
mixer.music.set_volume(0.7)
scale.grid(row=0, column=2, pady=15, padx=30)

root.protocol("WM_DELETE_WINDOW", on_closing)


root.mainloop()