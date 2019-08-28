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
    
def cast(data, dtype, n=None):
    arr = numpy.frombuffer(data, dtype=dtype)
    if n is None: return arr[0]
    else: return arr

def read(stream, dtype, n=None):
    data = stream.read(dtype().nbytes * (n or 1))
    x = cast(data, dtype, n)
    # print(x)
    return x
    
def readString(s):
    l = read(s, numpy.int32)
    S = s.read(int(l)).decode('ascii')
    while (l % 4 != 0):
        s.read(1);
        l += 1
    # print(S)
    return S
    
def readDoubleArray(s):
    l = read(s, numpy.int32) // 8
    return read(s, numpy.float64, int(l))
    
def readByteBuffer(s):
    l = read(s, numpy.int32)
    return s.read(int(l))
    
class entity_contents(object):
    def __init__(self, data):
        import json
        from io import BytesIO
        s = BytesIO(data)
        
        self.structure = [
            ("id"              , read(s, numpy.int32)), 
            ("guid"            , readString(s)), 
            ("name"            , readString(s)), 
            ("type"            , readString(s)), 
            ("parentId"        , read(s, numpy.int32)), 
            ("matrix"          , readDoubleArray(s)), 
            ("repId"           , read(s, numpy.int32)), 
            ("positions"       , readByteBuffer(s)), 
            ("normals"         , readByteBuffer(s)), 
            ("indices"         , readByteBuffer(s)), 
            ("colors"          , readByteBuffer(s)), 
            ("materialIndices" , readByteBuffer(s)), 
            ("extendedData"    , json.loads(s.read().strip(b'\x00').decode('ascii').strip(' ')))
        ]
        
    def __getattr__(self, k):
        return [kv for kv in self.structure if kv[0] == k][0][1]
        
    def __repr__(self):
        def format(x):
            a, b = x
            if isinstance(b, bytes):
                b = "<bytes>"
            elif isinstance(b, dict):
                padding = " " * (len(a) + 2)
                b = ("\n".join("%s%%s: %%s" % padding % format(x) for x in b.items())).strip()
            return a, b
        return "ENTITY: \n" + "\n".join("%s: %s" % format(x) for x in self.structure)

content_factory = {
    message_headers.ENTITY: entity_contents
}     

identity = lambda x: x
        
def parse_contents(header, contents):
    return (content_factory.get(header, identity))(contents)
    
message = namedtuple("message", ("header", "contents"))
    
def process(geomserver_exe, ifc_filename):
        
    proc = subprocess.Popen([geomserver_exe], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            
    def read_message(header_assertion=None):
        header, size = read(proc.stdout, numpy.int32, 2)
        assert header_assertion is None or header_assertion == header
        contents = b""
        if size > 0:
            contents = proc.stdout.read(size)
            contents = parse_contents(header, contents)
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
        geom_data = read_message(message_headers.ENTITY).contents
        yield geom_data
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
        for geom_data in process(exe, fn):
            print(geom_data)
