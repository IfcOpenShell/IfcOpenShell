import sys
sys.path.append('C:/cygwin64/home/moud308/Projects/IfcOpenShell/src/ifcblenderexport/io_export_ifc/')
import bpy
import time
import export
import os

print('# Starting export')
start = time.time()
ifc_export_settings = export.IfcExportSettings()
ifc_export_settings.bim_path = 'C:/cygwin64/home/moud308/Projects/IfcOpenShell/src/ifcblenderexport/io_export_ifc/'
ifc_export_settings.output_file = 'C:/cygwin64/home/moud308/Projects/New Folder/energy.ifc'
ifc_parser = export.IfcParser(ifc_export_settings)
ifc_schema = export.IfcSchema(ifc_export_settings)
qto_calculator = export.QtoCalculator()
ifc_exporter = export.IfcExporter(ifc_export_settings, ifc_schema, ifc_parser, qto_calculator)
ifc_exporter.export()
print('# Export finished in {:.2f} seconds'.format(time.time() - start))

