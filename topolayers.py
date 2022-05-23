import os
import time
import json
import logging

from topolayers import TopographyMap, Patterns

# We can throw good coding practices out the house for this file.
# For now at least. Also, this works best with high contrast colors.

fmt = "[%(asctime)s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt, datefmt="%m/%d/%Y %I:%M:%S %p")

print("Generating Topography Map...")
start = time.time()

with open("config.json", "r") as file:
    settings = json.load(file)
    zoom_aspect = settings.get("zoom_aspect")
    noise_size = (settings["noise_size"]["x"], settings["noise_size"]["y"])
    background_color = tuple(settings.get("background_color"))
    # Just for this script, the background_color argument is pretty much useless.
    gradient_steps = settings.get("gradient_steps")
    luminosity = settings.get("luminosity")
    colors = settings.get("colors")
    seed = settings.get("seed")
    output_path = settings.get("output_path")

generator = TopographyMap(seed, noise_size, background_color, zoom_aspect)
noise = sorted(generator.get_noise(zoom_aspect=zoom_aspect).ravel(), reverse=True)
pattern = Patterns(noise, gradient_steps=gradient_steps)

values = pattern.interpolate_colors(colors, luminosity=luminosity)  # Change method name.

for rgb, layer in values:
    generator.add_layer(rgb, threshold=max(layer))


if __name__ == "__main__":
    output_path = os.path.join(output_path, f"{generator.seed}.png")
    generator.generate_image(output_path)
    print(f"Generated Topography Map with seed: {seed}")
    print(f"Total time elapsed: {time.time() - start:.2f}s")
