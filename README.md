# Akiba-Tools

Tools to mod Akiba's Trip.

# Volume.py

Allows to extract the files from the main archive (volume.dat) and import modified files to it.

Extract files:

```
py Volume.py -e <volume.dat path> <extraction folder>
```

Import files:

```
py Volume.py -i <original volume.dat path> <folder with modified files> <new volume.dat path>
```

The folder containing your modified files don't need to contain all the files of the original volume.dat path. Actually, it will be much faster if only the files that you actually modified are in it. The path of the new volume.dat file can't be the same than the path of the original file.

# AkibaMSG.py

Allows to extract the text from the different text files and import the modified text to them.

Extract text:

```
py Volume.py -e <lang path> <extraction folder>
```

The lang_path is the path from a lang folder, for example if you extracted the volume.dat file to a "volume" folder, set lang path to "volume/lang_us" in order to extract the english text.

Import text:

```
py Volume.py -i <original lang path> <extraction folder> <new lang path>
```