color_names = {
    "white": "#FFFFFF",
    "silver": "#C0C0C0",
    "gray": "#808080",
    "black": "#000000",
    "red": "#FF0000",
    "maroon": "#800000",
    "yellow": "#FFFF00",
    "olive": "#808000",
    "lime": "#00FF00",
    "green": "#008000",
    "aqua": "#00FFFF",
    "teal": "#008080",
    "blue": "#0000FF",
    "navy": "#000080",
    "fuchsia": "#FF00FF",
    "purple": "#800080",
    "white": "#FFFFFF",
    "gray": "#C0C0C0",
    "dark gray": "#808080",
    "black": "#000000",
    "high red": "#FF0000",
    "low red": "#800000",
    "yellow": "#FFFF00",
    "brown": "#808000",
    "high green": "#00FF00",
    "green": "#00FF00",
    "low green": "#008000",
    "high cyan": "#00FFFF",
    "cyan": "#00FFFF",
    "low cyan": "#008080",
    "high blue": "#0000FF",
    "low blue": "#000080",
    "high magenta": "#FF00FF",
    "magenta": "#FF00FF",
    "low magenta": "#800080",
}


def convert_color(color_str):
    if isinstance(color_str, tuple):
        return color_str
    if color_str.lower() in color_names:
        color_str = color_names[color_str.lower()]
    color_str = color_str.replace("#", "")
    hr, hg, hb = color_str[:2], color_str[2:4], color_str[4:6]

    return int(hr, 16), int(hg, 16), int(hb, 16)

def convert_color_float(color_str):
    if isinstance(color_str, tuple):
        return color_str
    r, g, b = convert_color(color_str)
    return r/255.0, g/255.0, b/255.0