#!/usr/bin/env python3


"""\
This script can be executed while inside a MTB project folder, in order to list dependency changes
in its workspace's mtb_shared/* folders.
The list of dependencies is specified in the project's "dep/*.mtb"
https://github.com/mtb04313/mtb_scripts/get_dep_changes.py
"""
from __future__ import print_function
import sys, time
import logging
import datetime
import os
import glob
import re
from git import Repo


DEPS_FOLDER = 'deps'
DEP_COL_INDEX_PATH = 2
DEP_NUM_OF_COLUMNS = 3
DEP_COL_0_EXPECTED_VALUE = '$$ASSET_REPO$$'
ASSET_FOLDER = 'mtb_shared'
BSPS_FOLDER = '/bsps/'
CLEAN_REPO_MESSAGE = 'nothing to commit, working tree clean'


def parseArgs():
    """ Argument parser for Python 2.7 and above """
    from argparse import ArgumentParser
    parser = ArgumentParser(description='List code changes in mtb_shared sub-folders, which have not been committed')
    parser.add_argument('-d', '--debug',  action='store_true', help='dump debug information (for development)')
    parser.add_argument('-c', '--color',  action='store_true', help='use colored logs')
    parser.add_argument('-f', '--file',  action='store_true', help='log to file: out.log')
    return parser.parse_args()

def parseArgsPy26():
    """ Argument parser for Python 2.6 """
    from gsmtermlib.posoptparse import PosOptionParser, Option
    parser = PosOptionParser(description='List code changes in mtb_shared sub-folders, which have not been committed')
    parser.add_option('-d', '--debug',  action='store_true', help='dump debug information (for development)')
    parser.add_option('-c', '--color',  action='store_true', help='use colored logs')
    parser.add_option('-f', '--file',  action='store_true', help='log to file: out.log')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Incorrect number of arguments, e.g. {0}'.format(sys.argv[0]))
    else:
        options.port = args[0]
        return options


def load_dependency(filePath):
    """ load a dependency file and return its folder path """
    #print(filePath)

    input_file = open(filePath, 'r')
    all_lines = input_file.readlines()
    
    for line in all_lines:
        #print(line)
        if (not line.startswith('#')):
            x = re.split("#", line.strip())

            if (len(x) != DEP_NUM_OF_COLUMNS):
                print(x)
                assert(len(x) == DEP_NUM_OF_COLUMNS)

            result = x[DEP_COL_INDEX_PATH] 

            if (not result.startswith(DEP_COL_0_EXPECTED_VALUE)):
                print(result)
                assert(result.startswith(DEP_COL_0_EXPECTED_VALUE))
            
            result = result[len(DEP_COL_0_EXPECTED_VALUE) :]
            return result

    return ''

def find_asset_shared_folder(cur_folder):
    """ locate the 'mtb_shared' folder relative to current folder """

    parent = os.path.dirname(cur_folder)
    #print(parent)

    result = os.path.join(parent, ASSET_FOLDER)
    if (os.path.exists(result)):
        return result

    else:
        parent = os.path.dirname(parent)
        result = os.path.join(parent, ASSET_FOLDER)

        if (os.path.exists(result)):
            return result
        else:
            result = ''

    return result


def find_deps_folder(cur_folder):
    """ locate the 'deps' folder relative to current folder """

    result = []
    for root, dirs, files in os.walk(cur_folder):
        for folder in dirs:
            if (DEPS_FOLDER == folder):
                #print(folder)
                # ignore 'deps' under 'bsps' tree
                if (not BSPS_FOLDER in root):
                    result.append(os.path.join(root, folder))

    #print(result)
    return result


def process_dependencies():
    """ process dependencies *.mtb """
    #print('process_dependencies')

    cur_folder = os.getcwd()  #os.path.abspath(os.path.dirname(__file__))
    #print(cur_folder)

    asset_folder = find_asset_shared_folder(cur_folder)
    #print(asset_folder)
    if (asset_folder == ''):
        print("Error: cannot find '" + ASSET_FOLDER + "' folder")
        #assert(asset_folder != '')
        return

    deps_folders = find_deps_folder(cur_folder)
    if (len(deps_folders) == 0):
        print("Error: cannot find 'deps' folder")
        return

    #print(deps_folders)
    #quit()

    mtb_pattern = '*.mtb'
    count = 0

    for folder in deps_folders:
        #print(folder)
        print("--- " + os.path.basename(os.path.dirname(folder)) + "/" + DEPS_FOLDER + " ---")

        mtb_files = sorted(glob.glob(os.path.join(folder, mtb_pattern)))
        #print(mtb_files)

        for mtb_filepath in mtb_files:
            location = load_dependency(mtb_filepath)
          
            repo = Repo(asset_folder + location)
            status_result = repo.git.status()

            if (CLEAN_REPO_MESSAGE in status_result):
                print('[OK] ' + asset_folder + location)
            else:
                print('\n' + asset_folder + location)
                print(status_result + '\n')
                count += 1
  
    if (count):
        print('=====================================')
        print(str(count) + ' deps have uncommitted changes!')
        print('=====================================')


def main():
    """ main program """
    args = parseArgsPy26() if sys.version_info[0] == 2 and sys.version_info[1] < 7 else parseArgs()
    #print ('args:',args)

    my_logger = logging.getLogger(__name__)
    
    if (args.file):
        now = datetime.datetime.now(datetime.timezone.utc)  # GMT time
        #now = datetime.datetime.now()  # local time
        my_logger.log(logging.CRITICAL, now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    
    process_dependencies()    


if __name__ == '__main__':
    main()

