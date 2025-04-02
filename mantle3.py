import vtk
import sys

# File path to your NetCDF file
file_number = int(sys.argv[1])
file_path = f"mantle_data/spherical{file_number:03d}.nc"
print("Opening file:", file_path)

# Step 1: Create a reader for NetCDF CF files
reader = vtk.vtkNetCDFCFReader()
reader.SetFileName(file_path)
reader.UpdateMetaData()

# Step 2: Select the "temperature" variable to read
#selected_variable = "temperature"
selected_variable = "temperature"
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
        min_temp, max_temp = temperature_array.GetRange()
        #min_temp, max_temp = 293.0, 3610.0
        print(f"Temperature range: {min_temp} - {max_temp}")
        
        # Step 5: Set up a color transfer function for visualization
        color_transfer_function = vtk.vtkColorTransferFunction()
        diff = max_temp - min_temp
        # Defining the color points from highest to lowest temperature
        if selected_variable == "temperature":
            color_transfer_function.AddRGBPoint(max_temp - diff * 0 / 5, 1.0, 0.0, 0.0)  # Red for highest temperature
            color_transfer_function.AddRGBPoint(max_temp - diff * 1 / 5, 1.0, 0.5, 0.0)  # Orange for high
            color_transfer_function.AddRGBPoint(max_temp - diff * 2 / 5, 1.0, 1.0, 0.0)  # Yellow for medium
            color_transfer_function.AddRGBPoint(max_temp - diff * 3 / 5, 0.0, 1.0, 0.0)  # Green for lower medium
            color_transfer_function.AddRGBPoint(max_temp - diff * 4 / 5, 0.0, 0.5, 1.0)  # Light Blue for lower
            color_transfer_function.AddRGBPoint(max_temp - diff, 0.0, 0.0, 1.0)  # Dark Blue for lowest temperature
        if selected_variable == "temperature anomaly":
            color_transfer_function.AddRGBPoint(max_temp - diff * 0 / 2, 1.0, 0.0, 0.0)
            color_transfer_function.AddRGBPoint(max_temp - diff * 1 / 2, 1.0, 1.0, 1.0)
            color_transfer_function.AddRGBPoint(max_temp - diff * 2 / 2, 0.0, 0.0, 1.0)
            
        # Step 6: Get bounds of the data
        bounds = data.GetBounds()
        x_min, x_max, y_min, y_max, z_min, z_max = bounds

        # Step 7: Create the clipping box (from 0,0,0 to the upper bounds)
        box = vtk.vtkBox()
        box.SetBounds(0, x_max, 0, y_max, 0, z_max)  # Box from (0,0,0) to (x_max, y_max, z_max)

        # Step 8: Create the clipping filter
        clip_filter = vtk.vtkClipDataSet()
        clip_filter.SetInputData(data)
        clip_filter.SetClipFunction(box)
        clip_filter.Update()

        # Get the clipped output data
        clipped_data = clip_filter.GetOutput()

        # Step 9: Set up the mapper and actor for the clipped data
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(clipped_data)
        mapper.SetScalarModeToUseCellFieldData()
        mapper.SelectColorArray(selected_variable)
        mapper.SetScalarRange(min_temp, max_temp)
        mapper.SetLookupTable(color_transfer_function)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Step 10: Apply a transformation to rotate the dataset 180 degrees along the X-axis
        transform = vtk.vtkTransform()
        transform.RotateX(25)
        transform.RotateY(-45)
        actor.SetUserTransform(transform)

        # Step 11: Set up the renderer, window, and interactor
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        # Add the actor and scalar bar (color legend) to the renderer
        renderer.AddActor(actor)

        scalar_bar = vtk.vtkScalarBarActor()
        scalar_bar.SetLookupTable(color_transfer_function)
        scalar_bar.SetTitle("Temperature (K)")
        scalar_bar.SetNumberOfLabels(5)
        renderer.AddActor2D(scalar_bar)

        renderer.SetBackground(0.1, 0.2, 0.4)  # Background color
        render_window.SetSize(800, 600)
        
        renderer.ResetCamera()
        renderer.GetActiveCamera().Zoom(2.5)

        # Step 12: Start the visualization
        interactor.Initialize()
        render_window.Render()
        
        # Save the screen to a file
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(render_window)
        window_to_image_filter.SetInputBufferTypeToRGB()
        window_to_image_filter.ReadFrontBufferOff()
        window_to_image_filter.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(f"output_images/mantle_output{file_number:03d}.png")
        writer.SetInputConnection(window_to_image_filter.GetOutputPort())
        writer.Write()

        print(f"Saved current screen to 'mantle_output{file_number:03d}.png'")
        
        
        #interactor.Start()
