import vtk

# Step 1: Read VTS file
reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName('test_save.vts')
reader.Update()

# Get bounds for clipping
bounds = reader.GetOutput().GetBounds()
x_min, x_max, y_min, y_max, z_min, z_max = bounds

# Step 2: Ensure Temperature Data Exists
structured_grid = reader.GetOutput()
structured_grid.GetPointData().SetActiveScalars("temperature")  # Set active scalar

# Step 3: Create Clipping Box
box = vtk.vtkBox()
box.SetBounds(0, x_max, 0, y_max, 0, z_max)

clip_filter = vtk.vtkClipDataSet()
clip_filter.SetInputData(structured_grid)
clip_filter.SetClipFunction(box)
clip_filter.Update()

geometry_filter = vtk.vtkGeometryFilter()
geometry_filter.SetInputConnection(clip_filter.GetOutputPort())
geometry_filter.Update()

# Step 4: Create Lookup Table for Temperature
min_temp, max_temp = structured_grid.GetPointData().GetScalars("temperature").GetRange()

lut = vtk.vtkColorTransferFunction()
lut.AddRGBPoint(min_temp, 0.0, 0.0, 1.0)
lut.AddRGBPoint(500, 148/255,0,211/255)
lut.AddRGBPoint(2000, 0.0, 1.0, 0.0)
lut.AddRGBPoint(2200, 255/255,192/255,203/255)
lut.AddRGBPoint(2300, 1.0, 1.0, 0.0)
lut.AddRGBPoint(3400,48/255, 25/255, 52/255)
lut.AddRGBPoint(max_temp, 1.0, 0.0, 0.0)

# Step 5: Create LIC Mapper
mapper = vtk.vtkSurfaceLICMapper()
mapper.SetInputConnection(geometry_filter.GetOutputPort())
mapper.SetLookupTable(lut)
mapper.SetScalarModeToUsePointFieldData()  # Use temperature for coloring
mapper.SelectColorArray("temperature")  # Ensure the correct scalar field is used
mapper.SetScalarVisibility(True)
mapper.GetLICInterface().SetEnhanceContrast(vtk.vtkSurfaceLICInterface.ENHANCE_CONTRAST_COLOR)
mapper.GetLICInterface().SetColorMode(vtk.vtkSurfaceLICInterface.COLOR_MODE_MAP)

# Step 6: Create Actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.5, 0.5, 0.5)  # Grey background

# Render Window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Start rendering
render_window.Render()
interactor.Start()
