IfcGeomServer
-------------

A command-line executable intended to be ran as a child process that receives an IFC model from stdin and will send binary geometry information of products found in the IFC file in separate messages on stdout. The advantage over conventional static or dynamic linking is that, in case the IfcOpenShell process would crash (either due to invalid input, heap overflow, bugs, ...), this does not affect the main process. Currently, the only implementation of a consumer for this process is the Java module over at: https://github.com/opensourceBIM/IfcOpenShell-BIMserver-plugin/blob/master/src/org/ifcopenshell/IfcGeomServerClient.java 
