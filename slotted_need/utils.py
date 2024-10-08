import seaborn as sns


def generate_unique_rgba_colors(num_colors, alpha=0.6, border_color=False):
    """
    Generates a list of unique, visually distinct RGBA color strings using HSL.

    Args:
        num_colors (int): Number of unique colors to generate.
        alpha (float): Alpha value for RGBA colors (default: 0.6).
        border_color (boolean): If a matching border color is also required.

    Returns:
        List[str] or List[tuples]: List of unique RGBA color strings or
                                    list of tuples with pair of background
                                    and border RGBA color strings.
    """
    # check if number of colors requested exceed possible unique hues
    if num_colors > 360:
        raise ValueError(
            "Number of colors requested exceeds the unique hue variations.")

    # Initialize color list
    colors = []

    # Get a visually distinct husl palette
    palette = sns.color_palette('husl', num_colors)

    # If border color is required
    if border_color:
        # create a list of tuples with background and border colors
        colors = [
            (f'rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {alpha})',
             f'rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, 1)')
            for r, g, b in palette
        ]

    else:
        # Create a list background color strings only
        colors = [
            f'rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {alpha})'
            for r, g, b in palette
        ]

    return colors
