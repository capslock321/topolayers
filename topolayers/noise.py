import sys
import logging

import numpy as np
import scipy.ndimage.interpolation

np.set_printoptions(threshold=sys.maxsize)

TRANSPARENT = (0, 0, 0, 0)  # True
OPAQUE = (0, 0, 0, 232)  # False

logger = logging.getLogger(__name__)


class RandomNoise:
    def __init__(self, seed: int = None, array_size: np.ndarray = (4, 4)):
        logger.info(f"Generating noise array with array size: {array_size}.")
        if isinstance(seed, int):
            logger.info(f"Using seed: {seed}.")
            np.random.seed(seed)
        self.noise_array = np.random.uniform(size=array_size)

    def generate_noise_array(self, threshold: float = None, zoom_aspect: int = 8):
        logger.info(
            f"Processing noise array with threshold {threshold} and zoom aspect of {zoom_aspect}."
        )
        array = scipy.ndimage.interpolation.zoom(self.noise_array, zoom_aspect)
        array = array[:, :, np.newaxis]
        if threshold is not None:
            return np.where(array > threshold, TRANSPARENT, OPAQUE)
        return array


if __name__ == "__main__":
    seed = np.random.randint(0, 1000000)
    generator = RandomNoise(seed, (4, 4))
    with open("../out/out.txt", "w") as file:
        result = generator.generate_noise_array(512)
        print(result.shape)
        file.write(np.array_str(result, max_line_width=500))
    print(f"Done! Seed: {seed}")
