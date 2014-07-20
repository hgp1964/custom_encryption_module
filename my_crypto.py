__author__ = 'HGP'
"""
Inspired by
http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/

The examples and explation above made a relatively easy to write this module
The code code of eli was adapted and put into a module.  The keygeneration with the help of password has been integrated
in the functions. Still you will generate a new key for every file. So it should be reasonable safe. Functions were made
to encrypt and decrypt complete directories.

The program was written and tested on mac osx. So you may have to alter to code a little to make it compatible with
your own platform. Don't forget to check if you have the necessary modules installed in python. You will finds some todo
remarks in the code

Feel free to use and adapt the code. I you find errors or have suggestions for improvement contact me on my
tumblr blog.

A word of warning:
If a destination directory already exists it will be used and files with same name will be overwritten.
I am not a professional programmer. So check the code and backup your files when you take this for a testdrive.
You are completely one your own if something goes wrong. Then again what is Life without a challenge :)


"""
from Crypto.Cipher import AES
import os, random, struct,fnmatch,argparse

import hashlib

class mycrypt():
    def __init__(self,strength=32):
        self.strength = strength

    def strength(self):
        return self.__strength

    def setStrength(self,strength): # I didnot use this one yet
        self.__strength = strength


    def generate_key(self,PASSWORD):
        """
        generates a key that can be fed into encrypt and decrypt functions
        I guess it is unix and osx specifig
        """
        if PASSWORD is not None:
            password = PASSWORD
            key = hashlib.sha256(password).digest()
            response = "OK"
            return response, key
        else:
            print "You have fill something in as a password "
            return "BAD","You have to fill in "

    def encrypt_file_engine(self,key, in_filename, out_filename=None, chunksize=64*1024):
        """ Encrypts a file using AES (CBC mode) with the
            given key.

            key:
                The encryption key - a string that must be
                either 16, 24 or 32 bytes long. Longer keys
                are more secure.

            in_filename:
                Name of the input file

            out_filename:
                If None, '<in_filename>.enc' will be used.

            chunksize:
                Sets the size of the chunk which the function
                uses to read and encrypt the file. Larger chunk
                sizes can be faster for some files and machines.
                chunksize must be divisible by 16.
        """
        if not out_filename:
            out_filename = in_filename + '.enc'

        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))

    def decrypt_file_engine(self,key, in_filename, out_filename=None, chunksize=24*1024):
        """ Decrypts a file using AES (CBC mode) with the
            given key. Parameters are similar to encrypt_file,
            with one difference: out_filename, if not supplied
            will be in_filename without its last extension
            (i.e. if in_filename is 'aaa.zip.enc' then
            out_filename will be 'aaa.zip')
        """
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)

    def encrypt_file(self,PASSWORD,SOURCEFILE,DESTINATIONFILE=None,STRENGTH=None):
        """
        here the password is fed into the function
        :param PASSWORD:
        :param SOURCEFILE:
        :param DESTINATIONFILE:
        :param STRENGTH:
        """
        my_response, my_key = self.generate_key(PASSWORD)
        if my_response == "OK":
            self.encrypt_file_engine(my_key,SOURCEFILE,DESTINATIONFILE,64*1024)

    def decrypt_file(self,PASSWORD,FILETODECRYPT,FILENEWNAME=None,STRENGTH=None):
        """
        like the encrypt file the password is fed into the function

        :type self: object
        :param PASSWORD:
        :param FILETODECRYPT:
        :param FILENEWNAME:
        :param STRENGTH:
        """
        my_response, my_key = self.generate_key(PASSWORD)
        if my_response == "OK":
            self.decrypt_file_engine(my_key,FILETODECRYPT,FILENEWNAME,64*1024)

    def directory_walk(self,my_dirs, patterns='*', single_level=False, yield_folders=False):
        # Expand patterns from semicolon-separated string to list
        """
        This function takes all the directories you feed to it. Processes it and
        returns  information about the path, filename and file size.
        I found this one somewhere on the net
        :param my_dirs: a list of dirs [dir,dir2,dir3,etc]
        :param patterns: a searchpattern
        :param single_level:
        :param yield_folders:
        """
        patterns = patterns.split(';')
        for my_pad in my_dirs:
            for path, subdirs, files in os.walk(my_pad):
                if yield_folders:
                    files.extend(subdirs)
                files.sort()
                for name in files:
                    for pattern in patterns:
                        if fnmatch.fnmatch(name, pattern):
                            yield os.path.join(path,name)
                            break
                if single_level:
                    break

    def encrypt_directory(self,PASSWORD,MYPATH,DESTINATIONDIR=None):
        """
        The function tests if the destination directory exist, if not a directory is created
        The encrypted files get an extra extension .enc

        """
        # todo I easily make this a single lever operation (look at directory_walk)
        MYEXTENSION = ".enc"
        # todo make your own custom extension
        # todo maybe make a progressbar

        if os.path.exists(MYPATH):
            if DESTINATIONDIR is None:
                my_output_dir ="decrypted_dir"
                my_output_directory = os.path.join(MYPATH,my_output_dir)
                    # todo timestamp
                if os.path.exists(my_output_directory):
                    pass
                else:
                    os.mkdir(my_output_directory)
            else:
                if os.path.exists(DESTINATIONDIR):
                    my_output_directory = DESTINATIONDIR
                else:
                    os.mkdir(DESTINATIONDIR)
                    my_output_directory = DESTINATIONDIR

            length_of_source_path =  len(MYPATH)

            my_list_of_path =[]
            my_list_of_path.append(MYPATH) # the walk_dir function takes a list of dirs

            for my_file in self.directory_walk(my_list_of_path):
                destination_relativepath = my_file[length_of_source_path+1:] # +1 because i have to remove the preceding /
                destination_relative_dirname = os.path.dirname(destination_relativepath)
                destination_file_basename  = os.path.basename(my_file)

                my_destination_dirpath = os.path.join(my_output_directory,destination_relative_dirname)
                my_destination_fullpath = os.path.join(my_destination_dirpath,destination_file_basename)

                if not os.path.exists(os.path.join(my_output_directory,destination_relative_dirname)):
                    # print "I have to make: " , os.path.join(my_output_directory,destination_relative_dirname)
                    try:
                        os.mkdir(my_destination_dirpath)
                    except IOError as my_error:
                        print "something went wrong this {err} was raised".format(err = my_error)
                else:
                    # print "It was already there, ",os.path.join(my_output_directory,destination_relative_dirname)
                    # todo maybe I put in verbose option
                    pass
                self.encrypt_file(PASSWORD,my_file,my_destination_fullpath+MYEXTENSION)


            print "Done "
        else:
            print "No valid path the program will end"
            quit()
            # todo maybe build in a returncode

    def decrypt_directory_simple(self,PASSWORD,MYPATH,DESTINATIONDIR=None):
        """
        Simple decrypts the file und puts them in the same directory
        It works but I found it confusion
        """
        if os.path.exists(MYPATH):
            my_list_of_path =[]
            my_list_of_path.append(MYPATH) # the walk_dir function takes a list of dirs
            for my_file in self.directory_walk(my_list_of_path):
                self.decrypt_file(PASSWORD,my_file)
            print "Done decrypting {mypath}".format(mypath = MYPATH)

    def decrypt_directory(self,PASSWORD,MYPATH,DESTINATIONDIR=None):
        """
        decrypts the directory you feed into the function. If no destination directory is specified
        then a directory is made one level up in the path. This is to avoid recursion of the function. The function
        would get evermore new file to decrypt. This would lead to errors
        :param PASSWORD:
        :param MYPATH: The path you want to decrypt
        :param DESTINATIONDIR: The destination directory
        """
        MYEXTENSION = ".enc"
        if os.path.exists(MYPATH):
            if DESTINATIONDIR is None:
                my_output_dir ="decrypted_directory" # todo there is no overwrite protection
                one_dir_up,last_part_path= os.path.split(MYPATH) # we put the destination one level up
                if os.path.exists(one_dir_up):
                    my_output_directory = os.path.join(one_dir_up,my_output_dir) # you want to avoid recursion
                    # todo timestamo
                if os.path.exists(my_output_directory):
                    pass
                else:
                    os.mkdir(my_output_directory)
                    # todo if we come to here I should quit the path is unvalid
            else:
                if os.path.exists(DESTINATIONDIR):
                    my_output_directory = DESTINATIONDIR
                    pass
                else:
                    os.mkdir(DESTINATIONDIR)
                    my_output_directory = DESTINATIONDIR


            # todo I want to create a temp directory that mirrors the original directory  with the encrypted files
            length_of_source_path =  len(MYPATH)


            my_list_of_path =[]
            my_list_of_path.append(MYPATH) # the walk_dir function takes a list of dirs

            for my_file in self.directory_walk(my_list_of_path):
                destination_relativepath = my_file[length_of_source_path+1:] # +1 because i have to remove the preceding /
                destination_relative_dirname = os.path.dirname(destination_relativepath)
                destination_file_basename  = os.path.splitext(os.path.basename(my_file))[0] # the enc extension got off

                my_destination_dirpath = os.path.join(my_output_directory,destination_relative_dirname)
                my_destination_fullpath = os.path.join(my_destination_dirpath,destination_file_basename) # can be done in one function

                if not os.path.exists(os.path.join(my_output_directory,destination_relative_dirname)):
                    try:
                        os.mkdir(my_destination_dirpath)
                    except IOError as my_error:
                        print "something went wrong this {err} was raised".format(err = my_error)
                else:
                    # todo maybe I put in verbose option
                    pass


                self.decrypt_file(PASSWORD,my_file,FILENEWNAME=my_destination_fullpath)
            # todo could put i returncode here
        else:
            print "No valid path the program"
            quit()


