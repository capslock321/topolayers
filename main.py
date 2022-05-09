import json
import itertools

from PIL import ImageColor
from colour import Color
from topolayers import TopographyMap


def pairwise(iterable):
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
    gradient_steps = settings.get("gradient_steps")
    luminosity = settings.get("luminosity")
    colors = settings.get("colors")
    seed = settings.get("seed")

generator = TopographyMap(seed, noise_size, background_color, zoom_aspect)
noise = sorted(generator.get_noise(zoom_aspect=zoom_aspect).ravel(), reverse=True)

gradient_colors = list()

for color1, color2 in pairwise(colors):
    for iteration in range(gradient_steps):
        rgb1 = list(ImageColor.getrgb(Color(color1).get_hex()))
        rgb2 = list(ImageColor.getrgb(Color(color2).get_hex()))
        rgb = list(interpolerate(rgb1, rgb2, luminosity * (iteration + 1)))
        rgb.append(255)  # Make full opaque
        rgb = [c if c <= 255 else 255 for c in rgb]
        gradient_colors.append([int(c) for c in rgb])

c = len(noise) // len(gradient_colors)
chunks = [noise[x : x + c] for x in range(0, len(noise), c)]

# gradient_colors = gradient_colors[::-1]

for rgb, layer in zip(gradient_colors, chunks):
    print(rgb, max(layer), len(layer))
    generator.add_layer(rgb, threshold=max(layer))

generator.generate_image(f"./out/production/{generator.seed}.png")
print("Topgraphy Map Generated!")
print(f"Seed: {generator.seed}")
