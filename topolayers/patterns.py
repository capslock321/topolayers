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
    """Will output layers and thresholds."""

    def __init__(self, noise: np.ndarray, gradient_steps: int):
        self.noise: np.ndarray = noise
        self.gradient_steps: int = gradient_steps

    def _convert_hex(self, colors: list, color_opacity: int = 255):
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

    def interpolerate(self, color1: tuple, color2: tuple, luminosity: float, opacity: int):
        new_r = (color2[0] - color1[0]) * luminosity + color1[0]
        new_g = (color2[1] - color1[1]) * luminosity + color1[1]
        new_b = (color2[2] - color1[2]) * luminosity + color1[2]
        return new_r, new_g, new_b, opacity

    def _process_rgba(self, rgb: list):
        processed_rgba = [c if c <= 255 else 255 for c in rgb]
        processed_rgba = [c if c >= 0 else 0 for c in processed_rgba]
        return [int(c) for c in processed_rgba]

    def interpolerate_colors(self, colors: list, luminosity: float):
        gradient_colors = list()
        colors = self._convert_hex(colors, color_opacity=255)
        for rgb_color1, rgb_color2 in itertools.pairwise(colors):
            for iteration in range(self.gradient_steps):
                brightness = luminosity * (iteration + 1)
                rgba = list(self.interpolerate(rgb_color1, rgb_color2, brightness, opacity=255))
                gradient_colors.append(self._process_rgba(rgba))
            logger.info(f"Adding layer with start RGB {rgb_color1} and end RGB {rgb_color2}.")
        chunk_length = len(self.noise) // len(gradient_colors)
        chunks = [self.noise[x : x + chunk_length] for x in range(0, len(self.noise), chunk_length)]
        logger.info(f"Returning gradient with {len(gradient_colors)} colors and {len(chunks)} chunks.")
        return zip(gradient_colors, chunks)
