import os
import random
import tifffile as tiff
import numpy as np
from pathlib import Path

def crop_3d_image(image, crop_size):
    """
    Randomly crop a 3D or 4D image while maintaining Z-stack and channels.
    
    Args:
        image (numpy.ndarray): Input image, shape can be (C, Z, Y, X) or (Z, Y, X).
        crop_size (tuple): (crop_height, crop_width)

    Returns:
        numpy.ndarray: Cropped image with the same structure as input.
    """
    if image.ndim == 4:  # If channels are present
        channels, z_dim, y_dim, x_dim = image.shape
    elif image.ndim == 3:  # No channels
        z_dim, y_dim, x_dim = image.shape
        channels = None
    else:
        raise ValueError("Unsupported image dimensions. Expected 3D or 4D.")

    crop_height, crop_width = max(300, crop_size[0]), max(300, crop_size[1])

    if y_dim < crop_height or x_dim < crop_width:
        raise ValueError("Crop size exceeds image dimensions.")

    y_start = random.randint(0, y_dim - crop_height)
    x_start = random.randint(0, x_dim - crop_width)

    if channels is not None:
        cropped_image = image[:, :, y_start:y_start + crop_height, x_start:x_start + crop_width]
    else:
        cropped_image = image[:, y_start:y_start + crop_height, x_start:x_start + crop_width]

    return cropped_image

def save_tiff_correctly(output_file, image):
    """
    Saves a multi-channel TIFF correctly, ensuring Z-stack and channels are preserved.
    
    Args:
        output_file (str): Path to the output TIFF file.
        image (numpy.ndarray): Cropped image array.
    """
    if image.ndim == 4:  # Multi-channel case (C, Z, Y, X)
        tiff.imwrite(
            output_file,
            image,
            photometric='rgb',
            planarconfig='contig',  # Keeps channels grouped correctly
            metadata={'axes': 'CZYX'}
        )
    elif image.ndim == 3:  # No explicit channel dimension
        tiff.imwrite(
            output_file,
            image,
            photometric='minisblack',
            metadata={'axes': 'ZYX'}
        )
    print(f"Saved: {output_file} with shape {image.shape}")

def process_folder(input_folder, output_folder, crop_size):
    """
    Process all 3D/4D TIFF images in the input folder, crop them, and save them correctly.

    Args:
        input_folder (str): Path to input folder containing TIFF images.
        output_folder (str): Path to output folder to save cropped images.
        crop_size (tuple): (height, width).
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
            
            # Load the TIFF image
            image = tiff.imread(input_file)
            
            # Skip unsupported image dimensions
            if image.ndim not in [3, 4]:
                print(f"Skipping {file_name}: Unsupported dimensions {image.shape}")
                continue

            # Ensure the crop size does not exceed the image dimensions
            crop_height = min(max(300, crop_size[0]), image.shape[-2])
            crop_width = min(max(300, crop_size[1]), image.shape[-1])

            # Crop the image
            cropped_image = crop_3d_image(image, (crop_height, crop_width))

            # Save while ensuring proper Z-stack and channel recombination
            save_tiff_correctly(output_file, cropped_image)

            print(f"Processed and saved: {output_file}")

if __name__ == "__main__":
    # Define paths
    input_folder ="path/to/your/input/folder"
    output_folder = "path/to/your/output/folder"
    crop_height, crop_width = 600, 600  # Ensuring at least 300x300 but within image limits

    process_folder(input_folder, output_folder, (crop_height, crop_width))
