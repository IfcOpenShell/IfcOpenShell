###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

"""
Rough draft of a client application for the C++ IfcGeomServer binary
"""

import os
import numpy
import subprocess

from collections import namedtuple

class message_headers(object):
    HELLO = 0xff00
    IFC_MODEL = HELLO + 1
    GET = IFC_MODEL + 1
    ENTITY = GET + 1
    MORE = ENTITY + 1
    NEXT = MORE + 1
    BYE = NEXT + 1
    GET_LOG = BYE + 1
    LOG = GET_LOG + 1
    DEFLECTION = LOG + 1
    SETTING = DEFLECTION + 1
    
message = namedtuple("message", ("header", "contents"))
    
def process(geomserver_exe, ifc_filename):
        
    proc = subprocess.Popen([geomserver_exe], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    
    def cast(data, dtype, n=None):
        arr = numpy.frombuffer(data, dtype=dtype)
        if n is None: return arr[0]
        else: return arr

    def read(dtype, n=None):
        data = proc.stdout.read(dtype().nbytes * (n or 1))
        return cast(data, dtype, n)
        
    def read_message(header_assertion=None):
        header, size = read(numpy.int32, 2)
        assert header_assertion is None or header_assertion == header
        contents = b""
        if size > 0:
            contents = proc.stdout.read(size)
        return message(header, contents)
        
    def write(header, contents=None):
        if contents is None: contents = []
        proc.stdin.write(numpy.int32(header).tobytes())
        integers_as_int32 = list(map(lambda s: numpy.int32(s) if isinstance(s, int) else s, contents))
        to_bytes = list(map(lambda s: s.tobytes() if hasattr(s, 'tobytes') else s, integers_as_int32))
        total_length = numpy.int32(sum(map(len, to_bytes)))
        proc.stdin.write(total_length.tobytes())
        for b in to_bytes:
            proc.stdin.write(b)
        proc.stdin.flush()
        
    read_message(message_headers.HELLO)
    
    # @todo: no need to read the entire file in memory
    s = open(ifc_filename, "rb").read()
    
    write(message_headers.SETTING, [numpy.int32((1 << 4)), numpy.int32(1)]) 
    write(message_headers.IFC_MODEL, [numpy.int32(len(s)), s, b"\x00" * ((4 - (len(s) % 4)) % 4)])
        
    while True:    
        has_more = cast(read_message(message_headers.MORE).contents, numpy.int32) == 1        
        if not has_more: break        
        write(message_headers.GET)        
        print(read_message(message_headers.ENTITY).contents)        
        write(message_headers.NEXT)        
            
    write(message_headers.BYE)
    read_message(message_headers.BYE)
    proc.wait()
    assert proc.returncode == 0

if __name__ == "__main__":
    import sys
    import platform
    exe_extension = ".exe" if platform.system() == 'Windows' else ""
    exe = os.environ.get("IFCGEOMSERVER") or ("IfcGeomServer" + exe_extension)
    for fn in sys.argv[1:]:
        process(exe, fn)
