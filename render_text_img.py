from PIL import Image, ImageDraw, ImageFont
import re
from psd_tools import PSDImage


def write_text_file_png(save_to, size, font_size, ttf, text, location, color):
    if not save_to or '.png' not in save_to:
        print('cant find format of image')
        return

    fnt = None
    img = Image.new('RGBA', size, (255, 0, 0, 0))
    if not text:
        img.save(f'{save_to}')
        print(f'save success {save_to}')
        return img
    if ttf:
        fnt = ImageFont.truetype(ttf, font_size)
    d = ImageDraw.Draw(img)
    d.text(location, text, font=fnt, fill=color)

    img.save(f'{save_to}')
    print(f'save success {save_to}')
    return img

#
# write_text_file_png('test_text.png', (1000, 1000), 15, None, None, (723, 140),
#                     (255, 255, 0))
