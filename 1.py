import tkinter as tkp
import os
from tkinter import *
from tkinter.filedialog import askdirectory   #To specify the dir of your playlist
import time
from tinytag import *
import threading
from pygame import mixer


#Main window
player = tkp.Tk()                #building the main window
player.title('Music player')
player.geometry("500x500")      #size !
player.configure(background='peachpuff')


mixer.init()  # initializing the mixer


paused = FALSE


playlistbox = tkp.Listbox()

def play():
    global paused
    if paused:
        mixer.music.unpause()
        paused = FALSE
    else:
        mixer.music.load(playlistbox.get(tkp.ACTIVE))
        show_detail(playlistbox.get(tkp.ACTIVE)) #for showing music metadata
        var.set(playlistbox.get(tkp.ACTIVE))
        mixer.music.play()
        mixer.music.set_volume(volume.get())


def stop():
    mixer.music.stop()


def pause():
    global paused
    paused = TRUE
    mixer.music.pause()


def changeVolume(a):
    a = volume.get()
    mixer.music.set_volume(a)


def Load():
    #set the dir
    directory = askdirectory()
    os.chdir(directory)
    musiclist = os.listdir(directory)   #listing the music content
    for item in musiclist:
        if item.endswith('.mp3') or item.endswith('.wav'):
            i = 0
            playlistbox.insert(i, item)
            i += 1


def show_detail(playing_song):
    item = TinyTag.get(playing_song)
    total_length = item.duration
    mins, secs = divmod(total_length, 60)        # div - total_length/60, mod - total_length % 60
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)

    lengthlabel = tkp.Label(player, text='Total Length : --:--')
    lengthlabel.grid(row=8, column=0)
    lengthlabel['text'] = "Total Length" + ' - ' + timeformat

    tag1 = item.filesize/(10**6)
    sizelabel = tkp.Label(player, text='size :  {} Mb'.format(tag1))
    sizelabel.grid(row = 9, column = 0)



#bottons
btnload=tkp.Button(player, text="select folder", command=Load, background = "rosybrown2")
btnload.grid(row = 1, padx =120, ipadx = 50)

playlistbox.grid(row=2, padx= 150, ipadx = 50)

btnplay = tkp.Button(player, text="play", command=play, background="lightcyan2")     #making the botton
btnplay.grid(row = 3, sticky = N+S+E+W)      #showing the botton

btnstop = tkp.Button(player, text="Stop", command=stop,  background="lightcyan3")
btnstop.grid(row = 4, sticky = N+S+E+W)

btnpause = tkp.Button(player, text='Pause', command=pause,  background="lightcyan2")
btnpause.grid(row = 5, sticky = N+S+E+W)

#volume
volume = tkp.Scale(player, from_= 0, to_= 1, resolution= 0.1,  orient=tkp.HORIZONTAL, command=changeVolume, background='mediumpurple1' )
volume.grid(row = 6, padx = 150, pady = 10)


#music name
var = tkp.StringVar()
musictitle=tkp.Label(player,textvariable=var)
musictitle.grid(row = 7, padx = 200)






player.mainloop()               #for showing the main window
