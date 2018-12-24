from __future__ import print_function
import os
import os.path

def walk_dir(rootdir):
    for parent,dirnames,filenames in os.walk(rootdir):  #three parameters return 1.parent directory, 2.directorys, 3.files
        #for dirname in dirnames:                       #display directory information
        #    print("parent is:" + parent)
        #    print("dirname is" + dirname)

        for filename in filenames:                      #display file information
            print("parent is:" + parent)
            print("filename is:" + filename)
            print("the full name of the file is:" + os.path.join(parent,filename)) #display file path information

rootdir = "D:\MySource\PythonSource\bidder_log\20151121"
print("root dir is:" + rootdir)
rootdir = raw_input("Please enter the root directory:\n")
walk_dir(rootdir)

for file_name in os.listdir(rootdir):
    print("file name: " + file_name)
