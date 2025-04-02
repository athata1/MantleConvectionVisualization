#!/usr/bin/env python

# Purdue CS530 - Introduction to Scientific Visualization
# Spring 2023

# PyQt6 version of pyqt5_demo.py

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QSlider, QGridLayout, QLabel, QPushButton, QTextEdit
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import argparse
import sys
from vtk_camera import save_camera, load_camera
import os
import numpy as np

frame_counter = 0

def make_isocontour(input_fle, left, right):
    # Step 1: Create a reader for NetCDF CF files
    reader = vtk.vtkNetCDFCFReader()
    reader.SetFileName(input_fle)
    reader.UpdateMetaData()

    # Step 2: Select the "temperature anomaly" variable to read
    selected_variable = "temperature anomaly"
    reader.SetVariableArrayStatus(selected_variable, 1)
    reader.Update()  # Update the reader to load the data

    # Step 3: Check the dataset structure and ensure the variable is accessible
    data = reader.GetOutput()
    if data is None:
        print("Reader output is empty. Check the file and variable selection.")
    else:
        print(f"Number of arrays in Cell Data: {data.GetCellData().GetNumberOfArrays()}")
        for i in range(data.GetCellData().GetNumberOfArrays()):
            print(f"Array {i}: {data.GetCellData().GetArrayName(i)}")

        # Step 4: Retrieve the temperature array from Cell Data
        temperature_array = data.GetCellData().GetArray(selected_variable)
        if temperature_array is None:
            print(f"Variable '{selected_variable}' not found in Cell Data.")
        else:
            # Get range of values
            min_temp, max_temp = temperature_array.GetRange()
            print(f"Temperature range: {min_temp} - {max_temp}")
            
            otf = vtk.vtkPiecewiseFunction()
            otf.AddPoint(min_temp, 1.0)
            otf.AddPoint(left, 0.0)
            otf.AddPoint(right, 0.0)
            
            ctf = vtk.vtkColorTransferFunction()
            ctf.AddRGBPoint(min_temp, 0.0, 0.0, 1.0)
            ctf.AddRGBPoint(max_temp, 1.0, 0.0, 0.0)
            
            volume_property = vtk.vtkVolumeProperty()
            volume_property.SetScalarOpacity(otf)
            volume_property.SetColor(ctf)
            volume_property.SetInterpolationTypeToLinear()
            
            # Lower threshold filter
            lower_threshold = vtk.vtkThreshold()
            lower_threshold.SetInputData(data)
            lower_threshold.SetLowerThreshold(0)  # Adjust this as needed
            lower_threshold.Update()


            # Upper threshold filter
            upper_threshold = vtk.vtkThreshold()
            upper_threshold.SetInputData(data)
            upper_threshold.SetUpperThreshold(0)  # Adjust this as needed
            upper_threshold.Update()
            
            # Combine both thresholded outputs
            combine_threshold = vtk.vtkAppendFilter()
            combine_threshold.AddInputData(lower_threshold.GetOutput())
            combine_threshold.AddInputData(upper_threshold.GetOutput())
            combine_threshold.Update()
            
            volumeMapper = vtk.vtkUnstructuredGridVolumeRayCastMapper()
            volumeMapper.SetInputConnection(combine_threshold.GetOutputPort())
            
            # Create a volume
            volume = vtk.vtkVolume()
            volume.SetMapper(volumeMapper)
            volume.SetProperty(volume_property)
            
            colorbar = vtk.vtkScalarBarActor()
            colorbar.SetLookupTable(ctf)
            colorbar.SetTitle(selected_variable)
            colorbar.SetNumberOfLabels(5)
            colorbar.SetLabelFormat("%4.2f")
            
            return [volume, colorbar, volume_property, min_temp, max_temp]
            

            
            
    
    
