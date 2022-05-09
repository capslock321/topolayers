import logging
import dataclasses

import numpy as np
from PIL import Image

from .noise import RandomNoise
from .exceptions import InvalidRGB, LayerRequired, InvalidThreshold

TRANSPARENT = (0, 0, 0, 0)
OPAQUE = (0, 0, 0, 232)

logger = logging.getLogger(__name__)


class TopographyMap:
    def __init__(
        self,
        seed: int = None,
        array_size: np.ndarray = (4, 4),
        background_color: tuple = TRANSPARENT,
        zoom_aspect: int = 512,
    ):
        self.seed: int = seed  # str to int as seed
        self.array_size: np.ndarray = array_size
        self.zoom_aspect: int = zoom_aspect
        self.layers: list = []
        if self._is_valid_rgb(background_color):
            # Why does this parameter even exist?
            self.background_color: tuple = background_color
        else:
            raise InvalidRGB("An invalid RGB tuple was provided!")

    def _is_valid_rgb(self, rgb: tuple):
        if len(rgb) != 4:
            raise InvalidRGB("A RGB tuple must only contain 4 items!")
        return all([isinstance(k, int) for k in rgb])

    def get_noise(self, zoom_aspect: int = 512) -> np.ndarray:
        noise = RandomNoise(self.seed, self.array_size)
        return noise.generate_noise_array(zoom_aspect=zoom_aspect)

    def _preprocess_image(self, zoom_aspect: int = 512, threshold: int = 0.5):
        noise = RandomNoise(self.seed, self.array_size)
        if 1 <= threshold < 0:
            raise InvalidThreshold("Threshold must be a number between 0.0 and 1.0.")
        return noise.generate_noise_array(threshold, zoom_aspect)

    def add_layer(self, color: tuple, threshold: int = 0.5):
        logger.info(f"Adding layer with color {color} and threshold {threshold}.")
        noise_map = self._preprocess_image(self.zoom_aspect, threshold)
        noise_map[np.all(noise_map == OPAQUE, axis=-1)] = color
        layer = TopographyLayer(noise_map, threshold)
        return self.layers.append(layer)

    def generate_image(self, output_path: str = None):
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
            master.save(output_path)
        return master


@dataclasses.dataclass
class TopographyLayer:
    def __init__(self, noise_map: np.ndarray, threshold: int):
        self.noise_map: np.ndarray = noise_map
        self.threshold: int = threshold
