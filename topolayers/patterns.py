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
import itertools
import numpy as np

from PIL import ImageColor
from .exceptions import InvalidHex

logger = logging.getLogger(__name__)


class Patterns:
    def __init__(self, noise: np.ndarray, gradient_steps: int):
        """A utility function that helps the image generation process.

        Args:
            noise: The noise array to base the layers on.
            gradient_steps: The amount of layers that will be generated between each color.
        """
        self.noise: np.ndarray = noise
        self.gradient_steps: int = gradient_steps

    def _convert_hex(self, colors: list, color_opacity: int = 255):
        """Converts hex into RGBA given a list of colors and a color opacity.

        Args:
            colors: A list of colors to convert to RGBA.
            color_opacity: The alpha element for each color.

        Returns:
            list: A list of RGBA values.

        Raises:
            InvalidHex: If the hex provided is invalid.
        """
        try:
            converted_colors = list()
            for color in colors:
                rgb = list(ImageColor.getrgb(color))
                rgb.append(color_opacity)  # We want to turn it into rgba
                logger.debug(f"Adding color with RGB {rgb}.")
                converted_colors.append(rgb)
            return converted_colors
        except ValueError as exc:
            raise InvalidHex("An invalid hex was provided!") from exc

    def interpolate(self, color1: tuple, color2: tuple, luminosity: float, opacity: int):
        """Interpolates between two colors given a luminosity value.

        Args:
            color1: The start color.
            color2: The end color.
            luminosity: The luminosity between the start and end color.
            opacity: The alpha value of the final RGBA value.

        Returns:
            int: The new R value.
            int: The new G value.
            int: The new B value.
            int: The new A value.
        """
        new_r = (color2[0] - color1[0]) * luminosity + color1[0]
        new_g = (color2[1] - color1[1]) * luminosity + color1[1]
        new_b = (color2[2] - color1[2]) * luminosity + color1[2]
        return new_r, new_g, new_b, opacity

    def _process_rgba(self, rgba: list):
        """Converts the given RGBA value so it doesn't overflow or underflow.

        Along with that, this also converts every value into an integer. This prevents
        floats from appearing in the final RGBA value.

        Args:
            rgba: The given RGBA value.

        Returns:
            list: The final processed RGBA value.
        """
        processed_rgba = [c if c <= 255 else 255 for c in rgba]
        processed_rgba = [c if c >= 0 else 0 for c in processed_rgba]
        return [int(c) for c in processed_rgba]

    def _chunk_noise(self, colors: list):
        """Chunks the given noise arrays based on the amount of colors given.

        Args:
            colors: A list of colors.

        Returns:
            list: An array of the chunked array.
        """
        chunk_length = len(self.noise) // len(colors)
        return [self.noise[x: x + chunk_length] for x in range(0, len(self.noise), chunk_length)]

    def interpolate_colors(self, colors: list, luminosity: float):
        """Interpolates between two different colors.

        This returns an array of colors where each color slowly fades
        into the second color, giving a nice looking effect.

        Args:
            colors: A list of colors to interpolate from and to.
            luminosity: The difference between each color while fading between two colors.

        Returns:
            zip: A zip object with all noise chunks and generated gradients.
        """
        gradient_colors = list()
        colors = self._convert_hex(colors, color_opacity=255)
        for rgb_color1, rgb_color2 in itertools.pairwise(colors):
            for iteration in range(self.gradient_steps):
                brightness = luminosity * (iteration + 1)
                rgba = list(self.interpolate(rgb_color1, rgb_color2, brightness, opacity=255))
                gradient_colors.append(self._process_rgba(rgba))
            logger.info(f"Adding layer with start RGB {rgb_color1} and end RGB {rgb_color2}.")
        chunks = self._chunk_noise(gradient_colors=gradient_colors)
        logger.info(f"Returning gradient with {len(gradient_colors)} colors and {len(chunks)} chunks.")
        return zip(gradient_colors, chunks)