if __name__ =='__main__':
    parser = argparse.ArgumentParser(description='Encrypt or decrypt a file or directory ')
    parser.add_argument('-a', action="store", dest="todo",\
                        help = "e encrypts your source  d decrypts the source")
    parser.add_argument('-p', action="store", dest="password",\
                        help = "Fill in your password")
    parser.add_argument('-s', action="store", dest="source",\
                        help = "fill in sourcefile or source directory")
    parser.add_argument('-d', action="store", dest="destination",default=None,\
                        help = "If nothing is filled in directories will be created")

    given_args = parser.parse_args()


    if given_args.todo == "encrypt"  or given_args.todo == "decrypt":
        print "Starting the program ...  \n"
        my_hider = mycrypt() # instantiate an object

        if os.path.exists(given_args.source):
            if os.path.isfile(given_args.source):
                if given_args.todo == "encrypt":
                    print "encrypt it"
                    my_hider.encrypt_file(PASSWORD=given_args.password,SOURCEFILE=given_args.source,\
                                          DESTINATIONFILE=given_args.destination)
                    print "Encrypted your file "
                else:
                    print "decrypt it"
                    my_hider.decrypt_file(PASSWORD=given_args.password,FILETODECRYPT=given_args.source,\
                                          FILENEWNAME=given_args.destination)
                    print "decrypted your file"
            elif os.path.isdir(given_args.source):
                if given_args.todo == "encrypt":
                    print "I am encrypting your direcory {mydir} ".format(mydir=given_args.source)
                    my_hider.encrypt_directory(PASSWORD=given_args.password,MYPATH=given_args.source,\
                                               DESTINATIONDIR=given_args.destination)
                    print "Succesfully encrypted your directory and saves result in {mydest} \n".format(mydest=given_args.destination)
                else:
                    print "I am decrypting your directory {mydir}".format(mydir=given_args.source)
                    my_hider.decrypt_directory(PASSWORD=given_args.password,MYPATH=given_args.source\
                                                   ,DESTINATIONDIR=given_args.destination)
                    if given_args.destination is not None:
                        print "Succesfully decrypted your directory and saved result in .. {mydest} .."\
                            .format(mydest=given_args.destination)
                    else:
                        print "Succesfully decrypted your directory and saved result a a sibling of your source directory"
        else:
            print "No valid file or directory given as source"

    else:
        print "Plese fill in -a encrypt  for encrypting or -a decrypt for decrypting"





