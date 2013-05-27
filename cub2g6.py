#!/usr/bin/python
#-*- coding:utf-8 -*-
"""CUB to G6 file(s) conversion tool

Usage: cub2g6 FILE [FILE]... [DEST]
       cub2g6 -z FOLDER [FOLDER]... [DEST]
FILE can either be a CUB file or a folder containing CUB files.
FOLDER is a folder containing CUB files.
DEST, if present, specifies the path where to save the converted file(s).

Beware, DEST must be present if there are multiple FILE/FOLDER.

Options:
-z: convert the files in FOLDER and save as a ZIP file

"""

import subprocess, tempfile, os, sys, zlib, zipfile, logging


def _convert(cub_file, g6_file):
    """Convert a CUB Python File Object and write to a G6 Python File Object"""
    # Get number of vertices
    n = int(cub_file.readline())

    # dreadnaut commands generation
    # Header, only consists in declaring the number of vertices
    header = "n=" + str(n) + '\n'

    # Parse the .cub file and generates commands for each line
    s = ""
    for line in cub_file :
        set = line.split()
        for v in set[1:4] :
            s += " "+ v
        s+= "; "

    # Create the final dreadnaut command string
    command = header + s[1:len(s)-2] + '.'

    # dreadnaut temp file creation 
    temp = tempfile.NamedTemporaryFile()
    temp.write(command)
    temp.flush()

    # dreadnaut to G6 conversion
    subprocess.call("dretog " + temp.name + " \"" + 
                    g6_file.name + "\" ", shell = True)

    temp.close()


def main(file, zip=False, save_path=os.getcwd()):
    """main(file, zip=False, save_path=os.getcwd())
    
    Convert a CUB file or a folder to G6 file(s) or ZIP
    Arguments:
    file (string) -- filename of the file (or folder) to convert
    
    Keyword arguments:
    zip (boolean) -- used only if file is a folder, choose if converted files must
                     be zipped or saved directly in save_path (default: False)
    save_path (string) -- where to save the G6 files (default: current working directory)
    
    """
    
    if zip:
        zipname = os.path.normpath(os.path.join(save_path, os.path.basename(file)+'.zip'))
    
    # Test if we have a folder
    if os.path.isdir(file):
        if zip:
            try:
                root_file = file
                if not os.path.exists(os.path.split(zipname)[0]):
                    os.makedirs(os.path.split(zipname)[0])
                with zipfile.ZipFile(zipname, 'w') as myzip:
                    for root, dirs, files in os.walk(root_file):
                        for file in files:
                            (name, ext) = os.path.splitext(file)
                            if '.cub' in ext:
                                cub_filename = os.path.normpath(os.path.join(root, file))
                                with open(cub_filename) as cub_file:
                                    g6_filename_arc = os.path.join(root.replace(root_file, '').lstrip('/'), name+'.g6')
                                    g6_filename = os.path.normpath(os.path.join(save_path, root_file, g6_filename_arc))
                                    dest_directory = os.path.split(g6_filename)[0]
                                    if not os.path.exists(dest_directory):
                                        os.makedirs(dest_directory)
                                    with open(g6_filename, 'wb') as g6_file:
                                        _convert(cub_file, g6_file)
                                        myzip.write(g6_filename, g6_filename_arc)
                                    os.remove(g6_filename)
                                    try:
                                        os.removedirs(dest_directory)
                                    except:
                                        pass
            except Exception as e:
                logging.exception("Error while converting {}".format(zipname))
                os.remove(zipname)
                try:
                    os.removedirs(os.path.split(zipname)[0])
                except:
                    pass
        else:
            root_file = file
            for root, dirs, files in os.walk(file):
                for file in files:
                    (name, ext) = os.path.splitext(file)
                    if '.cub' in ext:
                        cub_filename = os.path.normpath(os.path.join(root, file))
                        with open(cub_filename) as cub_file:
                            g6_filename_arc = os.path.join(root.replace(root_file, '').lstrip('/'), os.path.splitext(file)[0]+'.g6')
                            g6_filename = os.path.normpath(os.path.join(save_path, g6_filename_arc))
                            dest_directory = os.path.split(g6_filename)[0]
                            if not os.path.exists(dest_directory):
                                os.makedirs(dest_directory)
                            try:
                                with open(g6_filename, 'wb') as g6_file:
                                    _convert(cub_file, g6_file)
                            except Exception as e:
                                logging.exception("Error while converting {}".format(g6_filename))
                                os.remove(g6_filename)
                                                        
    # or a lone CUB file
    else:
        (name, ext) = os.path.splitext(file)
        if '.cub' in ext:
            with open(file) as f:
                g6_filename = os.path.normpath(os.path.join(save_path, name+'.g6'))
                try:
                    with open(g6_filename, 'wb') as g6_file:
                        _convert(f, g6_file)
                except Exception as e:
                    logging.exception("Error while converting {}".format(g6_filename))
                    os.remove(g6_filename)
        else:
            print '{} must have a .cub extension to be converted'.format(file)


# If script is called via command line, exec main with each argument if any,
# or print usage
if __name__ == "__main__":
    args = len(sys.argv)
    if args >= 3:
        if '-z' in sys.argv[1]:
            if args == 3:
                main(sys.argv[2], True)
            else:
                dest = sys.argv[-1]
                for argv in sys.argv[2:-1]:
                    main(argv, True, dest)
        else:
            dest = sys.argv[-1]
            for argv in sys.argv[1:-1]:
                main(argv, save_path=dest)
    elif args == 2 and not '-z' in sys.argv[1]:
        main(sys.argv[1])
    else:
        print("""Usage: cub2g6 FILE [FILE]... [DEST]
       cub2g6 -z FOLDER [FOLDER]... [DEST]
FILE can either be a CUB file or a folder containing CUB files.
FOLDER is a folder containing CUB files.
DEST, if present, specifies the path where to save the converted file(s).

Beware, DEST must be present if there are multiple FILE/FOLDER.

Options:
-z: convert the files in FOLDER and save as a ZIP file""")
