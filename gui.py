from tkinter import *
from tkinter import filedialog
import convert_dict
import convert_vocab
import os
import subprocess


root = Tk()
root.title("Kindle to Anki exporter")
root.geometry("600x150")



def saveDict():
    saveDict.dictPath = filedialog.askopenfilename(initialdir="/Users/emileberhard/Desktop", title="Select Dictionary File", filetypes=(("HTML files", "*.html"),))
    print("The dictionary file has been set.\n")

def convert_dictionary():
    convert_dict.main(dictPath, "dict.tsv")

def saveDB():
    saveDB.DBPath = filedialog.askopenfilename(initialdir="/Users/emileberhard/Desktop", title="Select Vocab.db File", filetypes=(("DB files", "*.db"),))
    print("The vocab.db file has been set.\n")

def convert_vocabulary():
    print("Converting Vocabulary")

def startConvtoAnki(dictPath, DBPath):
    try:
        #convert_dict.main(dictPath, "dict.tsv")
        dict_tsv = "dict.tsv"
        notes_tsv = open("notes.tsv", "w")

        convert_vocab.main(saveDB.DBPath, dict_tsv, notes_tsv)
    except Exception as e:
        raise



my_label2 = Label(root, text="Welcome! Please select your dictionary file (in .html format) and your vocab.db file\n(Please Google how to find your Kindle's vocab.db file if you don't have it...)\n")
my_label2.pack()
vocabChooser = Button(root, text="Choose Vocab File (.DB)", command=saveDB).pack()
dictChooser = Button(root, text="Choose Dictionary File (.HTML)", command=saveDict).pack()
startButton = Button(root, text="Start", command=lambda:startConvtoAnki(saveDict.dictPath, saveDB.DBPath)).pack()


root.mainloop()
