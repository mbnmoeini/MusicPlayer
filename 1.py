import tkinter as tkp
import os
from tkinter.filedialog import askdirectory   #To specify the dir of your playlist
from pygame import mixer
from pygame import *


#Main window
player = tkp.Tk()
player.title('Music player')
player.geometry("500x400")      #size
player.configure(background='gray')


playlist = tkp.Listbox()


def play():

    pygame.mixer.music.load(playlist.get(tkp.ACTIVE))
    var.set(playlist.get(tkp.ACTIVE))
    mixer.music.play()
    mixer.music.set_volume(volume.get())


def stop():
    mixer.music.stop()


def pause():
    mixer.music.pause()


def unpause():
    mixer.music.unpause()


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
            playlist.insert(i, item)
            i += 1


#bottons
btnload=tkp.Button(player, text="select folder", command=Load)
btnload.pack(fill="x")

btnplay = tkp.Button(player, text="play", command=play)     #making the botton
btnplay.pack(fill='x')       #showing the botton

btnstop = tkp.Button(player, text="Stop", command=stop)
btnstop.pack(fill='x')

btnpause = tkp.Button(player, text='Pause', command=pause)
btnpause.pack(fill='x')

btnunpause = tkp.Button(player, text='Continue Playing', command=unpause)
btnunpause.pack(fill='x')

#volume
volume = tkp.Scale(player, from_= 0, to_= 1, resolution= 0.1,  orient=tkp.HORIZONTAL, command=changeVolume )
volume.pack()


#music name
var = tkp.StringVar()
musictitle=tkp.Label(player,textvariable=var)
musictitle.pack()
playlist.pack()

player.mainloop()               #for showing the main window
