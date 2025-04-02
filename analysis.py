import vtk
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, norm

# File path to your NetCDF file
file_number = int(sys.argv[1])
file_path = f"mantle_data/spherical{file_number:03d}.nc"
print("Opening file:", file_path)

# Step 1: Create a reader for NetCDF CF files
reader = vtk.vtkNetCDFCFReader()
reader.SetFileName(file_path)
reader.UpdateMetaData()

# Step 2: Select the "temperature" variable to read
selected_variable = "temperature"
reader.SetVariableArrayStatus(selected_variable, 1)
reader.Update()  # Update the reader to load the data

# Step 3: Check the dataset structure
data = reader.GetOutput()
print(data)

for i in range(data.GetCellData().GetNumberOfArrays()):
    print(f"Array {i}: {data.GetCellData().GetArrayName(i)}")

# Step 4: Retrieve the temperature array from Cell Data
temperature_array = data.GetCellData().GetArray(selected_variable)
np_temp_array = np.array([temperature_array.GetValue(i) for i in range(temperature_array.GetNumberOfTuples())])

# Initial clipping range
clip_min, clip_max = -10, 10

def compute_kde_derivative():
    """Computes KDE and its derivative, and finds zero-crossings."""
    kde = gaussian_kde(np_temp_array, bw_method=0.1)  # Kernel Density Estimation
    x_vals = np.linspace(np_temp_array.min(), np_temp_array.max(), 500)
    kde_vals = kde(x_vals)

    # Compute the derivative using finite differences
    kde_derivative = np.gradient(kde_vals, x_vals)

    # Find zero-crossings (where the derivative changes sign)
    zero_crossings = []
    for i in range(1, len(kde_derivative)):
        if kde_derivative[i-1] * kde_derivative[i] < 0:  # Sign change
            zero_crossings.append(x_vals[i])

    print("\nPoints where the histogram gradient is zero (peaks or valleys):")
    for z in zero_crossings:
        print(f"Temperature: {z:.4f}")

    return x_vals, kde_vals, kde_derivative, zero_crossings

def plot_fitted_function():
    """Fits and plots a smooth function over the histogram."""
    x_vals, kde_vals, kde_derivative, zero_crossings = compute_kde_derivative()

    # Fit a Gaussian (Normal Distribution)
    mean, std_dev = np_temp_array.mean(), np_temp_array.std()
    gaussian_vals = norm.pdf(x_vals, mean, std_dev) * len(np_temp_array) * (x_vals[1] - x_vals[0])

    # Plot the KDE
    ax1.plot(x_vals, kde_vals * len(np_temp_array) * (x_vals[1] - x_vals[0]), color='red', label="KDE Estimate")

    # Plot Gaussian Fit
    ax1.plot(x_vals, gaussian_vals, color='blue', linestyle='dashed', label="Gaussian Fit")

    ax1.legend()

    # Plot KDE derivative
    ax2.plot(x_vals, kde_derivative, color='green', label="KDE Derivative")
    ax2.axhline(0, color='black', linestyle='dotted')  # Zero reference line

    # Mark zero-crossings on the plot
    for z in zero_crossings:
        ax2.axvline(z, color='purple', linestyle='dashed', alpha=0.6)

    ax2.set_title(f"Derivative of KDE")
    ax2.set_xlabel(f"{selected_variable}")
    ax2.set_ylabel("Derivative")
    ax2.legend()
    ax2.grid(True)

def update_hist():
    """Updates the histogram and overlays the fitted function."""
    global clip_min, clip_max

    ax1.clear()
    ax1.hist(np_temp_array, bins=100, density=True, alpha=0.6, edgecolor='black', label="Histogram")
    ax1.set_title(f'{selected_variable} Histogram with Fitted Curve')
    ax1.set_xlabel(f'{selected_variable}')
    ax1.set_ylabel('Density')
    ax1.grid(True)

    plot_fitted_function()
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

# Step 5: Create the figure with subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), sharex=True)

update_hist()
fig.canvas.mpl_connect('key_press_event', on_key)

# Step 6: Save the histogram as an image file
output_image_path = f"mantle_data/temperature_anomaly_histogram_{file_number:03d}.png"
plt.savefig(output_image_path)
print(f"Histogram saved as {output_image_path}")

# Show the histogram with interactivity
plt.show()
