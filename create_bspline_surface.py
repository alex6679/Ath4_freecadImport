#exec(open('D:/Dropbox/HIFI/ATHSoftware/ath-latest-231015/export/FreeCadScript/create_bspline_surface.py').read())
#csv_file_path = 'D:/Dropbox/HIFI/multy_entry_horn_randy_parker/hornDesign/Ath4_Horns/firstTry/firstTry_profiles_grid_highRes.csv'
import FreeCAD as App
import FreeCADGui as Gui
import Part
import csv
from collections import defaultdict

# Prompt the user to select the CSV file
try:
    from PySide import QtGui  # For FreeCAD versions up to 0.18
except ImportError:
    from PySide2 import QtWidgets as QtGui  # For FreeCAD 0.19 and above

# Open a file dialog to select the CSV file
csv_file_path, _ = QtGui.QFileDialog.getOpenFileName(None, "Select CSV File", "", "CSV Files (*.csv)")

if not csv_file_path:
    print("No CSV file selected. Exiting.")
else:
    # Read the CSV file and parse it into profiles
    def read_profiles(file_path):
        profiles = []
        current_profile = []
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if not row or len(row) < 3:
                    if current_profile:
                        profiles.append(current_profile)
                        current_profile = []
                    continue  # Skip empty lines or incomplete data
                x, y, z = map(float, row)
                current_profile.append((x, y, z))
            if current_profile:
                profiles.append(current_profile)
        return profiles

    # Collect points at each Z-coordinate from all profiles
    def collect_points_by_z(profiles):
        z_values = sorted(set(point[2] for profile in profiles for point in profile))
        points_by_z = defaultdict(list)
        for z in z_values:
            for profile in profiles:
                # Find the point in the profile with the current Z-coordinate
                for point in profile:
                    if abs(point[2] - z) < 1e-6:
                        x, y, _ = point
                        points_by_z[z].append(App.Vector(x, y, z))
                        break
        return z_values, points_by_z

    # Create B-spline wires at each Z-coordinate with specified degree
    def create_wires(z_values, points_by_z, degree=3):
        doc = App.ActiveDocument
        if doc is None:
            doc = App.newDocument("LoftFromBsplines")

        wires = []
        for z in z_values:
            points = points_by_z[z]
            # Ensure the points form a closed loop
            if points[0] != points[-1]:
                points.append(points[0])

            # Create a periodic B-spline curve with specified degree
            bspline_curve = Part.BSplineCurve()
            periodic = True
            interpolate = True

            # Build the B-spline curve from poles
            bspline_curve.buildFromPoles(points, periodic, degree, interpolate)

            # Create an edge from the curve
            bspline_edge = bspline_curve.toShape()
            # Create a wire from the edge
            wire = Part.Wire([bspline_edge])
            wires.append(wire)

        doc.recompute()
        return wires

    # Create a loft connecting the wires
    def create_loft(wires):
        doc = App.ActiveDocument
        # Create the loft
        loft = Part.makeLoft(wires, True)  # True for solid loft, False for a shell
        # Add the loft to the document
        loft_obj = doc.addObject("Part::Feature", "Loft")
        loft_obj.Shape = loft
        doc.recompute()
        Gui.ActiveDocument.activeView().viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")
        print("Loft created successfully.")

    # Main execution
    profiles = read_profiles(csv_file_path)
    if not profiles or len(profiles) < 2:
        print("Need at least two profiles to create a loft.")
    else:
        z_values, points_by_z = collect_points_by_z(profiles)
        if not points_by_z:
            print("No valid data found.")
        else:
            wires = create_wires(z_values, points_by_z, degree=3)
            if len(wires) < 2:
                print("Need at least two wires to create a loft.")
            else:
                create_loft(wires)