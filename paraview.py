from paraview.simple import *

# Set input file and output file
input_netcdf_file = "your_file.nc"  # Change to your NetCDF file path
output_vti_file = "output.vti"      # Change to desired output file path

# Load the NetCDF file
netcdf_reader = NetCDFReader(FileName=input_netcdf_file)
netcdf_reader.UpdatePipeline()

# Get the dataset information
data_info = netcdf_reader.GetDataInformation()
extent = data_info.GetExtent()  # (xmin, xmax, ymin, ymax, zmin, zmax)

# Compute sampling dimensions from the extent
sampling_dimensions = [
    extent[1] - extent[0] + 1,  # X dimension size
    extent[3] - extent[2] + 1,  # Y dimension size
    extent[5] - extent[4] + 1,  # Z dimension size
]

print(f"Automatically determined sampling dimensions: {sampling_dimensions}")

# Apply the "Resample to Image" filter with auto-detected dimensions
resampled = ResampleToImage(Input=netcdf_reader)
resampled.SamplingDimensions = sampling_dimensions
resampled.UpdatePipeline()

# Save the resampled data as .vti (VTK Image Data)
SaveData(output_vti_file, proxy=resampled)

# Optionally, save a screenshot of the visualization
renderView = GetActiveViewOrCreate("RenderView")
Show(resampled, renderView)
Render()
SaveScreenshot("output_image.png", renderView, ImageResolution=[1024, 1024])

print(f"Exported VTI file: {output_vti_file}")
print("Screenshot saved as output_image.png")
