import glob
import os
import random
import colorsys

from PIL import Image

def calculate_possibilities():
    return (len(grips) * palettes.size[0]) * (len(pommels) * palettes.size[0]) * (len(crossguards) * palettes.size[0]) * (len(blades) * palettes.size[0])

def generate_sword_image():
    """Generates a sword image from pieces

    Returns:
        A PIL Image object.
    """

    # Chose a random set of pieces
    grip = open_with_palette(random.choice(grips), random.randint(0, palettes.size[1]))
    pommel = open_with_palette(random.choice(pommels), random.randint(0, palettes.size[1]))
    crossguard = open_with_palette(random.choice(crossguards), random.randint(0, palettes.size[1]))
    blade = open_with_palette(random.choice(blades), random.randint(0, palettes.size[1]))

    composite = Image.new('RGBA', (32, 32))

    # Paste with mask needs to be RGBA data.
    composite.paste(grip)
    composite.paste(pommel, (0, 0), pommel.convert())
    composite.paste(blade, (0, 0), blade.convert())
    composite.paste(crossguard, (0, 0), crossguard.convert())

    return composite

def open_with_palette(image_path, palette):
    image = Image.open(image_path, 'r')
    return palette_swap(image, palette)

def palette_swap(image, palette):
    """Returns the palette column for the given pixel. 

    Returns:
        A PIL Image object.
    """

    image = image.convert("RGBA")
    output = image.copy()

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            col = image.getpixel((i, j))
            if col[3] > 0:
                output.putpixel((i, j), get_palette_color(get_value_index(col), palette))

    return output


def get_palette_color(value_index, palette_shift):
    out = (value_index[0], (value_index[1] + palette_shift) % palettes.size[1])
    return palettes.getpixel(out)

def get_value_index(color):
    """Returns the palette column for the given pixel. If color doesn't exist
    in any palettes, return index based on value. 

    Returns:
        A tuple containing:
            palette column (0 - 4)
            palette index, if it exists (int)
    """

    # First check the cache
    if color in palette_cache:
        return palette_cache[color]

    for i in range(palettes.size[0]):
        for j in range(palettes.size[1]):
            if palettes.getpixel((i, j)) == color:
                palette_cache[color] = (i, j)
                return (i, j)

    print("Can't find color in palettes, figuring by value")

    palette_values = (0.0, 0.4, 0.55, 0.75, 0.95)
    v = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)
    output = 0
    while (v > palette_values[output]):
        output += 1

    palette_cache[color] = (output, 0)
    return (output, 0)


if __name__ == "__main__":
    print("Generating blades...")

    # Set the random seed to have deterministic results.
    random.seed("teddybear")

    palettes = Image.open("./images/palettes.png")
    palette_cache = {}

    # Load up individual pieces
    grips = [os.path.normpath(g) for g in glob.glob('./images/grips/*.png')]
    pommels = [os.path.normpath(g) for g in glob.glob('./images/pommels/*.png')]
    crossguards = [os.path.normpath(g) for g in glob.glob('./images/crossguards/*.png')]
    blades = [os.path.normpath(g) for g in glob.glob('./images/blades/*.png')]

    print("Possibility space: {}".format(calculate_possibilities()))

    sheet_size = 32 * 16, 32 * 64
    sprite_sheet = Image.new('RGBA', sheet_size)

    # Build the sprite sheet
    for x in range(0, sheet_size[0], 32):
        for y in range(0, sheet_size[1], 32):
            image = generate_sword_image()
            sprite_sheet.paste(image, (x, y))

    # Save the sprite sheet to file
    sprite_sheet.save('out.png')
    print("Done!")
