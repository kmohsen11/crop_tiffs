import os
import random
import tifffile as tiff
import numpy as np
from pathlib import Path

import numpy as np

def crop_3d_image(image, crop_size):
    """
    Crop a 3D or 4D image in one go without looping through each Z-plane, including extracting the center 8 Z slices.
    
    Args:
        image (numpy.ndarray): Input image, shape can be (Z, C, Y, X) for 4D or (Z, Y, X) for 3D.
        crop_size (tuple): Desired crop dimensions as (crop_height, crop_width).
        
    Returns:
        numpy.ndarray: Cropped image.
    """
    # Check image dimensions
    if image.ndim not in [3, 4]:
        raise ValueError("Unsupported image dimensions. Expected 3D or 4D.")
    
    # Unpack crop dimensions
    crop_height, crop_width = crop_size
    
    # Get image dimensions
    if image.ndim == 4:
        z_dim, _, y_dim, x_dim = image.shape
    elif image.ndim == 3:
        z_dim, y_dim, x_dim = image.shape

    # Validate crop size
    if y_dim < crop_height or x_dim < crop_width or z_dim < 10:
        raise ValueError("Crop size exceeds image dimensions or not enough Z slices.")

    # Calculate the start and end indices to crop the center 8 Z slices
    z_start = (z_dim - 10) // 2
    z_end = z_start + 10

    # Randomly choose the starting indices for Y and X dimensions
    y_start = np.random.randint(0, y_dim - crop_height + 1)
    x_start = np.random.randint(0, x_dim - crop_width + 1)
    
    # Crop the image
    if image.ndim == 4:
        cropped_image = image[z_start:z_end, :, y_start:y_start + crop_height, x_start:x_start + crop_width]
    else:
        cropped_image = image[z_start:z_end, y_start:y_start + crop_height, x_start:x_start + crop_width]
    
    return cropped_image



from tifffile import imwrite

def save_tiff_correctly(output_file, image):
    """
    Saves a multi-channel TIFF correctly, ensuring compatibility with ImageJ,
    formatted for non-color channel data like fluorescence markers,
    adding placeholder dimensions for T (time) and S (samples) if necessary.

    Args:
        output_file (str): Path to the output TIFF file.
        image (numpy.ndarray): Cropped image array, expected to have dimensions (Z, C, Y, X).
    """
    # Check if we need to add placeholders for T and S
    if image.ndim == 4:  # Z, C, Y, X
        # Add a singleton dimension for T at the start and S at the end (1, Z, C, Y, X, 1)
        image = np.expand_dims(image, axis=0)  # Add T dimension at the start
        image = np.expand_dims(image, axis=-1)  # Add S dimension at the end

    # Format the description for ImageJ
    imagej_description = (
        'ImageJ=1.52h\nimages={}\nchannels={}\nslices={}\nframes=1\nhyperstack=true\n'
        'mode=composite\nunit=um\nspacing=1.0\nloop=false\n'.format(
            image.shape[1] * image.shape[2],  # Total number of images (Z * C)
            image.shape[2],  # Number of channels
            image.shape[1]   # Number of slices
        )
    )

    # Save the entire image using tifffile
    imwrite(
        output_file,
        image,
        photometric='minisblack',
        metadata={'axes': 'TZCYXS'},
        imagej=imagej_description
    )
    print(f"Saved: {output_file} with shape {image.shape}")


from pathlib import Path
import os
import tifffile as tiff

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
            output_file_name = f"{input_file.stem}_cropped{input_file.suffix}"
            output_file = output_path / output_file_name
            
            try:
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
            except Exception as e:
                print(f"Error processing {file_name}: {e}")


if __name__ == "__main__":
    # Define paths
    input_folder = "D:/annotations_for_MBL/dapi/rna_scope/round2"
    output_folder = "D:/annotations_for_MBL/dapi/rna_scope/round2/cropped_outdir"
    crop_height, crop_width = 350, 350  # Ensuring at least 300x300 but within image limits

    process_folder(input_folder, output_folder, (crop_height, crop_width))
