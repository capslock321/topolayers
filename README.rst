topolayers - random topography like images
===========================================
This is a repository featuring randomly generated topographic map like images.
It works by creating a noise map, applying a threshold and replacing pixels that meet the threshold,
with colors from a user defined gradient.

Usage
-----------------------
First configure `config.json` and tweak the settings to your liking. The settings are as follows:

+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| Configuration Argument |                                                       Argument Description                                                       |
+========================+==================================================================================================================================+
| Seed                   | The seed to generate the image.                                                                                                  |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| zoom_aspect            | The noise zoom aspect.                                                                                                           |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| noise_size             | The initial noise size. Higher the number, the more complexity the final image will have.                                        |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| output_path            | The path in which to dump the final image at.                                                                                    |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| background_color       | The color for any unfilled pixels.                                                                                               |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| colors                 | The gradient colors. The resulting gradient is a inter polarization from the first color to the second, second to third etc etc. |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| gradient_steps         | The amount of layers that will be generated between each color.                                                                  |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| luminosity             | The difference between each color while fading between two colors.                                                               |
+------------------------+----------------------------------------------------------------------------------------------------------------------------------+

Afterwards, run `main.py` and check the directory where you have specified your output path for the final generated image.
The file is named after the seed, for example, if your seed is `7`, the deposited file will be called `7.png`.

License
-----------------------
Copyright (c) 2022 capslock321
See LICENSE for additional details.
