#!/usr/bin/python
#-*- coding:utf-8 -*-
"""CUB to G6 file(s) conversion tool

"""

import subprocess, tempfile, os, sys, zlib, zipfile


def _convert(g6_file, cub_file):
    """Convert a CUB Python File Object and write to a G6 Python File Object"""
    # Get number of vertices and degree
    n = int(g6_file.readline())

    """ dreadnaut commands generation """

    # Header, only consists in declaring the number of vertices
    header = "n=" + str(n) + '\n'

    # Parse the .cub file and generates commands for each line
    s = ""
    for line in g6_file :
        set = line.split()
        for v in set[1:4] :
            s += " "+ v
        s+= "; "

    # Create the final dreadnaut command string
    command = header + s[1:len(s)-2] + '.'

    """ dreadnaut temp file creation """

    temp = tempfile.NamedTemporaryFile()
    temp.write(command)
    temp.flush()

    """ dreadnaut to G6 conversion """
    # Works on Unix, TODO : Adapt for Windows
    subprocess.call("\"" +  os.getcwd() + "/\"" + "dretog " + temp.name + 
                    " \"" +  os.getcwd() + "/\"" + cub_file.name, shell = True)

    temp.close()


def main(file, zip=False, save_path=os.getcwd()):
    """Convert a CUB file or a folder to G6 file(s) or ZIP
    Arguments:
    file (string) -- filename of the file (or folder) to convert
    zip (boolean) -- used only if file is a folder, choose if converted files must
                     be zipped or saved directly in save_path, defaults to False
    save_path (string) -- where to save the G6 files, defaults to current working directory
    
    """
    
    if zip:
        zipname = os.path.normpath(os.path.join(save_path, os.path.splitext(file)[0]+'.zip'))
    
    # Test if we have a folder
    if os.path.isdir(file):
        if zip:
            with zipfile.ZipFile(zipname, 'w') as myzip:
                for root, dirs, files in os.walk(file):
                    for file in files:
                        g6_filename_arc = os.path.splitext(file)[0]+'.g6'
                        g6_filename = os.path.normpath(os.path.join(save_path, root, g6_filename_arc))
                        with open(g6_filename, 'wb') as g6_file:
                            _convert(f, g6_file)
                            myzip.write(g6_filename, g6_filename_arc)
                        os.remove(g6_filename)
        else:
            for root, dirs, files in os.walk(file):
                for file in files:
                    g6_filename_arc = os.path.splitext(file)[0]+'.g6'
                    g6_filename = os.path.normpath(os.path.join(save_path, root, g6_filename_arc))
                    g6_file = open(g6_filename, 'wb')
                    _convert(f, g6_file)
        
    # or a lone CUB file
    else:
        with open(file) as f:
            g6_filename_arc = os.path.splitext(file)[0]+'.g6'
            g6_filename = os.path.normpath(os.path.join(save_path, g6_filename_arc))
            if zip:
                with zipfile.ZipFile(zipname, 'w') as myzip:
                    with open(g6_filename, 'wb') as g6_file:
                        _convert(f, g6_file)
                        myzip.write(g6_filename, g6_filename_arc)
                    os.remove(g6_filename)
            else:
                g6_file = open(g6_filename, 'wb')
                _convert(f, g6_file)


# If script is called via command line, exec main with each argument if any,
# or print usage
if __name__ == "__main__":
    args = len(sys.argv)
    if args >= 3:
        if '-z' in sys.argv[1]:
            if args == 3:
                for argv in sys.argv[2:]:
                    main(argv, True)
            else:
                dest = sys.argv[-1]
                for argv in sys.argv[2:-1]:
                    main(argv, True, dest)
        else:
            dest = sys.argv[-1]
            for argv in sys.argv[1:-1]:
                main(argv, dest)
    elif args == 2:
        main(sys.argv[1])
    else:
        print("""Usage: cub2g6 FILE [FILE]... [DEST]
       cub2g6 -z FILE [FILE]... [DEST]
FILE can either be a CUB file or a folder containing CUB files.
DEST, if present, specifies the path where to save the converted file(s).

Beware, DEST must be present if there are multiple FILE.

Options:
-z: convert the file(s) and save as a ZIP file""")