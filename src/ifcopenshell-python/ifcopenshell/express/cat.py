import sys, fileinput

if sys.platform == "win32" and not hasattr(sys.stdout, 'buffer'):
    import os, msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

files = sys.argv[1:]
if files[0] == '-o':
    b = open(files[1], 'wb')
    files = files[2:]
else:
    b = getattr(sys.stdout, 'buffer', sys.stdout)

for line in fileinput.input(files=files, mode='rb'):
    b.write(line)
