import cv2
import os

# Set up the path to the images
image_folder = './'  # The directory where your images are located

image_files = []
i = 1
while True:
    print(f"output_images/animation.{str(i).zfill(3)}.png")
    file_path = f"output_images/animation.{str(i).zfill(4)}.png"
    if os.path.exists(file_path):
        image_files.append(file_path)
        i += 1
    else:
        break
print(image_files)
# Read the first image to get the dimensions
first_image = cv2.imread(os.path.join(image_folder, image_files[0]))
height, width, layers = first_image.shape

# Set up the video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Video codec (e.g., 'mp4v' for .mp4 files)
video = cv2.VideoWriter('output_video_color.mp4', fourcc, 30.0, (width, height))  # 30 fps

# Loop through all images and write them to the video
for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    img = cv2.imread(image_path)
    video.write(img)

# Release the video writer
video.release()

print("Video created successfully!")
