Macro for FreeCad for the import of Ath4 horn profiles.
## Usage:
### Ath4 Export:
Use the Grid coordinates export in the horn definition file. <br>
E.g.: <br>
GridExport:grid = { <br>
ProfileRange = 0,100			; maximum value: Mesh.AngularSegments <br>
SliceRange = 0,30				; maximum value: Mesh.LengthSegments <br>
ExportProfiles = 1 <br>
ExportSlices = 1 <br>
Scale = 1.0 <br>
Delimiter = ";" <br>
FileExtension = "csv" <br>
SeparateFiles = 0      ; put everything into one file <br>
} <br>
### In FreeCad:
Add the create_bspline_surface macro. <br>
Run the macro. A file dialog opens. Choose the exported .csv file from Ath4 that contains the profiles. <br>
Tested with FreeCad 0.21.2 and Ath 4.8.2. <br>
