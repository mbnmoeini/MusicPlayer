import os, threading, time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory   #To specify the dir of your playlist
from tkinter import ttk
from ttkthemes import themed_tk as tk
from mutagen.mp3 import MP3
from pygame import mixer
import sqlite3
from tinytag import TinyTag

conn = sqlite3.connect('playlist.sqlite')  #creating a connection to the data base by SQLite
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS Genre;

CREATE TABLE Location (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    loc    TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title   TEXT UNIQUE
);

CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY
        AUTOINCREMENT UNIQUE,
    title TEXT  ,
    album_id  INTEGER,
    loc_id  INTEGER,
    genre_id  INTEGER,
    len INTEGER, year INTEGER
);
''')


def insert_PL(music_path):  #inserting data into the DB
    tag = TinyTag.get(music_path)
    name = tag.title
    t_length = tag.duration
    mins, secs = divmod(t_length, 60) if not t_length==None else (3,30)
    mins = round(mins)
    secs = round(secs)
    length = '{:02d}:{:02d}'.format(mins, secs)
    album = tag.album if not tag.album==None else 'nadare'
    genre = tag.genre if not tag.genre==None else 'nadare'
    year = tag.year
    loc = music_path

    if name is None or loc is None  :
        return -1


    cur.execute('''INSERT OR IGNORE INTO Location (loc)
        VALUES ( ? )''', ( loc, ) )      #the path or URL of music
    cur.execute('SELECT id FROM Location WHERE loc = ? ', (loc, ))
    loc_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Genre (name)
        VALUES ( ? )''', ( genre, ) )
    cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre, ))
    genre_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title)
        VALUES ( ? )''', ( album, ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, loc_id,genre_id, len, year)
        VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( name, album_id, loc_id, genre_id, length, year) )

    cur.execute('SELECT id FROM Track WHERE title = ? ', (name, ))
    track_id = cur.fetchone()[0]

    conn.commit()

    return track_id




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
    global progress_bar
    mixer.music.stop()
    statusbar['text'] = "Music Stopped"
    progress_bar['value'] = 0.0
    progress_bar.update()


def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music Paused"


def restart_music():
    play_music()
    statusbar['text'] = "Music Restarted"

def rewind():
    value = playlistbox.get(playlistbox.curselection())
    x1 = playlistbox.curselection()[0]
    playlistbox.selection_clear(x1)
    if x1 - 1 == -1:
        playlistbox.selection_set(len(playlist) - 1)
    else:
        playlistbox.selection_set(x1-1)
    return x1


def forward():
    value = playlistbox.get(playlistbox.curselection())
    x1 = playlistbox.curselection()[0]
    playlistbox.selection_clear(x1)
    if x1+1==playlistbox.size():
        playlistbox.selection_set(0)
    else:
        playlistbox.selection_set(x1+1)
    return x1


def rewind_music():
    stop_music()
    time.sleep(1)
    x1 = rewind()
    play_it = playlist[x1 - 1]
    mixer.music.load(play_it)
    mixer.music.play()
    statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
    show_details(play_it)

def forward_music():
    stop_music()
    time.sleep(1)
    x1 = forward()
    if x1 == (len(playlist) - 1):
        play_it = playlist[0]
    else:
        play_it = playlist[x1 + 1]
    mixer.music.load(play_it)
    mixer.music.play()
    statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
    show_details(play_it)


def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)


def del_song():
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)


def about_us():
    tkinter.messagebox.showinfo('About Music Player', 'This is a music player using Python Tkinter by Yasamin and Mobina ;)')


def Load():
    #for inserting a whole playlist from a folder path
    directory = askdirectory()    #set the dir
    os.chdir(directory)
    musiclist = os.listdir(directory)   #listing the music content
    for item in musiclist:
        filename = os.path.basename(item)
        if item.endswith('.mp3') or item.endswith('.wav'):
            i = 0
            playlistbox.insert(i, filename)
            playlist.insert(i, item)
            i += 1


def show_details(play_song):
    file_data = os.path.splitext(play_song)
    global progress_bar
    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    lengthlabel['text'] = "Total Length" + ' - ' + timeformat
    progress_bar['maximum'] = total_length
    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
    # Continue - Ignores all of the statements below it. We check if music is paused or not.
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            currenttimelabel['text'] = "Current Time" + ' - ' + timeformat
            time.sleep(1)
            progress_bar['value'] = current_time
            progress_bar.update()
            current_time += 1


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

# Create the menubar
menubar = Menu(root)
root.config(menu=menubar)

# Create the submenu
subMenu = Menu(menubar, tearoff=0)

menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)

subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="More", menu=subMenu)
subMenu.add_command(label="About Us", command=about_us)

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

delBtn = ttk.Button(leftframe, text="- Del Song", command=del_song)
delBtn.pack(side=LEFT)

btnload = ttk.Button(leftframe, text="select folder", command=Load)
btnload.pack(side=LEFT)


rightframe = Frame(root)
rightframe.pack(pady=30)

topframe = Frame(rightframe)
topframe.pack()

lengthlabel = ttk.Label(topframe, text='Total Length : --:--')
lengthlabel.pack(pady=5)

currenttimelabel = ttk.Label(topframe, text='Current Time : --:--', relief=GROOVE)
currenttimelabel.pack()


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

restartBtn = ttk.Button(bottomframe, text='Restart', command=restart_music)
restartBtn.grid(row=0, column=0)


rewindBtn = ttk.Button(bottomframe, text = 'Rewind', command=rewind_music)
rewindBtn.grid(row=0, column=1)

forwardBtn = ttk.Button(bottomframe, text = 'Forward', command=forward_music)
forwardBtn.grid(row=0, column=2)


volumeBtn = ttk.Button(bottomframe, text='Mute', command=mute_music)
volumeBtn.grid(row=0, column=3)

scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # implement the default value of scale when music player starts
mixer.music.set_volume(0.7)
scale.grid(row=0, column=4, pady=15, padx=30)

root.protocol("WM_DELETE_WINDOW", on_closing)

#progres bar
global progress_bar
progress_bar = ttk.Progressbar(root, orient='horizontal',length=300)
progress_bar.place(x=100,y=100)
progress_bar.pack()

root.mainloop()
