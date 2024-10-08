import random


def generate_unique_rgba_colors(num_colors, alpha=0.6, border_color=False):
    """
    Generates a list of unique RGBA color strings.

    Args:
        num_colors (int): Number of unique colors to generate.
        alpha (float): Alpha value for RGBA colors (default: 0.6).

    Returns:
        List[str] or List[tuples]: List of unique RGBA color strings or
                                    list of tuples with pair of background
                                    and border RGBA color strings.
    """
    # check if number of colors requested exceed possible unique RGB numbers
    if num_colors > 256**3:
        raise ValueError(
            "Number of colors requested exceeds the unique RGB color space.")

    # Initialize used colours set and chosen color list
    used_colors = set()
    colors = []

    # create random color tuples until requirement is met
    while len(colors) < num_colors:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color_tuple = (r, g, b)

        # add color to lists if not already added
        if color_tuple not in used_colors:
            used_colors.add(color_tuple)
            bg_color_str = f'rgba({r}, {g}, {b}, {alpha})'

            if border_color:
                bd_color_str = f'rgba({r}, {g}, {b}, 1)'
                colors.append((bg_color_str, bd_color_str))

            else:
                colors.append(bg_color_str)

    return colors
