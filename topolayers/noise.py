import logging

import numpy as np
import scipy.ndimage.interpolation

TRANSPARENT = (0, 0, 0, 0)  # True
OPAQUE = (0, 0, 0, 232)  # False

logger = logging.getLogger(__name__)


class RandomNoise:
    def __init__(self, seed: int = None, array_size: np.ndarray = (4, 4)):
        """The noise generator for layering. Takes a seed and an initial array size.

        If seed is None, then a random seed is chosen. The array size signifies the
        initial array size. Note that when zooming, a higher array size is equal to
        a more complex final image. Also, the generation process will take longer
        the higher the value put into the array_size argument.

        Args:
            seed: The seed to generate the random noise map.
            array_size: The initial size of the noise array.
        """
        logger.info(f"Generating noise array with array size: {array_size}.")
        if isinstance(seed, int):
            logger.info(f"Using seed: {seed}.")
            np.random.seed(seed)
        self.noise_array = np.random.uniform(size=array_size)

    def process_noise_array(self, threshold: float = None, zoom_aspect: int = 8):
        """Zooms and filters the generated noise array.

        If threshold is set to None, then it will just return the generated noise
        array. Else, it will return`the filtered noise array.

        Args:
            threshold: The threshold to aim for.
            zoom_aspect: The zoom aspect for that array.

        Returns:
            np.ndarray: The processed noise array.
        """
        logger.info(f"Processing noise array with threshold {threshold} and zoom aspect {zoom_aspect}.")
        array = scipy.ndimage.interpolation.zoom(self.noise_array, zoom_aspect)
        array = array[:, :, np.newaxis]
        if threshold is not None:
            return np.where(array > threshold, TRANSPARENT, OPAQUE)
        return array
