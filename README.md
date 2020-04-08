# copy-dedupe
Copy a directory while checking if a copy of any given file already exists at target location

This tool will copy the file tree from source to the same tree at destination
while checking to see if there is already a copy of that file somewhere at the destination.
If the file has a different name in another branch of the tree already at the destination
it will not be copied and report that it already exists.
Todo: find the location of the file that already exists and report it.

Usage: ./copy-dedupe.py --src [path/to/source] --dest [path/to/dest]