def save_frame(window, log):
    global frame_counter
    global args
    # ---------------------------------------------------------------
    # Save current contents of render window to PNG file
    # ---------------------------------------------------------------
    file_name = args.output + str(frame_counter).zfill(5) + ".png"
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    png_writer = vtk.vtkPNGWriter()
    png_writer.SetInputConnection(image.GetOutputPort())
    png_writer.SetFileName(file_name)
    window.Render()
    png_writer.Write()
    frame_counter += 1
    if args.verbose:
        print(file_name + " has been successfully exported")
    log.insertPlainText('Exported {}\n'.format(file_name))

def print_camera_settings(camera, text_window, log, ren):
    # ---------------------------------------------------------------
    # Print out the current settings of the camera
    # ---------------------------------------------------------------
    if os.path.exists('camera.json'):
        os.remove('camera.json')
    save_camera(camera, ren)
    text_window.setHtml("<div style='font-weight:bold'>Camera settings:</div><p><ul><li><div style='font-weight:bold'>Position:</div> {0}</li><li><div style='font-weight:bold'>Focal point:</div> {1}</li><li><div style='font-weight:bold'>Up vector:</div> {2}</li><li><div style='font-weight:bold'>Clipping range:</div> {3}</li></ul>".format(camera.GetPosition(), camera.GetFocalPoint(),camera.GetViewUp(),camera.GetClippingRange()))
    log.insertPlainText('Saved camera info\n')


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName('The Main Window')
        MainWindow.setWindowTitle('Simple VTK + PyQt5 Example')
        # in Qt, windows are made of widgets.
        # centralWidget will contains all the other widgets
        self.centralWidget = QWidget(MainWindow)
        # we will organize the contents of our centralWidget
        # in a grid / table layout
        # Here is a screenshot of the layout:
        # https://www.cs.purdue.edu/~cs530/projects/img/PyQtGridLayout.png
        self.gridlayout = QGridLayout(self.centralWidget)
        # vtkWidget is a widget that encapsulates a vtkRenderWindow
        # and the associated vtkRenderWindowInteractor. We add
        # it to centralWidget.
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        # Sliders
        self.contour_slider = QSlider()
        self.y_slider = QSlider()
        # Push buttons
        self.push_screenshot = QPushButton()
        self.push_screenshot.setText('Save screenshot')
        self.push_camera = QPushButton()
        self.push_camera.setText('Save camera info')
        self.push_quit = QPushButton()
        self.push_quit.setText('Quit')
        # Text windows
        self.camera_info = QTextEdit()
        self.camera_info.setReadOnly(True)
        self.camera_info.setAcceptRichText(True)
        self.camera_info.setHtml("<div style='font-weight: bold'>Camera settings</div>")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        # We are now going to position our widgets inside our
        # grid layout. The top left corner is (0,0)
        # Here we specify that our vtkWidget is anchored to the top
        # left corner and spans 3 rows and 4 columns.
        self.contour_label = QLabel("Left slider")
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 4, 4)
        self.gridlayout.addWidget(self.contour_label, 4, 0, 1, 1)
        self.gridlayout.addWidget(self.contour_slider, 4, 1, 1, 1)
        self.gridlayout.addWidget(QLabel("Right Slider"), 4, 2, 1, 1)
        self.gridlayout.addWidget(self.y_slider, 4, 3, 1, 1)
        self.gridlayout.addWidget(self.push_screenshot, 0, 5, 1, 1)
        self.gridlayout.addWidget(self.push_camera, 1, 5, 1, 1)
        self.gridlayout.addWidget(self.camera_info, 2, 4, 1, 2)
        self.gridlayout.addWidget(self.log, 3, 4, 1, 2)
        self.gridlayout.addWidget(self.push_quit, 5, 5, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)

