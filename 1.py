import os, threading, time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory   #To specify the dir of your playlist
from tkinter import ttk
from ttkthemes import themed_tk as tk
from mutagen.mp3 import MP3
from mutagen.wavpack import *
from pygame import mixer
import sqlite3
from tinytag import TinyTag
from itertools import count

#################
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
    album = tag.album if not tag.album==None else 'None'
    genre = tag.genre if not tag.genre==None else 'None'
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


def select_PL(track_id):

    if track_id == -1 :
        return

    cur.execute('SELECT title FROM Track WHERE id = ? ', (track_id, ))
    name = cur.fetchone()[0]

    cur.execute('SELECT album_id FROM Track WHERE id = ? ', (track_id, ))
    album_id = cur.fetchone()[0]

    cur.execute('SELECT loc_id FROM Track WHERE id = ? ', (track_id, ))
    loc_id = cur.fetchone()[0]

    cur.execute('SELECT genre_id FROM Track WHERE id = ? ', (track_id, ))
    genre_id = cur.fetchone()[0]

    cur.execute('SELECT len FROM Track WHERE id = ? ', (track_id, ))
    length = cur.fetchone()[0]

    cur.execute('SELECT year FROM Track WHERE id = ? ', (track_id, ))
    year = cur.fetchone()[0]

    cur.execute('SELECT loc FROM Location WHERE id = ? ', (loc_id, ))
    loc = cur.fetchone()[0]

    cur.execute('SELECT name FROM Genre WHERE id = ? ', (genre_id, ))
    genre = cur.fetchone()[0]

    cur.execute('SELECT title FROM Album WHERE id = ? ', (album_id, ))
    album = cur.fetchone()[0]




    detail_label.config(text =u'Metadata:\n{}, {}, {}, {}, {}'.format(name, genre, album, year, length))
    detail_label.pack()
####################
#Main

track_id_list =[]
paused = FALSE
muted = FALSE
playlist = []       # playlist - contains the full path + filename
filename_path =''
index = 0
t_id = 1


def browse_file():
    global t_id
    global index
    global filename_path
    filename_path = filedialog.askopenfilename()
    if filename_path == '':
        return
    t_id = insert_PL(filename_path) #inserting file URL into DB
    if t_id == -1:
        return
    track_id_list.insert(index, t_id)
    add_to_playlist(filename_path)
    index += 1
    mixer.music.queue(filename_path)



def Load():
    #for inserting a whole playlist from a folder path
    global index

    directory = askdirectory(title='Choose the folder :')
    os.chdir(directory)
    musiclist = os.listdir(directory)   #listing the music content
    for item in musiclist:

        filename = os.path.basename(item)
        if item.endswith('.mp3') or item.endswith('.wav'):

            t_id = insert_PL(item)  #inserting into the DB
            if t_id == -1:
                continue
            track_id_list.insert(index, t_id)
            playlistbox.insert(index, filename)
            playlist.insert(index, item)
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
            play_it = playlist[selected_song]   #plylist gets the index of the selected song and returns its path
            #######
            #print(selected_song)
            #print (playlist[selected_song])
            #print (playlist)
            #print(track_id_list)
            select_PL(track_id_list[selected_song]) #reading from the DB
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
            show_details(play_it)
        except Exception as e:
            print(e)
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
    global progress_bar
    stop_music()
    time.sleep(1)
    x1 = rewind()
    play_it = playlist[(x1-1+len(playlist))%len(playlist)]
    if x1 == 0:
        play_it = playlist[len(playlist)-1]
        select_PL(track_id_list[len(playlist)-1])
    else:
        play_it = playlist[x1-1]
        select_PL(track_id_list[x1-1])


    progress_bar['value'] = 0.0
    progress_bar.update()
    mixer.music.load(play_it)
    mixer.music.play()
    statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
    show_details(play_it)


def forward_music():
    global progres_bar
    stop_music()
    time.sleep(1)
    x1 = forward()
    print(playlist)
    print(track_id_list)
    if x1 == (len(playlist) - 1):
        play_it = playlist[0]
        select_PL(track_id_list[0])
    else:
        play_it = playlist[x1 + 1]
        select_PL(track_id_list[x1+1])


    progress_bar['value'] = 0.0
    progress_bar.update()
    mixer.music.load(play_it)
    mixer.music.play()
    statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
    show_details(play_it)


def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)
    # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1


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

def add_to_playlist(filename):
    global index
    filename = os.path.basename(filename)
    playlistbox.insert(index, filename)
    playlist.insert(index, filename_path)
    index += 1


