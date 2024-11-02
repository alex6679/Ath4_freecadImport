Macro for FreeCad for the import of Ath4 horn profiles.
Usage:
Ath4 Export:
Use the Grid coordinates export in the horn definition file.
E.g.:
GridExport:grid = {
ProfileRange = 0,100			; maximum value: Mesh.AngularSegments
SliceRange = 0,30				; maximum value: Mesh.LengthSegments
ExportProfiles = 1
ExportSlices = 1
Scale = 1.0
Delimiter = ";"
FileExtension = "csv"
SeparateFiles = 0      ; put everything into one file
}
In FreeCad:
Add the create_bspline_surface macro.
Run the macro. A file dialog opens. Choose the exported .csv file from Ath4 that contains the profiles.
Tested with FreeCad 0.21.2 and Ath 4.8.2.
