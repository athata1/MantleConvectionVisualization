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

# Step 2: Select the "temperature anomaly" variable to read
selected_variable = "temperature anomaly"
reader.SetVariableArrayStatus(selected_variable, 1)
reader.Update()  # Update the reader to load the data

# Step 3: Check the dataset structure and ensure the variable is accessible
data = reader.GetOutput()
print(type(data))
print(data)
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
        min_temp, max_temp = -200, 200  # Shrink the range for visualization
        print(f"Using temperature range: {min_temp} - {max_temp}")
        
        # Step 5: Scale the data to match the temperature range for visualization
        scalar_range = temperature_array.GetRange()  # Get original range of the data
        scale_factor = (max_temp - min_temp) / (scalar_range[1] - scalar_range[0])  # Scaling factor
        shift_factor = min_temp - scalar_range[0] * scale_factor  # Shift factor to match min_temp

        # Apply the scaling to the data
        #Create dee copy of temperature array
        
        scaled_array = vtk.vtkDoubleArray()
        scaled_array.SetNumberOfTuples(temperature_array.GetNumberOfTuples())
        for i in range(temperature_array.GetNumberOfTuples()):
            original_value = temperature_array.GetValue(i)
            scaled_value = original_value * scale_factor + shift_factor
            scaled_array.SetValue(i, scaled_value)

        # Set the scaled array back to the data
        data.GetCellData().SetScalars(scaled_array)
        print(type(data))
        
        threshold_value = 50

        # Lower threshold filter
        lower_threshold = vtk.vtkThreshold()
        lower_threshold.SetInputData(data)
        lower_threshold.SetLowerThreshold(threshold_value)  # Adjust this as needed
        lower_threshold.Update()


        # Upper threshold filter
        upper_threshold = vtk.vtkThreshold()
        upper_threshold.SetInputData(data)
        upper_threshold.SetUpperThreshold(-threshold_value)  # Adjust this as needed
        upper_threshold.Update()
        
        # Combine both thresholded outputs
        combine_threshold = vtk.vtkAppendFilter()
        combine_threshold.AddInputData(lower_threshold.GetOutput())
        combine_threshold.AddInputData(upper_threshold.GetOutput())
        combine_threshold.Update()
        print(type(combine_threshold.GetOutput()))
        # In-between threshold filter (for values between 50 and 150)
        in_between_threshold = vtk.vtkThreshold()
        in_between_threshold.SetInputData(data)
        in_between_threshold.SetLowerThreshold(-threshold_value)  # Lower bound of in-between range
        in_between_threshold.SetUpperThreshold(threshold_value)  # Upper bound of in-between range
        in_between_threshold.Update()

        # Get the combined filtered data
        data = combine_threshold.GetOutput()
        
        # Convert unstructured grid to polydata using vtkGeometryFilter
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(data)
        geometry_filter.Update()

        # Get the output polydata
        polydata = geometry_filter.GetOutput()
        
        # Apply vtkSmoothPolyDataFilter to smooth the polydata
        smooth_filter = vtk.vtkSmoothPolyDataFilter()
        smooth_filter.SetInputData(polydata)
        smooth_filter.SetNumberOfIterations(40)  # Number of smoothing iterations
        smooth_filter.SetRelaxationFactor(0.1)   # Relaxation factor (default: 0.01)
        smooth_filter.FeatureEdgeSmoothingOff()  # Disable feature edge smoothing
        smooth_filter.BoundarySmoothingOn()      # Enable boundary smoothing
        smooth_filter.Update()

        # Get the smoothed polydata output
        data = smooth_filter.GetOutput()



        in_between_data = in_between_threshold.GetOutput()
        
        # Step 7: Set up a color transfer function for visualization
        color_transfer_function = vtk.vtkColorTransferFunction()
        color_transfer_function.AddRGBPoint(max_temp, 1.0, 0.0, 0.0)  # Red for max
        color_transfer_function.AddRGBPoint(0.0, 1.0, 1.0, 1.0)       # White for neutral
        color_transfer_function.AddRGBPoint(min_temp, 0.0, 0.0, 1.0)  # Blue for min

        # Step 11: Set up the mapper and actor for the clipped data
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(data)
        mapper.SetScalarModeToUseCellFieldData()
        mapper.SelectColorArray(selected_variable)
        mapper.SetScalarRange(min_temp, max_temp)
        mapper.SetLookupTable(color_transfer_function)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        # Set up a mapper and actor for the in-between data (with opacity of 0.1)
        in_between_mapper = vtk.vtkDataSetMapper()
        in_between_mapper.SetInputData(in_between_data)
        in_between_mapper.SetScalarModeToUseCellFieldData()
        in_between_mapper.SelectColorArray(selected_variable)
        in_between_mapper.SetScalarRange(min_temp, max_temp)
        in_between_mapper.SetLookupTable(color_transfer_function)

        in_between_actor = vtk.vtkActor()
        in_between_actor.SetMapper(in_between_mapper)
        in_between_actor.GetProperty().SetOpacity(0.1)  # Set opacity for in-between data

        # Step 12: Apply a transformation to rotate the dataset
        transform = vtk.vtkTransform()
        transform.RotateX(25)
        transform.RotateY(-45)
        actor.SetUserTransform(transform)

        # Step 13: Set up the renderer, window, and interactor
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        # Add the actor and scalar bar (color legend) to the renderer
        renderer.AddActor(actor)
        renderer.AddActor(in_between_actor)  # Actor for in-between data with opacity


        scalar_bar = vtk.vtkScalarBarActor()
        scalar_bar.SetLookupTable(color_transfer_function)
        scalar_bar.SetTitle("Temperature Anomaly (K)")
        scalar_bar.SetNumberOfLabels(5)
        renderer.AddActor2D(scalar_bar)

        renderer.SetBackground(0.1, 0.2, 0.4)  # Background color
        render_window.SetSize(1600, 1200)
        
        renderer.ResetCamera()
        renderer.GetActiveCamera().Zoom(2.5)

        # Step 14: Start the visualization
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
        
        # Uncomment the next line to start interaction
        interactor.Start()
