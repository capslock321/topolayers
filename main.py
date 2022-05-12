import os
import json
import itertools

from PIL import ImageColor
from topolayers import TopographyMap

# We can throw good coding practices out the house for this file.
# For now at least. Also, this works best with high contrast colors.


def pairwise(iterable):
    # Copied from the docs cuz too lazy to do write own.
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def interpolerate(color1: tuple, color2: tuple, luminosity: float):
    new_r = (color2[0] - color1[0]) * luminosity + color1[0]
    new_g = (color2[1] - color1[1]) * luminosity + color1[1]
    new_b = (color2[2] - color1[2]) * luminosity + color1[2]
    return new_r, new_g, new_b


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

gradient_colors = list()

for color1, color2 in pairwise(colors):
    for iteration in range(gradient_steps):
        rgb1 = list(ImageColor.getrgb(color1))
        rgb2 = list(ImageColor.getrgb(color2))
        rgb = list(interpolerate(rgb1, rgb2, luminosity * (iteration + 1)))
        rgb.append(255)  # Make full opaque
        rgb = [c if c <= 255 else 255 for c in rgb]
        rgb = [c if c >= 0 else 0 for c in rgb]
        gradient_colors.append([int(c) for c in rgb])

c = len(noise) // len(gradient_colors)
chunks = [noise[x: x + c] for x in range(0, len(noise), c)]

# gradient_colors = gradient_colors[::-1]

for rgb, layer in zip(gradient_colors, chunks):
    print(f"Adding layer with color {rgb} and threshold of {max(layer):.2f}.")
    generator.add_layer(rgb, threshold=max(layer))

generator.generate_image(os.path.join(output_path, f"{generator.seed}.png"))
print("Topgraphy Map Generated!")
print(f"Seed: {generator.seed}")
