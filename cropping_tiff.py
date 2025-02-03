import os
import random
import tifffile as tiff
import numpy as np
from pathlib import Path

def crop_3d_image(image, crop_size):
    """
    Randomly crop a 3D image along x and y axes, while accounting for channels if present.
    
    Args:
        image (numpy.ndarray): Input 3D or 4D image (Z, Y, X) or (C, Z, Y, X).
        crop_size (tuple): Tuple specifying the crop dimensions (height, width).

    Returns:
        numpy.ndarray: Cropped 3D image.
    """
    if image.ndim == 4:  # If channels are present
        channels, z_dim, y_dim, x_dim = image.shape
    elif image.ndim == 3:  # No channels
        z_dim, y_dim, x_dim = image.shape
        channels = None
    else:
        raise ValueError("Unsupported image dimensions. Only 3D or 4D arrays are supported.")

    crop_height, crop_width = crop_size

    if y_dim < crop_height or x_dim < crop_width:
        raise ValueError("Crop size exceeds image dimensions.")

    y_start = random.randint(0, y_dim - crop_height)
    x_start = random.randint(0, x_dim - crop_width)

    if channels is not None:
        cropped_image = image[:, :, y_start:y_start + crop_height, x_start:x_start + crop_width]
    else:
        cropped_image = image[:, y_start:y_start + crop_height, x_start:x_start + crop_width]

    return cropped_image

def process_folder(input_folder, output_folder, crop_size):
    """
    Process all 3D/4D TIFF images in the input folder, crop them, and save them to the output folder.

    Args:
        input_folder (str): Path to the input folder containing 3D or 4D TIFF images.
        output_folder (str): Path to the output folder to save cropped images.
        crop_size (tuple): Tuple specifying the crop dimensions (height, width).
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    for file_name in os.listdir(input_path):
        if file_name.endswith('.tif') or file_name.endswith('.tiff'):
            input_file = input_path / file_name
            output_file_name = f"{Path(file_name).stem}_cropped{Path(file_name).suffix}"
            output_file = output_path / output_file_name
            
            # Load the 3D or 4D TIFF image
            image = tiff.imread(input_file)
            
            # Handle cases where image may be grayscale and missing expected dimensions
            if image.ndim not in [3, 4]:
                print(f"Skipping {file_name}: Unsupported image dimensions {image.shape}")
                continue

            # Crop the image
            cropped_image = crop_3d_image(image, crop_size)

            # Save the cropped image
            tiff.imwrite(output_file, cropped_image)

            print(f"Processed and saved: {output_file}")

if __name__ == "__main__":
    # Hardcoded directories and crop size
    input_folder = "path/to/input_folder"
    output_folder = "path/to/output_folder"
    crop_height = 300  # you can change this value
    crop_width = 300  # you can change this value

    crop_size = (crop_height, crop_width)

    process_folder(input_folder, output_folder, crop_size)
