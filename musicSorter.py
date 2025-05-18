"""
\nA basic program intended to sort through music.
\nUses tkinter running with the Azure theme, https://github.com/rdbende/ttk-widget-factory
\nAuthor: Connor Nydam
\nIntended for use on Windows operating system, may work with others, not tested
\nApologies for lack of documentation within the code, it was a small project that soon ballooned further
"""

from tinytag import TinyTag as tag
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from datetime import datetime
import json

class Sorter(object):
    def __init__(self, unsortedDir: str, outputDir: str):
        self.unsortedDir = unsortedDir
        self.sortedDir = outputDir

        self.createdArtists = []
        self.createdAlbums = []
        self.output = ""

    def sort(self):
        songSuperList = []
        for folder in os.listdir(self.unsortedDir):
            folderDir = os.path.join(self.unsortedDir, folder)
            if os.path.isdir(folderDir): # if it is a folder

                for file in os.listdir(folderDir):
                    try:
                        song = tag.get(os.path.join(folderDir, file))

                        artist = self.removeInvalidCharacters(song.artist)
                        album = self.removeInvalidCharacters(song.album)
                        title = self.removeInvalidCharacters(song.title)

                        songSuperList.append([folder, artist, album, title, file])

                    except:
                        self.output = f"fail for file {file}"
            
            elif os.path.isfile(folderDir):
                try:
                    song = tag.get(folderDir)

                    artist = self.removeInvalidCharacters(song.artist)
                    album = self.removeInvalidCharacters(song.album)
                    title = self.removeInvalidCharacters(song.title)

                    songSuperList.append([None, artist, album, title, folder])
                except:
                    self.output = f"fail for {folder}"
        
        for song in songSuperList:
            self.artistFolderCreate(song[1])
        
        for song in songSuperList:
            self.albumFolderCreate(song[2], song[1])
        
        for song in songSuperList:
            self.copyAndrename(song[0], song[1], song[2], song[3], song[4])
    
    def artistFolderCreate(self, artist):
        try:
            os.mkdir(os.path.join(self.sortedDir, artist))
            self.output = f"Successfully created folder for {artist}"
            self.createdArtists.append(artist)
        except FileExistsError:
            return None
        except:
            self.output = f"Error 2: Folder creation error for {artist}"

    def albumFolderCreate(self, album, artist):
        try:
            os.mkdir(os.path.join(self.sortedDir, artist, album))
            self.output = f"Successfully made a folder for {album}"
            self.createdAlbums.append(album)
        except FileExistsError:
            return None
        except FileNotFoundError:
            self.output = f"Error 3: Parent file not found for {album}"
        except:
            self.output = f"Error 2: Failed creating folder for {album}"
    
    def copyAndrename(self, folder, artist, album, song, file):

        LocUnsortedDir = self.unsortedDir.replace("\\","/")
        LocSortedDir = self.sortedDir.replace("\\","/")

        if folder != None:
            src = f"{LocUnsortedDir}/{folder}/{file}"
        else:
            src = f"{LocUnsortedDir}/{file}"
        dst = f"{LocSortedDir}/{artist}/{album}"

        renamedDst = f"{LocSortedDir}/{artist}/{album}/{song}.mp3"
        renamedSRC = f"{LocSortedDir}/{artist}/{album}/{file}"
        try:
            shutil.copy2(src, dst)
            shutil.move(renamedSRC, renamedDst)
        except FileExistsError:
            self.output = f"{song} Already Exists!"
        except FileNotFoundError:
            self.output = f"Error finding {song}, {src}, {dst}"
        except:
            self.output = self.unsortedDir + file
            self.output = f"Error copying {song}"
    
    def removeInvalidCharacters(self, string: str):
        invalidCharacters = r'<>:/\|?"*'
        for char in invalidCharacters:
            string = string.replace(char, "")
        return string
    
    def __str__(self):
        return self.output
    
    def changeDir(self, unsorted, sorted):
        self.unsortedDir = unsorted
        self.sortedDir = sorted

