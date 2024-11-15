import FreeCAD as App
import FreeCADGui as Gui
import Part
import csv
from collections import defaultdict

# Import QtWidgets from PySide2 for FreeCAD 0.19 and above
from PySide2 import QtWidgets, QtCore

# Open a file dialog to select the CSV file
csv_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select CSV File", "", "CSV Files (*.csv)")

if not csv_file_path:
    print("No CSV file selected. Exiting.")
else:
    # Create a custom dialog to set 'solid', 'ruled', and 'closed' parameters
    class LoftOptionsDialog(QtWidgets.QDialog):
        def __init__(self, parent=None):
            super(LoftOptionsDialog, self).__init__(parent)
            self.setWindowTitle("Loft Options")
            self.setMinimumWidth(200)

            # Create checkboxes
            self.solid_checkbox = QtWidgets.QCheckBox("Solid")
            self.solid_checkbox.setChecked(True)
            self.ruled_checkbox = QtWidgets.QCheckBox("Ruled")
            self.ruled_checkbox.setChecked(False)
            self.closed_checkbox = QtWidgets.QCheckBox("Closed")
            self.closed_checkbox.setChecked(False)

            # Create buttons
            self.ok_button = QtWidgets.QPushButton("OK")
            self.cancel_button = QtWidgets.QPushButton("Cancel")

            # Connect buttons
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

            # Layout
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.solid_checkbox)
            layout.addWidget(self.ruled_checkbox)
            layout.addWidget(self.closed_checkbox)

            button_layout = QtWidgets.QHBoxLayout()
            button_layout.addStretch(1)
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.cancel_button)

            layout.addLayout(button_layout)

            self.setLayout(layout)

    # Show the dialog and get user input
    dialog = LoftOptionsDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        # Get the user's choices
        solid = dialog.solid_checkbox.isChecked()
        ruled = dialog.ruled_checkbox.isChecked()
        closed = dialog.closed_checkbox.isChecked()
    else:
        print("Loft creation canceled by user.")
        sys.exit()
        
    # Read the CSV file and parse it into profiles
    def read_profiles(file_path):
        profiles = []
        current_profile = []
        lengthLast = -1
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
                lenghtCurrent=len(current_profile)
                if lengthLast != -1 and lenghtCurrent != lengthLast:
                    print("Found profile with different length: ", lenghtCurrent)
                    print("Last profile had length length: ", lengthLast)
                    
                lengthLast=lenghtCurrent
                profiles.append(current_profile)
        n=len(profiles)
        print("Read profiles: ", n)
        return profiles

    # Create B-spline wires at each Z-coordinate with specified degree
    def create_wires(profiles, degree=3):
        doc = App.ActiveDocument
        if doc is None:
            doc = App.newDocument("LoftFromBsplines")
        noWires=len(profiles[0])
        print("Number of wires: ", noWires)
        wires = []
        for i in range(noWires):
            pointsOfWire =[]
            for profile in profiles:
                pointsOfWire.append(App.Vector(profile[i][0], profile[i][1], profile[i][2]))
            # Ensure the points form a closed loop
            if pointsOfWire[0] != pointsOfWire[-1]:
                pointsOfWire.append(pointsOfWire[0])
            
            # Create a periodic B-spline curve with specified degree
            bspline_curve = Part.BSplineCurve()
            periodic = True
            interpolate = True

            # Build the B-spline curve from poles
            bspline_curve.buildFromPoles(pointsOfWire, periodic, degree, interpolate)

            # Create an edge from the curve
            bspline_edge = bspline_curve.toShape()
            # Create a wire from the edge
            wire = Part.Wire([bspline_edge])
            wires.append(wire)
            
        doc.recompute()
        return wires

    # Create a loft connecting the wires
    def create_loft(wires, solid=True, ruled=False, closed=False):
        doc = App.ActiveDocument
        # Create the loft
        maxDegree = 3
        loft = Part.makeLoft(wires, solid, ruled, closed, maxDegree)
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
        wires = create_wires(profiles, degree=3)
        if len(wires) < 2:
            print("Need at least two wires to create a loft.")
        else:
            create_loft(wires, solid=solid, ruled=ruled, closed=closed)