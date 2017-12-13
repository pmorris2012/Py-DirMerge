import os
import argparse
import shutil
import sys

ops = ['del-1-2','del-2-1','merge-1-2','merge-2-1','copy-1-2','copy-2-1', 'compare']

#https://stackoverflow.com/a/29988426
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def get_flist(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            yield os.path.join(root, f)

def get_unique(dir1, dir2, dir1_files, dir2_files):
    dir1_set = set([os.path.normpath(x.replace(dir1, '')) for x in dir1_files])
    dir2_set = set([os.path.normpath(x.replace(dir2, '')) for x in dir2_files])
    return [os.path.join(dir1, x) for x in (dir1_set - dir2_set)], [os.path.join(dir2, x) for x in (dir2_set - dir1_set)]

#logic from https://gist.github.com/jacobtomlinson/9031697
def op_del_empty_dirs(path):
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                op_del_empty_dirs(fullpath)
    
    files = os.listdir(path)
    if len(files) == 0:
        uprint("Removing empty folder:", path)
        os.rmdir(path)

def op_del(files):
    for f in files:
        uprint("Deleting", f)
        os.remove(f)

def op_copy(files, from_dir, to_dir):
    for f in files:
        f_path = f.replace(from_dir, to_dir)
        if os.path.exists(f_path):
            continue
        uprint("copying", f_path.replace(to_dir, ''), "from", from_dir, "to", to_dir)
        os.makedirs(os.path.dirname(f_path), exist_ok=True)
        shutil.copyfile(f, f_path)

parser = argparse.ArgumentParser(description='Py-DirMerge v0.1: Cmd-line cross platform alternative to slow ass WinMerge - Warning: goes by file names only')
parser.add_argument('dir1', help='absolute path of the first directory to compare')
parser.add_argument('dir2', help='absolute path of the second directory to compare')
parser.add_argument('ops', type=str, choices=ops, nargs='+', help='Specify any number of operations to perform from the list:\n del-1-2: delete all files in 2 which are not in 1\n del-2-1: delete all files in 1 which are not in 2\n merge-1-2: move files in 1 to 2, without replacement\n merge-2-1: move files in 2 to 1, without replacement\n copy-1-2: move files in 1 to 2, with replacement\n copy-2-1: move files in 2 to 1, with replacement\n compare: display dir info')

args = parser.parse_args()
args.dir1 = os.path.join(args.dir1, '')
args.dir2 = os.path.join(args.dir2, '')

for op in args.ops:
    dir1_files = list(get_flist(args.dir1))
    dir2_files = list(get_flist(args.dir2))
    dir1_uniq, dir2_uniq = get_unique(args.dir1, args.dir2, dir1_files, dir2_files)

    uprint("--------\n")
    uprint("found", len(dir1_files), "files, with", len(dir1_uniq), "unique files, in dir1")
    uprint("found", len(dir2_files), "files, with", len(dir2_uniq), "unique files, in dir2")

    if op == 'del-1-2':
        uprint("deleting", len(dir2_uniq), "unique files from dir2.")
        op_del(dir2_uniq)
        op_del_empty_dirs(args.dir2)
    elif op == 'del-2-1':
        uprint("deleting", len(dir1_uniq), "unique files from dir1.")
        op_del(dir1_uniq)
        op_del_empty_dirs(args.dir1)
    elif op == 'merge-1-2':
        uprint("copying", len(dir1_uniq), "unique dir1 files to dir2.")
        op_copy(dir1_uniq, args.dir1, args.dir2)
    elif op == 'merge-2-1':
        uprint("copying", len(dir2_uniq), "unique dir2 files to dir1.")
        op_copy(dir2_uniq, args.dir2, args.dir1)
    elif op == 'copy-1-2':
        uprint("copying all", len(dir1_files), "dir1 files to dir2.")
        op_copy(dir1_files, args.dir1, args.dir2)
    elif op == 'copy-2-1':
        uprint("copying all", len(dir2_files), "dir2 files to dir1.")
        op_copy(dir2_files, args.dir2, args.dir1)
    elif op == 'compare':
        pass
