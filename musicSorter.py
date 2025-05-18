"""Sorts through the mess of file I have for music"""

from tinytag import TinyTag as tag
import os
import shutil
import tkinter as tk

class Sorter(object):
    def __init__(self, unsortedDir: str, outputDir: str):
        self.unsortedDir = unsortedDir
        self.sortedDir = outputDir

        self.createdArtists = []
        self.createdAlbums = []

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
                        print(f"fail for file {file}")
            
            elif os.path.isfile(folderDir):
                try:
                    song = tag.get(folderDir)

                    artist = self.removeInvalidCharacters(song.artist)
                    album = self.removeInvalidCharacters(song.album)
                    title = self.removeInvalidCharacters(song.title)

                    songSuperList.append([None, artist, album, title, folder])
                except:
                    print(f"fail for {folder}")
        
        for song in songSuperList:
            self.artistFolderCreate(song[1])
        
        for song in songSuperList:
            self.albumFolderCreate(song[2], song[1])
        
        for song in songSuperList:
            self.copyAndrename(song[0], song[1], song[2], song[3], song[4])
    
    def artistFolderCreate(self, artist):
        try:
            os.mkdir(os.path.join(self.sortedDir, artist))
            print(f"Successfully created folder for {artist}")
            self.createdArtists.append(artist)
        except FileExistsError:
            return None
        except:
            print(f"Error 2: Folder creation error for {artist}")

    def albumFolderCreate(self, album, artist):
        try:
            os.mkdir(os.path.join(self.sortedDir, artist, album))
            print(f"Successfully made a folder for {album}")
            self.createdAlbums.append(album)
        except FileExistsError:
            return None
        except FileNotFoundError:
            print(f"Error 3: Parent file not found for {album}")
        except:
            print(f"Error 2: Failed creating folder for {album}")
    
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
            print(f"{song} Already Exists!")
        except FileNotFoundError:
            print(f"Error finding {song}, {src}, {dst}")
        except:
            print(self.unsortedDir + file)
            print(f"Error copying {song}")
    
    def removeInvalidCharacters(self, string: str):
        invalidCharacters = r'<>:/\|?"*'
        for char in invalidCharacters:
            string = string.replace(char, "")
        return string

class CLI(Sorter):
    def __init__(self) -> None:

        print("Welcome to musicSorter, please define the working directories")

        while True:
            self.unsortedDir = input("\nUnsorted Music >>> ")
            if os.path.isdir(self.unsortedDir):
                break
            else:
                print("Error finding folder")

        while True:
            self.outputDir = input("\nOutput >>> ")
            if os.path.isdir(self.outputDir):
                break
            else:
                print("Error finding folder")

        super().__init__(self.unsortedDir, self.outputDir)

        print("File directories found! Please use sort to sort the files,\n "\
            + "or you can type help to list all commands")
        
        self.main()

    def main(self) -> None:
        """Main loop of the program"""
        commandList = {
            "sort": "self.sort()",
            "changeInput": "self.changeInput()",
            "changeOutput": "self.changeOutput()",
            "help": "self.help()",
            "quit": "break"
        }
        while True:
            command = input("\n >>> ")
        
            if command in commandList:
                eval(commandList[command])
            else:
                print("Command Not Found")

    def help(self) -> None:
        """Returns all the commands in a neat list"""
        help_dict = {
            "sort": "Sorts all files in the specified directories",
            "changeInput": "Changes the specified input directory",
            "changeOutput": "Changes the specified output directory",
            "quit": "quits the current program"
        }

        for key, value in help_dict.items():
            print(key + "   ---     " + value)
    
    def changeInput(self) -> None:
        print(f"\ncurrent unsorted directory is {self.unsortedDir}\n")
        newDir = input("New Directory >>> ")

        if newDir == "":
            return None
        elif os.path.isdir(newDir):
            self.unsortedDir = newDir
            super().__init__(self.unsortedDir, self.sortedDir)
        else:
            print("Error finding folder")

    def changeOutput(self) -> None:
        print(f"\ncurrent unsorted directory is {self.outputDir}\n")
        newDir = input("New Directory >>> ")

        if newDir == "":
            return None
        elif os.path.isdir(newDir):
            self.sortedDir = newDir
            print("Change Complete!")
            super().__init__(self.unsortedDir, self.sortedDir)
        else:
            print("Error finding folder")
    
    def sort(self):
        super().sort()
        
if __name__ == "__main__":
    CLI()