#!/usr/bin/env python3

# Santiago Larrain
# slarrain@uchicago.edu

import sys

def remove (filename, no_comments=False):
    '''
    Removes the whitespace, tabs and empty lines in a file
    and creates an .out file with the same name.
    Optionally, it removes // comments too.
    '''

    with open(filename, 'r') as f:

        # Open the writefile
        outf = open (filename[:-3]+'out', 'w')

        #lines = [line for line in f]

        for line in f:

            #Removes whitespace
            line = line.replace(' ', '')

            #Removes tabs
            line = line.replace('\t', '')

            #Remove the comments if no-comments was an argument
            if no_comments:
                line = line.split('//', 1)[0]

            #Make all lines equal
            line = line.split('\n', 1)[0]

            #If its not an empty line
            if line and line != '\n':
                #Write the line to the outfile with newline at the end
                outf.writelines(line+'\n')

        outf.close()


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print ('Usage: python rws.py testfile.in no-comments')
    elif len(sys.argv) == 3 and sys.argv[2]=='no-comments':
        remove(sys.argv[1], True)
    elif len(sys.argv) == 2:
        remove(sys.argv[1])
    else:
        print ('Usage: python rws.py testfile.in no-comments')
