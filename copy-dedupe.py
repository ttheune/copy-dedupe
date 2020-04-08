#!/usr/bin/env python3

"""
This tool will copy the file tree from source to the same tree at destination
while checking to see if there is already a copy of that file somewhere at the destination.
If the file has a different name in another branch of the tree already at the destination
it will not be copied and report that it already exists.
Todo: find the location of the file that already exists and report it.

Usage: ./copy-dedupe.py --src [path/to/source] --dest [path/to/dest]
"""

import argparse
import hashlib
import os
from shutil import copyfile


# Determine the md5 hash of a file
def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Get a list of files in a given directory
def file_list(dir):
    files = []
    with os.scandir(dir) as dir_list:
        for item in dir_list:
            if item.is_file():
                files.append(item.name)
    return files


# Seed the MD5 hash list
def base_hash(dest):
    hash_list = []
    for root, dirs, files in os.walk(dest):
        for file in files:
            hash_list.append(md5(os.path.join(root, file)))
    return hash_list


# Copy one directory and update the hash list
def copy_dir(src, dest, base_hash):
    for file in file_list(src):
        src_path_file = src + '/' + file
        dest_path_file = dest + '/' + file
        hash = md5(src_path_file)
        if hash not in base_hash:
            base_hash.append(hash)
            copyfile(src_path_file, dest_path_file)
            print('Copied {} to {}'.format(src_path_file, dest_path_file))
        else:
            print('{} data already exists at target.'.format(src_path_file))
    return base_hash


# Process source dir tree
def walk_src(src_tree, dest_tree, base_hash):
    for dir in src_tree:
        copy_dir(dir, dest_tree[src_tree.index(dir)], base_hash)


# Return a relative tree path of source
def create_trees(src, dest, cut):
    src_tree = [src]
    dest_tree = []
    for root, dirs, files in os.walk(src):
        for dir in sorted(dirs):
            src_tree.append(os.path.join(root, dir))
    for dir in src_tree:
        dest_tree.append(dest + '/'.join(dir.split('/')[cut:]))
    return src_tree, dest_tree


# Build the relative tree path of source at destination
def make_dest_tree(dest_tree):
    for dir in dest_tree:
        try:
            os.makedirs(dir)
            print('Created {}'.format(dir))
        except FileExistsError:
            pass


# Get arguments from the command line
def get_args():
    parser = argparse.ArgumentParser(description='Copy files from source to destination while deduping')
    parser.add_argument('--src', required=True, help='Full path to source directory')
    parser.add_argument('--dest', required=True, help='Full path to destination directory')
    return parser.parse_args()


def main():
    args = get_args()
    src = args.src
    dest = args.dest
    if not dest.endswith('/'):
        dest = dest + '/'
    if not os.path.isdir(dest):
        os.makedirs(dest)
    if not os.path.isdir(src):
        print('{} does not exist.'.format(src))
        return
    cut = len(src.split('/')) - 1
    src_tree, dest_tree = create_trees(src, dest, cut)
    make_dest_tree(dest_tree)
    walk_src(src_tree, dest_tree, base_hash(dest))


if __name__ == '__main__':
    main()
