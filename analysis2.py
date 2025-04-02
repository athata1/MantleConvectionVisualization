import vtk
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import pyplot as plt

# File path to your NetCDF file
file_number = int(sys.argv[1])
file_path = f"mantle_data/spherical{file_number:03d}.nc"
print("Opening file:", file_path)

# Step 1: Create a reader for NetCDF CF files
reader = vtk.vtkNetCDFCFReader()
reader.SetFileName(file_path)
reader.UpdateMetaData()

# Step 2: Select the "temperature anomaly" variable to read
selected_variable = "temperature"
reader.SetVariableArrayStatus(selected_variable, 1)
reader.Update()  # Update the reader to load the data

# Step 3: Check the dataset structure and ensure the variable is accessible
data = reader.GetOutput()
print(data)

for i in range(data.GetCellData().GetNumberOfArrays()):
    print(f"Array {i}: {data.GetCellData().GetArrayName(i)}")
    
# Step 4: Retrieve the temperature array from Cell Data
temperature_array = data.GetCellData().GetArray(selected_variable)
np_temp_array = np.array([temperature_array.GetValue(i) for i in range(temperature_array.GetNumberOfTuples())])

# Initial clipping range
clip_min, clip_max = 500, 600

def update_hist():
    """Updates the histogram based on the current clipping range."""
    global clip_min, clip_max
    
    filtered_data = np_temp_array[(np_temp_array > clip_min) & (np_temp_array < clip_max)]
    
    ax.clear()
    ax.hist(filtered_data, bins=1000, edgecolor='black')
    ax.set_title(f'{selected_variable} Histogram')
    ax.set_xlabel(f'{selected_variable}')
    ax.set_ylabel('Frequency')
    ax.grid(True)
    plt.draw()

def on_key(event):
    """Handles key press events for shifting the clipping range."""
    global clip_min, clip_max
    if event.key == 'right':
        clip_min += 50
        clip_max += 50
        update_hist()
    elif event.key == 'left':
        clip_min -= 50
        clip_max -= 50
        update_hist()

# Step 5: Create the figure and histogram
fig, ax = plt.subplots()
update_hist()
fig.canvas.mpl_connect('key_press_event', on_key)

# Step 6: Save the histogram as an image file
output_image_path = f"mantle_data/temperature_anomaly_histogram_{file_number:03d}.png"
plt.savefig(output_image_path)
print(f"Histogram saved as {output_image_path}")

# Show the histogram with interactivity
plt.show()