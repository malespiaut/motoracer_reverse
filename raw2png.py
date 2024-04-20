"""
Description: HSI Raw image convert to PNG
Author: Marc-Alexandre Espiaut <ma.dev@espiaut.fr>
Date Created: 2024-03-22
Last Modified: 2024-04-20
Version: 240420
"""

# This software was originally written to convert Moto Racer images to PNG.
# However, upon further research, it appears that this is a common image format
# know as “HSI Raw”, that is used in other video games, such as “Ecstatica II”,
# “The Prince and the Coward”, and “Zombie Wars” (also known as Halloween Harry 2).

# The “mhwanh” signature stands for Marcos H. Woehrmann, Allan N. Hessenflow.
# See:
# - http://fileformats.archiveteam.org/wiki/HSI_Raw
# - http://tex.imm.uran.ru/alchemy.pdf


import logging
import struct
import sys
from pathlib import Path
from PIL import Image


def main() -> bool:
    """Everything happens here."""
    logging.basicConfig(level=logging.INFO)

    inpath: str = sys.argv[1]
    with open(inpath, "rb") as r:
        # Checking if this is a real “mhwanh” file
        if r.read(6) != b"mhwanh":
            logging.error("Incorrect signature.")
            return False
        logging.info("Signature is correct")

        # Jumping directly to the image dimensions.
        r.seek(0x8)

        # Reading header (3 × shorts, big endian)
        image_width, image_height, palette_colors = struct.unpack(">HHH", r.read(6))
        logging.info(f"Image size: {image_width}×{image_height}")

        # Jumping directly to the image data.
        r.seek(0x20)

        if palette_colors != 0:
            logging.info("This image has a color palette!")

            # Load in palette
            palette: bytes = r.read(768)

            # Write palette to a .pal file
            palpath: Path = Path(inpath).with_suffix(".pal")
            with open(palpath, "wb") as output_palette:
                output_palette.write(palette)
                logging.info(f"Wrote {palpath}")

            # Load indexed-color image
            indexed_data: bytes = r.read(image_width * image_height)
            image = Image.frombytes("P", (image_width, image_height), indexed_data)
            image.putpalette(palette)
        else:
            logging.info("This image is RGB!")

            # Load RGB image
            rgb_data: bytes = r.read()
            image = Image.frombuffer("RGB", (image_width, image_height), rgb_data)

    outpath: Path = Path(inpath).with_suffix(".png")
    image.save(outpath)
    logging.info(f"Wrote {outpath}")
    return True


if __name__ == "__main__":
    SUCCESS = main()
    if not SUCCESS:
        sys.exit(1)
