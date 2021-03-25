from PIL import Image, ImageDraw, ImageFont


def write_text_file_png(save_to, size, font_size, tff, text, location, color):
    img = Image.new('RGBA', size, (255, 0, 0, 0))

    fnt = ImageFont.truetype(tff, font_size)
    d = ImageDraw.Draw(img)
    d.text(location, text, font=fnt, fill=color)

    img.save(f'{save_to}')


write_text_file_png('test_text.png', (1000, 1000), 15, './font/OpenSans-Bold.ttf', "Xin Chao", (723, 140), (255, 255, 0))
