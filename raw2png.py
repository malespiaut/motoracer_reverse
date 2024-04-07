"""
Description: HSI Raw image convert to PNG
Author: Marc-Alexandre Espiaut <ma.dev@espiaut.fr>
Date Created: 2024-03-22
Last Modified: 2024-04-07
Version: 240407
"""

# This software was originally written to convert Moto Racer images to PNG.
# However, upon further research, it appears that this is a common image format
# know as “HSI Raw”, that is used in other video games, such as “Ecstatica II”,
# “The Prince and the Coward”, and “Zombie Wars” (also known as Halloween Harry 2).

# The “mhwanh” signature stands for Marcos H. Woehrmann, Allan N. Hessenflow.
# See:
# - http://fileformats.archiveteam.org/wiki/HSI_Raw
# - http://tex.imm.uran.ru/alchemy.pdf


import io
import logging
import os
import sys
import numpy as np
from PIL import Image


def filename_gen(rawfile_path: str, extension: str) -> str:
    """This function makes it easier to generate filenames that matches the input file."""
    # path/file.ext -> file
    filename: str = os.path.splitext(os.path.basename(rawfile_path))[0]

    return filename + "." + extension


def main():
    """Everything happens here."""
    logging.basicConfig(level=logging.INFO)

    file = None
    with open(sys.argv[1], "rb") as f:
        logging.info(f"Storing {sys.argv[1]} in RAM.")
        file = f.read()
        f.close()

    with io.BytesIO(file) as r:
        # Checking is this is a real “mhwanh” file
        if str(r.read(6), "ascii") == "mhwanh":
            logging.info("Signature is correct")

            # Jumping directly to the image dimensions.
            r.seek(0x8)

            # Reading header
            image_width: int = int.from_bytes(r.read(2), byteorder="big")
            image_height: int = int.from_bytes(r.read(2), byteorder="big")
            logging.info(f"Image size: {image_width}x{image_height}")

            palette_colors: int = int.from_bytes(r.read(2), byteorder="big")

            # Jumping directly to the image data.
            r.seek(0x20)

            if palette_colors != 0:
                logging.info("This image have a color palette!")

                # Writing palette to a file, and saving it in memory
                with open(filename_gen(sys.argv[1], "pal"), "wb") as output_palette:
                    palette: bytes = r.read(768)
                    output_palette.write(palette)
                    output_palette.close()

                    # Writing the paletized image
                    output_image: Image.Image = Image.frombytes(
                        "P",
                        (image_width, image_height),
                        r.read(image_width * image_height),
                    )
                    output_image.putpalette(palette)
                    output_image.save(filename_gen(sys.argv[1], "png"))

            else:
                logging.info("This image is RGB!")

                # Writing the RGB image
                Image.fromarray(
                    np.frombuffer(r.read(), dtype=np.uint8).reshape(
                        (image_height, image_width, 3)
                    )
                ).save(filename_gen(sys.argv[1], "png"))

        else:
            logging.error("Incorrect signature.")


if __name__ == "__main__":
    main()
