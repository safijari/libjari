from libjari.jpath import JPath
from PIL import Image, ImageDraw, ImageFont


def draw_text(text, text_size):
    fnt = ImageFont.truetype(JPath.from_home("Downloads/mononoki-Bold.ttf").str, text_size)
    w, h = fnt.getsize(text)

    txt = Image.new("RGBA", (w, h), (255, 255, 255, 0))

    d = ImageDraw.Draw(txt)

    # draw text, half opacity
    d.text((0, 0), text, font=fnt, fill=(255, 255, 255))

    return txt
