import os
import time
import json
import logging

import numpy as np

from PIL import Image
from topolayers import TopographyMap

print("Generating Topography Rings...")
start = time.time()

fmt = "[%(asctime)s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt, datefmt="%m/%d/%Y %I:%M:%S %p")

with open("config.json", "r") as file:
    settings = json.load(file)
    zoom_aspect = settings.get("zoom_aspect")
    noise_size = (settings["noise_size"]["x"], settings["noise_size"]["y"])
    background_color = tuple(settings.get("background_color"))
    gradient_steps = settings.get("gradient_steps")
    luminosity = settings.get("luminosity")
    colors = settings.get("colors")
    seed = settings.get("seed")
    output_path = settings.get("output_path")

generator = TopographyMap(seed, noise_size, background_color, zoom_aspect)
noise = sorted(generator.get_noise(zoom_aspect=zoom_aspect).ravel(), reverse=True)

ring_amount = 20
ring_indices = 4
cl = len(noise) // ring_amount
chunks = [noise[x:x + cl] for x in range(0, len(noise), cl)]

overlay_image = Image.open("examples/prod/gilded/gilded.png")

for ring, chunk in enumerate(chunks):
    if ring % ring_indices == 0:
        generator.add_layer([0, 0, 0, 255], threshold=max(chunk))
    else:
        generator.add_layer([35, 35, 35, 255], threshold=max(chunk))


def generate_ringmap(source_image: Image):
    master = generator.generate_image(output_path)
    image = source_image.resize(master.size).convert("RGBA")
    master_image, overlay = np.array(master), np.array(image)
    mask = (master_image == [0, 0, 0, 255])
    master_image[mask] = overlay[mask]
    return master_image


if __name__ == "__main__":
    output_path = os.path.join(output_path, f"gilded/{generator.seed}.png")
    master = generate_ringmap(overlay_image)
    Image.fromarray(master, mode="RGBA").save(output_path)
    print(f"Generated Topography Map with seed: {seed}")
    print(f"Total time elapsed: {time.time() - start:.2f}s")
