#!/usr/bin/env python3
'''
Created in December 2017

Read the package directory under /var/db/pkg - get a list of all
packages containing .a files, then emerge them.

@author: wjb
'''

import os.path
import sys
from glob import glob
from argparse import ArgumentParser


def is_version(s):
    """
    Looks at the given string and decides whether it is a valid version
    number or not. The syntax is too demented for a regular expression.

    from: https://devmanual.gentoo.org/ebuild-writing/file-format/
    """
    idx = 0
    types = ('alpha','beta','pre','rc','p')

    if not s[idx].isdigit():
        return False

    while s[idx].isdigit():
        idx += 1
        if idx >= len(s):
            return True

    while s[idx] == '.':
        idx += 1
        if idx >= len(s):
            return False
        if not s[idx].isdigit():
            return False
        while s[idx].isdigit():
            idx += 1
            if idx >= len(s):
                return True

    if s[idx]>='a' and s[idx]<='z':
        idx += 1
        if idx >= len(s):
            return True

    if idx >= len(s):
        return True

    while idx<len(s) and s[idx] == '_':
        idx += 1
        if idx >= len(s):
            return False
        typ = ''
        while idx<len(s) and s[idx]>='a' and s[idx]<='z':
            typ += s[idx]
            idx += 1
        if typ not in types:
            return False
        if idx >= len(s):
            return True
        num = ''
        while idx<len(s) and s[idx].isdigit():
            num += s[idx]
            idx += 1

    if idx >= len(s):
        return True

    if s[idx] != '-':
        return False

    idx += 1
    if idx >= len(s):
        return False

    if s[idx] != 'r':
        return False

    idx += 1
    if idx >= len(s):
        return True

    num = ''
    while idx<len(s) and s[idx].isdigit():
        num += s[idx]
        idx += 1
    if idx >= len(s):
        return True

    return False



def splitname(packagever):
    """
    Given: name-123
    Return a tuple: (<name>, <version>)
    """

    dashes = [i for i,ltr in enumerate(packagever) if ltr=='-']

    package_name = None
    package_version = None

    for pos in dashes:
        if is_version(packagever[pos+1:]):
            package_name = packagever[:pos]
            package_version = packagever[pos+1:]
            break

    return (package_name, package_version)


def is_library(filename):
    """
    Return true if the filename ends in ".a"
    """
    return filename[-2:] == ".a"



class PackageDef:

    def __init__(self,category,packagever,slot):
        """
        packagever is: packagename-version
        """
        self.slot = slot

        (name,ver) = splitname(packagever)
        self.category = category
        self.name = name
        self.version = ver

    @property
    def fullname(self):
        return self.category + '/' + self.name

    @property
    def fullnamever(self):
        return self.category + '/' + self.name + '-' + self.version



# Parse the command line options
#
parser = ArgumentParser(description="Remerge packages containing static libraries")

parser.add_argument('-a','--ask',
                    action="store_true",
                    dest="ask",
                    default=False,
                    help="Stop and ask before starting emerge")
parser.add_argument('-p','--pretend',
                    action="store_true",
                    dest="pretend",
                    default=False,
                    help="Just pretend, do not carry out any builds")
parser.add_argument('-P','--pump',
                    action="store_true",
                    dest="pumpmode",
                    default=False,
                    help="Use pump (distcc)")
args = parser.parse_args()

# Now find the packages ...

rootpath = r'/var/db/pkg'
packagelist = []

filelist = glob(r'/var/db/pkg/*/*/CONTENTS')

for fname in filelist:
    split = fname.split(r'/')
    category = split[-3]
    package = split[-2]  # includes the version number

    with open(fname,"r") as contents:
        for line in contents:
            fields = line.split(' ')
            if len(fields)>=2 and fields[0]=="obj" and is_library(fields[1]):

                # get the slot number of the package
                slot_name = os.path.join(rootpath,category,package,'SLOT')
                if os.path.exists(slot_name):
                    with open(slot_name,"r") as fh:
                        slot = fh.readline().strip()
                        slot = slot.split('/')[0]
                else:
                    slot = "0"

                # add the package to the list and end this loop
                packagelist.append(PackageDef(category, package, slot))
                break

command = 'emerge --quiet --quiet-build'
if args.ask:
    command += ' --ask'
if args.pretend:
    command += ' --pretend'
command += ' --oneshot'

if args.pumpmode:
    command = "pump " + command

for pkg in packagelist:
    command += ' {0}:{1}'.format(pkg.fullname,pkg.slot)

print("Found {} packages".format(len(packagelist)))
print(command)

# Run the emerge command
args = command.split(' ')
os.execvp(args[0],args)
