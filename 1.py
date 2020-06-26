import tkinter as tkp
import os
from tkinter.filedialog import askdirectory   #To specify the dir of your playlist
import pygame

#Main window
player = tkp.Tk()                #building the main window
player.title('Music player')
player.geometry("500x400")      #size !
player.configure(background='gray')

#pygame init
pygame.init()  #using this module for playing sounds
pygame.mixer.init()
playlist = tkp.Listbox()


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


def play():

    pygame.mixer.music.load(playlist.get(tkp.ACTIVE))
    var.set(playlist.get(tkp.ACTIVE))
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(volume.get())


var = tkp.StringVar()
musictitle=tkp.Label(player,textvariable=var)
musictitle.pack()
playlist.pack()


#bottons
btnload=tkp.Button(player, text="select folder", command=Load)
btnload.pack(fill="x")

btnplay = tkp.Button(player, text="play", command=play)     #making the botton
btnplay.pack(fill='x')       #showing the botton


player.mainloop()               #for showing the main window
