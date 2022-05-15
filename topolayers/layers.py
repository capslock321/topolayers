"""
MIT License

Copyright (c) 2022 capslock321

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import dataclasses

import numpy as np
from PIL import Image
from typing import Optional

from .noise import RandomNoise
from .exceptions import InvalidRGB, LayerRequired, InvalidThreshold

TRANSPARENT = (0, 0, 0, 0)
OPAQUE = (0, 0, 0, 232)

logger = logging.getLogger(__name__)


class TopographyMap:
    def __init__(
        self,
        seed: int = None,
        array_size: tuple = (4, 4),
        background_color: tuple = TRANSPARENT,
        zoom_aspect: int = 512,
    ):
        """Generates a topography like style map based on a random seeded noise map.

        Note that the seed, array_size and zoom_aspect arguments are passed
        as arguments into the RandomNoise class.

        Args:
            seed: The seed in which to generate the final image.
            array_size: The initial array size of the noise map.
            background_color: The color of any pixel that does not meet the threshold.
            zoom_aspect: The zoom aspect of the processed noise map.
        """
        self.seed: Optional[int] = seed  # str to int as seed
        self.array_size: np.ndarray = array_size
        self.zoom_aspect: int = zoom_aspect
        self.layers: list = []
        if self._is_valid_rgba(background_color):
            # Why does this parameter even exist?
            self.background_color: tuple = background_color
        else:
            raise InvalidRGB("An invalid RGB tuple was provided!")

    def _is_valid_rgba(self, rgb: tuple) -> bool:  # Right now does not check RGB overflow or underflow.
        """Checks if the provided rgba tuple is valid.

        Args:
            rgb: RGBA tuple. Color value must be provided in RGBA format

        Returns:
            bool: True if value is a valid RGBA tuple.
        """
        if len(rgb) != 4:
            raise InvalidRGB("A RGB tuple must only contain 4 items!")
        return all([isinstance(k, int) for k in rgb])

    def get_noise(self, zoom_aspect: int = 512) -> np.ndarray:
        """Generates noise and returns it zoomed.

        Args:
            zoom_aspect: The zoom aspect of the processed noise map.

        Returns:
            np.ndarray: The processed noise map.
        """
        noise = RandomNoise(self.seed, self.array_size)
        return noise.process_noise_array(zoom_aspect=zoom_aspect)

    def _preprocess_image(self, zoom_aspect: int = 512, threshold: float = 0.5):
        """Processes the noise map and prepare it for pasting.

        Args:
            zoom_aspect: The zoom aspect of the processed noise map.
            threshold: The threshold to aim for.

        Returns:
            np.ndarray: The final processed noise array.

        Raises:
            InvalidThreshold: If the threshold given is too high or low.
        """
        noise = RandomNoise(self.seed, self.array_size)
        if 1 <= threshold < 0:
            # Perhaps I should just remove this.
            raise InvalidThreshold("Threshold must be a number between 0.0 and 1.0.")
        return noise.process_noise_array(threshold, zoom_aspect)

    def add_layer(self, color: tuple, threshold: float = 0.5) -> None:
        """Adds a layer to the final image. You need at least 1 layer to generate
        an image.

        Args:
            color: The color to replace all values that meet the threshold.
            threshold: The threshold to aim for.
        """
        logger.info(f"Adding layer with color {color} and threshold {threshold}.")
        noise_map = self._preprocess_image(self.zoom_aspect, threshold)
        noise_map[np.all(noise_map == OPAQUE, axis=-1)] = color
        layer = TopographyLayer(noise_map, threshold)
        return self.layers.append(layer)

    def generate_image(self, output_path: str = None) -> Image:
        """Generates the final image and returns it in a PIL.Image object.

        This works by creating a new RGBA image and layering all layers onto it.

        Args:
            output_path: If provided, then it will save the generated image to that path.

        Returns:
            PIL.Image: The generated image.
        """
        if not self.layers:
            raise LayerRequired("A single layer is required to generate the image!")
        height, width, _ = self.layers[0].noise_map.shape
        logger.info(f"Generating image with dimensions ({height}, {width})")
        master = Image.new("RGBA", (height, width), self.background_color)
        for layer in self.layers:
            image = Image.fromarray(np.uint8(layer.noise_map), mode="RGBA")
            master.paste(image, (0, 0), image)
        if output_path is not None:
            logger.debug(f"Output path is not None, saving to {output_path}.")
            master.save(output_path, optimize=True)
        return master


@dataclasses.dataclass
class TopographyLayer:
    def __init__(self, noise_map: np.ndarray, threshold: float):
        """A filtered topography layer.

        Args:
            noise_map: The filtered noise map.
            threshold: The threshold used to get that noise map.
        """
        self.noise_map: np.ndarray = noise_map
        self.threshold: float = threshold
