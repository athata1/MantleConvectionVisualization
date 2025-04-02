from paraview import *

# Step 1: Load the NetCDF file
netcdf_reader = NetCDFReader(FileName=["mantle_data/spherical001.nc"])
netcdf_reader.UpdatePipeline()

# Step 2: Convert cell data to point data
point_data = CellDatatoPointData(netcdf_reader)
point_data.UpdatePipeline()

# Step 3: Remove unwanted arrays (thermal conductivity and thermal expansivity)
cleaned_data = PassArrays(Input=point_data)
cleaned_data.PointDataArrays = [
    "spin transition-induced density anomaly",
    "temperature",
    "temperature anomaly",
    "vx", "vy", "vz"  # Keep velocity components for now
]
cleaned_data.UpdatePipeline()

# Step 4: Create a vector field from vx, vy, vz
calculator = Calculator(Input=cleaned_data)
calculator.ResultArrayName = "Velocity"
calculator.Function = "vx*iHat + vy*jHat + vz*kHat"
calculator.UpdatePipeline()

# Step 5: Remove vx, vy, vz after combining
final_data = PassArrays(Input=calculator)
final_data.PointDataArrays = [
    "spin transition-induced density anomaly",
    "temperature",
    "temperature anomaly",
    "Velocity"  # Only keep the combined velocity vector
]
final_data.UpdatePipeline()

# Step 6: Save as a VTS file
SaveData("mantle_transformaed_data/output.vts", proxy=final_data)

print("Saved processed data as output.vts")