class PyQtDemo(QMainWindow):

    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.left = -10
        self.right = 10

        [self.image_actor, self.colorbar, self.volume, self.min_temp, self.max_temp] = make_isocontour(args.input,self.left,self.right)

        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        if args.camera is not None and os.path.exists(args.camera):
            camera = load_camera(args.camera)
            self.ren.SetActiveCamera(camera)
            self.ui.log.insertPlainText('Loaded camera settings from camera.json\n')
                
        self.ren.AddViewProp(self.image_actor)      
        self.ren.AddActor2D(self.colorbar)  
        
        self.ren.GradientBackgroundOn()  # Set gradient for background
        self.ren.SetBackground(0.75, 0.75, 0.75)  # Set background to silver
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.ren.GetRenderWindow().Render()

        # Setting up widgets
        def slider_setup(slider, val, bounds, interv):
            slider.setOrientation(Qt.Orientation.Horizontal)
            slider.setRange(bounds[0], bounds[1])
            slider.setValue(int(val))
            slider.setTracking(False)
            slider.setTickInterval(interv)
            slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        
        slider_setup(self.ui.contour_slider, self.left, [-1100, 1100], 100)
        slider_setup(self.ui.y_slider, self.right, [-1100,1100], 100)
    def contour_callback(self, val):
        self.left = val
        new_otf = vtk.vtkPiecewiseFunction()
        new_otf.AddPoint(self.min_temp, 1.0)
        new_otf.AddPoint(self.left, 0.0)
        new_otf.AddPoint(self.right, 0.0)
        new_otf.AddPoint(self.max_temp, 1.0)
        self.volume.SetScalarOpacity(new_otf)
        self.ui.log.insertPlainText('Left bound value set to {}\n'.format(self.left))
        self.ren.GetRenderWindow().Render()
        

    def y_clip_callback(self, val):
        self.right = val
        new_otf = vtk.vtkPiecewiseFunction()
        new_otf.AddPoint(self.min_temp, 1.0)
        new_otf.AddPoint(self.left, 0.0)
        new_otf.AddPoint(self.right, 0.0)
        new_otf.AddPoint(self.max_temp, 1.0)
        self.volume.SetScalarOpacity(new_otf)
        self.ui.log.insertPlainText('Left bound value set to {}\n'.format(self.right))
        self.ren.GetRenderWindow().Render()
        

    def screenshot_callback(self):
        save_frame(self.ui.vtkWidget.GetRenderWindow(), self.ui.log)

    def camera_callback(self):
        print_camera_settings(self.ren.GetActiveCamera(), self.ui.camera_info, self.ui.log, self.ren)

    def quit_callback(self):
        sys.exit()

if __name__=="__main__":
    global args

    parser = argparse.ArgumentParser(
        description='Illustrate the use of PyQt5 with VTK')
    parser.add_argument('-r', '--resolution', type=int, metavar='int', nargs=2, help='Image resolution', default=[1024, 768])
    parser.add_argument('-o', '--output', type=str, metavar='filename', help='Base name for screenshots', default='frame_')
    parser.add_argument('-v', '--verbose', action='store_true', help='Toggle on verbose output')
    parser.add_argument('-i', '--input', type=str, metavar='filename', help='Input file', required=True)
    parser.add_argument('--camera', type=str, metavar='filename', help='Camera settings file', default=None)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = PyQtDemo()
    window.ui.vtkWidget.GetRenderWindow().SetSize(args.resolution[0], args.resolution[1])
    window.ui.log.insertPlainText('Set render window resolution to {}\n'.format(args.resolution))
    window.show()
    window.setWindowState(Qt.WindowState.WindowMaximized)  # Maximize the window
    window.iren.Initialize() # Need this line to actually show
                             # the render inside Qt

    window.ui.contour_slider.valueChanged.connect(window.contour_callback)
    window.ui.y_slider.valueChanged.connect(window.y_clip_callback)
    window.ui.push_screenshot.clicked.connect(window.screenshot_callback)
    window.ui.push_camera.clicked.connect(window.camera_callback)
    window.ui.push_quit.clicked.connect(window.quit_callback)
    sys.exit(app.exec())
