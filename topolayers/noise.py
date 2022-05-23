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

import numpy as np
import scipy.ndimage.interpolation

from typing import Union

TRANSPARENT = (0, 0, 0, 0)  # True
OPAQUE = (0, 0, 0, 232)  # False

logger = logging.getLogger(__name__)


class RandomNoise:
    def __init__(self, seed: int = None, array_size: tuple = (4, 4)):
        """The noise generator for layering. Takes a seed and an initial array size.

        If seed is None, then a random seed is chosen. The array size signifies the
        initial array size. Note that when zooming, a higher array size is equal to
        a more complex final image. Also, the generation process will take longer
        the higher the value put into the array_size argument.

        Args:
            seed: The seed to generate the random noise map.
            array_size: The initial size of the noise array.
        """
        logger.debug(f"Generating noise array with array size: {array_size}.")
        if isinstance(seed, int):
            logger.debug(f"Seed is not None. Using seed: {seed}.")
            np.random.seed(seed)
        self.noise_array = np.random.uniform(size=array_size)

    def process_noise_array(self, threshold: Union[int, float] = None, zoom_aspect: int = 8):
        """Zooms and filters the generated noise array.

        If threshold is set to None, then it will just return the generated noise
        array. Else, it will return`the filtered noise array.

        Args:
            threshold: The threshold to aim for.
            zoom_aspect: The zoom aspect for that array.

        Returns:
            np.ndarray: The processed noise array.
        """
        logger.debug(f"Processing noise array with threshold {threshold} and zoom aspect {zoom_aspect}.")
        generated_array = scipy.ndimage.interpolation.zoom(self.noise_array, zoom_aspect)[:, :, np.newaxis]
        if isinstance(threshold, float) or isinstance(threshold, int):
            return np.where(generated_array > threshold, TRANSPARENT, OPAQUE)
        return generated_array
