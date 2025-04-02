import vtk

# Read the VTS file
reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName("spherical_transformed.vts")
reader.Update()

# Check available data arrays
print(reader.GetOutput())
point_data = reader.GetOutput().GetCellData()
for i in range(point_data.GetNumberOfArrays()):
    print("Array", i, ":", point_data.GetArrayName(i))

# Ensure that the 'temperature' array exists
temperature_array = point_data.GetArray("temperature")
if temperature_array:
    print(f"Temperature array found! Range: {temperature_array.GetRange()}")
else:
    print("Temperature array not found! Please check your data.")

# Create a color transfer function
lut = vtk.vtkColorTransferFunction()

# Adjust color mapping based on the actual temperature range
min_temp, max_temp = temperature_array.GetRange()
lut.AddRGBPoint(min_temp, 0.0, 0.0, 1.0)  # Blue for min temperature
lut.AddRGBPoint(max_temp, 1.0, 0.0, 0.0)  # Red for max temperature

# Optionally add more color points in between for better contrast:
lut.AddRGBPoint(min_temp + (max_temp - min_temp) * 0.25, 0.0, 1.0, 0.0)  # Green for mid-range
lut.AddRGBPoint(min_temp + (max_temp - min_temp) * 0.75, 1.0, 1.0, 0.0)  # Yellow for high-mid range

# Create a mapper
mapper = vtk.vtkDataSetMapper()
mapper.SetInputConnection(reader.GetOutputPort())

# Apply the color transfer function to the mapper
mapper.SetLookupTable(lut)
mapper.SelectColorArray("temperature")  # Use the temperature array for coloring

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Add the actor to the scene
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)  # Background color

# Adjust camera to ensure the object is visible
renderer.GetActiveCamera().Azimuth(30)
renderer.GetActiveCamera().Elevation(30)
renderer.ResetCamera()

# Render and interact
renderWindow.Render()
renderWindowInteractor.Start()
