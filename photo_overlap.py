#!/usr/bin/python
import json
import re
from PIL import Image
import sys

import render_text_img

list_image_object = []


def save_output_file(image, img_text, name):
    img1 = Image.open(image)
    img2 = Image.open(img_text)
    Image.alpha_composite(img1, img2).save(f"{name}.png")


def render_background(psd_path, json_path, option_f, set_text_f, ttf_f, color_f, font_size=30):
    json_file = open(json_path)
    json_obj = json.load(json_file)
    check_size_img = Image.open(f"{psd_path}/{list(option_f[0].values())[0]}.png")
    size = check_size_img.size

    for index, obj in enumerate(json_obj[0]['frame']):
        location = (obj['position']['X'], obj['position']['Y'])

        render_text_img.write_text_file_png(f'background{index}.png', size, font_size,
                                            ttf_f[index], list(set_text_f[index].values())[0], location,
                                            color_f[index])
        save_output_file('background0.png', f'background{index}.png', 'background0')


def photo_stack_with_option(psd_path, json_path, option_f=None, set_text_f=None, color_f=None, ttf_f=None, font_size=None):
    if not option_f or not set_text_f or not json_path:
        print('wrong params root, option, text')
        return
    name = ''
    if font_size:
        render_background(psd_path, json_path, option_f,  set_text_f, ttf_f, color_f, font_size=font_size)
    else:
        render_background(psd_path, json_path, option_f, set_text_f, ttf_f, color_f)

    for index in range(len(option_f)):
        branch = list(option_f[index].values())[0].split('/')
        name += branch[-1] + '_'

    save_output_file(f"{psd_path}/{list(option_f[0].values())[0]}.png", 'background0.png', name)
    for index in range(1, len(option_f)):
        save_output_file(f"{name}.png", f"{psd_path}/{list(option_f[index].values())[0]}.png", name)

    print(f"save success {name}.png")


path, set_text, ttf, color, option, js = [None, [], [], [], [], None]

# if len(sys.argv) < 6:
#     print('Wrong params')
#     sys.exit()

for i in range(len(sys.argv)):
    if sys.argv[i] == '--psd':
        path = sys.argv[i + 1]

    if '--text' in sys.argv[i]:
        set_text.append({
            f"{sys.argv[i]}": sys.argv[i + 1]
        })

    if '--font' in sys.argv[i]:
        ttf.append(
            sys.argv[i + 1]
        )

    if '--option' in sys.argv[i]:
        option.append({
            f"{sys.argv[i]}": sys.argv[i + 1]
        })

    if '--color' in sys.argv[i]:
        color.append(
            sys.argv[i + 1]
        )

    if '--json' in sys.argv[i]:
        js = sys.argv[i + 1]

if not path or not option or not set_text:
    print('wrong params')
    sys.exit()
if len(set_text) != len(color) or len(color) != len(ttf):
    print('need to fill complete in params. Ex : --text1 --text2 --font1 --font2 --color1 --color2')
    sys.exit()

photo_stack_with_option(path, js, option_f=option, set_text_f=set_text, ttf_f=ttf, color_f=color, font_size=25)
