import glob
import os
import random
import colorsys

from PIL import Image, ImageDraw

def calculate_possibilities():
    return (len(grips) * num_palettes) * (len(pommels) * num_palettes) * (len(crossguards) * num_palettes) * (len(blades) * num_palettes)

def generate_sword_image():
    """Generates a sword image from pieces

    Returns:
        A PIL Image object.
    """

    # Chose a random set of pieces
    grip = open_with_palette(random.choice(grips), random.randint(0, palettes.size[1]))
    pommel = open_with_palette(random.choice(pommels), random.randint(0, palettes.size[1]))
    crossguard = open_with_palette(random.choice(crossguards), random.randint(0, palettes.size[1]))
    blade = generate_blade()

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

    # print("Can't find color in palettes, figuring by value")

    palette_values = (0.4, 0.55, 0.75, 0.95, 1.0)
    v = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)
    output = 0
    while (v[2] > palette_values[output]):
        output += 1

    palette_cache[color] = (output, 0)
    return (output, 0)

def generate_palette(satmod = 1.0, valmod = 1.0):
    """Returns a new generated palette range

    Returns:
        A PIL Image object.
    """
    basehue = random.random()
    modhue = basehue + ((random.random() - 0.5) * 0.2)
    modhue = max(0.0, min(modhue, 1.0))
    hueshift = 0.75
    hues = []
    hues.append(basehue)
    hues.append(lerp(basehue, modhue, hueshift))
    hues.append(modhue)
    hues.append(lerp(basehue, modhue, hueshift))
    hues.append(basehue)

    basesat = random.random()
    satshift = 0.95 - random.random()*0.2
    sats = []
    for i in range(5):
        sats.append(basesat + (random.random() * 0.2))
        basesat *= satshift

    baseval = (random.random() * 0.2) + 0.1
    valshift = 0.1 + random.random() * 0.4
    vals = []
    for i in range(5):
        vals.append(baseval)
        baseval = lerp(baseval, 1.0, valshift)

    output = Image.new("RGBA", (5, 1))
    for i in range(5):
        col = colorsys.hsv_to_rgb(hues[i], sats[i] * satmod, vals[i] * valmod)
        col = (int(col[0] * 255.0), int(col[1] * 255.0), int(col[2] * 255.0))
        output.putpixel((i, 0), col)

    return output


def lerp(a, b, t):
    return (b * t) + (a * (1.0 - t))


def generate_blade():
    """Generates a new blade sprite

    Returns:
        A 32x32 PIL Image object.
    """

    palette = generate_palette(random.random() * 0.2)
    if (random.random() < 0.1): palette = generate_palette(2.0, 1.2)
    output = Image.new("RGBA", (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(output)
    max_length = 19

    # Create shape information
    length = random.randint(10, max_length)
    highlight_length = length * random.random()
    sections = random.randint(2, 4)
    widths = []
    for i in range(sections):
        widths.append(random.randint(2,3))

    # Create lines defining the shape
    left_line = []
    right_line = []

    for i in range(sections):
        basepos = max_length - ((i/sections) * length)
        left_line.append((basepos - widths[i],basepos + widths[i]))
        right_line.append((basepos + widths[i],basepos - widths[i]))

    left_line.append((max_length-length,max_length-length))
    right_line.append((max_length-length,max_length-length))

    # Fill the base color for the blade
    left_polygon = []
    left_polygon.extend(left_line)
    left_polygon.append((max_length,max_length))

    right_polygon = []
    right_polygon.extend(right_line)
    right_polygon.append((max_length,max_length))

    draw.polygon(left_polygon, palette.getpixel((1,0)))
    draw.polygon(right_polygon, palette.getpixel((2,0)))

    # Draw the middle ridge
    draw.line([(max_length,max_length), (max_length - length, max_length - length)], palette.getpixel((3,0)))
    draw.line([(max_length,max_length), (max_length - highlight_length, max_length - highlight_length)], palette.getpixel((4,0)))

    # Draw the outline
    draw.line(left_line, palette.getpixel((0,0)))
    draw.line(right_line, palette.getpixel((0,0)))

    del draw
    return output


if __name__ == "__main__":
    print("Generating blades...")

    # Set the random seed to have deterministic results.
    #random.seed("teddybear")

    # palettes = Image.open("./images/palettes.png")

    num_palettes = 32
    palettes = Image.new("RGBA", (5, num_palettes))
    for i in range(num_palettes):
        palettes.paste(generate_palette(), (0, i))
    palettes.save("./images/genpalette.png")

    palette_cache = {}

    # Load up individual pieces
    grips = [os.path.normpath(g) for g in glob.glob('./images/grips/*.png')]
    pommels = [os.path.normpath(g) for g in glob.glob('./images/pommels/*.png')]
    crossguards = [os.path.normpath(g) for g in glob.glob('./images/crossguards/*.png')]
    blades = [os.path.normpath(g) for g in glob.glob('./images/blades/*.png')]

    print("Possibility space: {}".format(calculate_possibilities()))

    sheet_size = 32 * 8, 32 * 4
    sprite_sheet = Image.new('RGBA', sheet_size)

    # Build the sprite sheet
    for x in range(0, sheet_size[0], 32):
        for y in range(0, sheet_size[1], 32):
            image = generate_sword_image()
            sprite_sheet.paste(image, (x, y))

    # Save the sprite sheet to file
    sprite_sheet.save('out.png')
    print("Done!")