class GUI(ttk.Frame):
    """A gui for the music sorter"""
    def __init__(self, parent):
        super().__init__(parent)

        # setting up variables
        self.unsortedDir = ""
        self.sortedDir = ""
        self.smallFont = font.Font(family="Arial", size=8)
        self.genFont = font.Font(family="Arial", size=12)
        self.boldFont = font.Font(family="Arial", size=18, weight="bold")
        self.sorter = Sorter("", "")
        self.sorter_previous = str(self.sorter)

        self.padX = 10
        self.padY = 8

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)

        # buttons
        self.buttonFrame = ttk.Frame(self, style="Card.TFrame")

        self.buttonFrame.columnconfigure(index=0, weight=1, uniform=1)
        self.buttonFrame.columnconfigure(index=0, weight=1)
        self.buttonFrame.rowconfigure(index=0, weight=1)
        self.buttonFrame.rowconfigure(index=1, weight=1)

        self.buttonFrame.pack(fill="both", expand=True)

        self.sortButton = ttk.Button(self.buttonFrame, text="Sort!", style="Accent.TButton", command=self.sort)
        self.changeDirButton = ttk.Button(self.buttonFrame, text="Change Directories", command=lambda: self.createConfigFile("Directory Change"))

        self.sortButton.pack(fill="both", expand=True, padx=self.padX, pady=self.padY)
        self.changeDirButton.pack(fill="both", expand=True, padx=self.padX, pady=self.padY)

        # output console
        #self.outputFrame = ttk.LabelFrame(self, text="Console")
        #self.outputFrame.grid(row=0, column=1, padx=self.padX, pady=self.padY, sticky="nsew")

        #self.outputBox = tk.Text(self.outputFrame, height=15, width=50, relief="flat", font=self.smallFont, state=tk.DISABLED)
        #self.outputBox.grid(row=0, column=0, sticky="nsew")

        self.checkConfigFile()

        self.updateOutput("Event", "Initialization Complete")
        
        self.updateStatus()

    def checkConfigFile(self):
        try:
            with open("./musicSorterConfig.json", "r") as file:
                data = json.load(file)
                self.sortedDir = data["sorted"]
                self.unsortedDir = data["unsorted"]

                if os.path.isdir(self.sortedDir) != True or os.path.isdir(self.unsortedDir) != True:
                    raise FileNotFoundError("Unsorted or Sorted Directory in config file does not exist")

                self.sorter.changeDir(self.unsortedDir, self.sortedDir)

                self.updateOutput("Event", "Config File Found, using saved directories")
        except:
            self.createConfigFile("No config found, please enter directories")
    
    def createConfigFile(self, errorMsg) -> None:
        self.messageBox = tk.Toplevel(self)
        inputFrame = ttk.LabelFrame(self.messageBox, text=errorMsg, padding=(10))
        inputFrame.grid(row=0, column=0, padx=10, pady=5)

        self.messageBox.title("Directory Change")
        self.messageBox.resizable(False, False)
        
        unsortedLabel = ttk.Label(inputFrame, text="Unsorted Directory", font=self.genFont)
        sortedLabel = ttk.Label(inputFrame, text="Sorted Directory", font=self.genFont)

        unsortedLabel.grid(row=0, column=0)
        sortedLabel.grid(row=0, column=1)

        unsortedEntry = ttk.Entry(inputFrame, font=self.genFont)
        sortedEntry = ttk.Entry(inputFrame, font=self.genFont)

        unsortedEntry.grid(row=1, column=0)
        sortedEntry.grid(row=1, column=1)

        submitButton = ttk.Button(self.messageBox, text="Submit", style="Accent.TButton", command=lambda:self.changeDir(unsortedEntry.get(), sortedEntry.get()))
        submitButton.grid(row=1, column=0)

    def changeDir(self, unsortedDir: str, sortedDir: str) -> bool:
        self.unsortedDir = unsortedDir
        self.sortedDir = sortedDir

        if os.path.isdir(self.unsortedDir) == True and os.path.isdir(self.sortedDir):
            self.messageBox.destroy()
            self.sorter.changeDir(self.unsortedDir, self.sortedDir)
            self.updateOutput("Event", f"Directories configured as {self.unsortedDir} and {self.sortedDir}")
                
            with open("./musicSorterConfig.json", "w") as file:
                dump = {
                    "sorted": self.sortedDir,
                    "unsorted": self.unsortedDir
                }
                json.dump(dump, file, indent=2)
        else:
            messagebox.showerror("Directory Error", "Invalid Directoy Submitted")
    
    def updateOutput(self, outputType, message):
        return None

        # This function is diabled because I cannot find out how to get the output console to work properly

        #self.outputBox.config(state=tk.NORMAL) 

        #self.outputBox.insert(tk.END, f"\n {outputType} at {datetime.now()} {message}")

        #self.outputBox.config(state=tk.DISABLED)
    
    def updateStatus(self):
        if str(self.sorter) != self.sorter_previous:
            self.sorter_previous = str(self.sorter)
            self.updateOutput("Event", str(self.sorter))
            print(self.sorter)
        self.after(1, self.updateStatus)
    
    def sort(self):
        if os.path.isdir(self.unsortedDir) != True or os.path.isdir(self.sortedDir) != True:
            self.checkConfigFile()
        else:
            self.sorter.sort()

def main():
    """Main function for running"""
    root = tk.Tk()
    root.title("Music Sorter")
    root.minsize(200,150)

    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    gui = GUI(root)
    gui.pack(expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()