def del_song():
    global progress_bar
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    mixer.music.stop()
    x2 = forward()
    if x2 == (len(playlist) - 1):
        play_it = playlist[0]
        select_PL(track_id_list[0])
    else:
        play_it = playlist[x2 + 1]
        select_PL(track_id_list[x2 + 1])
    progress_bar['value'] = 0.0
    progress_bar.update()
    mixer.music.load(play_it)
    mixer.music.play()
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)
    track_id_list.pop(selected_song)
    statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
    show_details(play_it)

def show_details(play_song):
    file_data = os.path.splitext(play_song)
    global progress_bar

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    elif file_data[1] == '.wav':
        audio = WavPack(play_song)
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()
        ##progress_bar['maximum'] = total_length

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
    global progress_bar
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
            current_time += 1
            progress_bar['value'] = current_time
            progress_bar.update()



def about_us():
    tkinter.messagebox.showinfo('About Music Player', 'This is a music player using Python Tkinter by Yasamin and Mobina')


def on_closing():
    stop_music()
    root.destroy()



root = tk.ThemedTk()
root.set_theme("black")
root.title("Music player")


statusbar = ttk.Label(root, text="Welcome to Music Player", relief=SUNKEN, anchor=W, font='Times 10 italic')
statusbar.pack(side = BOTTOM, fill = X)

# Create the menubar
menubar = Menu(root)
root.config(menu = menubar)

# Create the submenu
subMenu = Menu(menubar, tearoff = 0)

subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="More", menu=subMenu)
subMenu.add_command(label="About Us", command=about_us)

menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)

mixer.init()  # initializing the mixer


#frames
leftframe = Frame(root)
leftframe.pack(side=LEFT, padx=30, pady=30)

rightframe = Frame(root)
rightframe.pack(pady=30)

topframe = Frame(rightframe)
topframe.pack()

middleframe = Frame(rightframe)
middleframe.pack(pady=30, padx=30)

bottomframe = Frame(rightframe)
bottomframe.pack()

detailframe = Frame(root)
detailframe.pack(side = TOP)
detail_label = ttk.Label(detailframe)

playlistbox = Listbox(leftframe,bg = 'lightyellow3' )  #the box for showing the songs,contains just the filename
playlistbox.config(width=30,height=15)
playlistbox.pack()

#scrollbar
scrollbar = Scrollbar(leftframe, orient="vertical",command=playlistbox.yview)
scrollbar.pack(side="right", fill="y")
playlistbox.config(yscrollcommand=scrollbar.set)


#bottons
addBtn = ttk.Button(leftframe, text="+ Add Song", command=browse_file)
addBtn.pack(side=LEFT)

delBtn = ttk.Button(leftframe, text="- Del Song", command=del_song)
delBtn.pack(side=LEFT)

btnload = ttk.Button(leftframe, text="select folder", command=Load)
btnload.pack(side=LEFT)

playBtn = ttk.Button(middleframe, text = 'play', command=play_music)
playBtn.grid(row=0, column=0, padx=3)

stopBtn = ttk.Button(middleframe, text = 'stop', command=stop_music)
stopBtn.grid(row=0, column=1, padx=3)

pauseBtn = ttk.Button(middleframe,text = 'pause', command=pause_music)
pauseBtn.grid(row=0, column=2, padx=3)

restartBtn = ttk.Button(bottomframe, text = 'restart', command=restart_music)
restartBtn.grid(row=0, column=0)

rewindBtn = ttk.Button(bottomframe, text ='Prev', command=rewind_music)
rewindBtn.grid(row=0, column=1)

forwardBtn = ttk.Button(bottomframe, text = 'Next', command=forward_music)
forwardBtn.grid(row=0, column=2)

volumeBtn = ttk.Button(bottomframe, text = 'Mute', command=mute_music)
volumeBtn.grid(row=0, column=3)

global progress_bar
progress_bar = ttk.Progressbar(root, orient='horizontal',length=300)
progress_bar.place(x=100,y=100)
progress_bar.pack()

scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # implement the default value of scale when music player starts
mixer.music.set_volume(0.7)
scale.grid(row=0, column=4, pady=15, padx=30)



#labels
lengthlabel = ttk.Label(topframe, text='Total Length : --:--')
lengthlabel.pack(pady=5)

currenttimelabel = ttk.Label(topframe, text='Current Time : --:--', relief=GROOVE)
currenttimelabel.pack()






root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop() #for showing the window
