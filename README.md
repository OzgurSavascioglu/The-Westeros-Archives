# The-Westeros-Archives
CMPE 321 Spring 2024 Project 4
The Westeros archive program consists of one program and one input. 
The program name is archive.py and the input name is input.txt. 
Program can be run as in the followed format:

python3 archive.py /full/path/of/input/file

Example:

python3 archive.py /Users/admin/python/CmpE321Project4/input.txt

When the archive.py file runs, it creates an output.txt to answer the search command in the same folder where the program is executed. In addition, log.txt file is created inside the root folder after the initial run. log.txt holds the time and result of every command given in the input file. Also, it creates westerosArchives database folder. Inside the folder, for every type created, there is a folder named after that type that includes a JSON file that holds primary key of the member of that type and multiple pages that holds information about records of that type. Besides the type folders, there is catalog.txt file inside westerosArchive. catalog.txt holds the names of the types.
