#!/usr/bin/python
import re

from PIL import Image

import sys

import find_location_frame
from psd_tools import PSDImage
import render_text_img

list_image_object = []


def count_options(root):
    count = 0
    for layer in root:
        if layer.kind == 'group' and layer.name.lower() != 'background':
            for child in layer:
                if child.kind == 'group':
                    count += 1
    return count


def visible_branch(root, branch):
    if len(branch) == 0:
        return
    for layer in root:
        if layer.name in branch or layer.name.lower() == 'background':
            if layer.name.lower() == 'background' and layer.kind == 'group':
                continue
            layer.visible = True
            if layer.name in branch:

                branch.remove(layer.name)
                if layer.kind == 'group':
                    visible_branch(layer, branch)


def find_option(root, option_f):
    count = 0
    name = ''
    for opt in option_f:
        branch = list(opt.values())[0].split('/')
        list_img = []

        for layer in reversed(list(root.descendants())):
            if layer.name == branch[-1]:
                list_img.append(layer)

        for img in list_img:
            branch_img = []
            while img.parent:
                branch_img.append(img.name)
                img = img.parent
            if branch_img == list(reversed(branch)):
                visible_branch(root, branch)
                name += f'{branch_img[0]}_'
                count += 1

    if count == len(option_f):
        return name
    return None


def set_visible_have_background(group, mode):
    for layer in group:
        if layer.kind == 'group' and layer.name.lower() != 'background':
            layer.visible = mode
            set_visible_have_background(layer, mode)
        else:
            if layer.kind == 'group' and layer.name.lower() == 'background':
                layer.visible = True
                continue
            layer.visible = False


def save_output_file(image, img_text, name):
    img1 = Image.open(image)
    img2 = Image.open(img_text)
    Image.alpha_composite(img1, img2).save(f"{name}.png")


def set_visible_all(root, mode):
    for layer in root:
        if layer.kind == 'group':
            layer.visible = mode
            set_visible_all(layer, mode)
        else:
            layer.visible = mode


def render_background(root, set_text_f, ttf_f, color_f):
    for index in range(len(set_text_f)):
        index_of_text_frame = re.findall(r"\d+", list(set_text_f[index].keys())[0])
        if len(index_of_text_frame) > 0:
            index_of_text_frame = index_of_text_frame[0]
        else:
            index_of_text_frame = ''
        for layer in root:
            if layer.name.lower() == 'background':
                continue
            if layer.kind == 'group' and f"text - {index_of_text_frame}" in layer.name.lower():
                frame_text = find_location_frame.find_location_and_text(layer)
                frame = frame_text[0]
                text = frame_text[1]
                location = (frame['frame'][0]['position']['X'], frame['frame'][0]['position']['Y'])
                font_size = text['text'][0]['data']['font_size']

                render_text_img.write_text_file_png(f'background{index}.png', root.size, int(font_size),
                                                    ttf_f[index], list(set_text_f[index].values())[0], location, color_f[index])
                save_output_file('background0.png', f'background{index}.png', 'background0')


def photo_stack_with_option(root, option_f=None, set_text_f=None, color_f=None, ttf_f=None):
    if not option_f or not set_text_f or not root:
        print('wrong params root, option, text')
        return

    set_visible_have_background(root, False)
    check_option = find_option(root, option_f)
    if check_option:
        render_background(root, set_text_f, ttf_f, color_f)
        image = root.composite(ignore_preview=True)
        image.save(f'{check_option}.png')
        save_output_file(f"{check_option}.png", 'background0.png',
                         f"{check_option}")


path, set_text, ttf, color, option = [None, [], [], [], []]

if len(sys.argv) < 6:
    print('Wrong params')
    sys.exit()

for i in range(len(sys.argv)):
    if sys.argv[i] == '--psd':
        path = sys.argv[i + 1]

    if '--text' in sys.argv[i]:
        set_text.append({
            f"{sys.argv[i]}": sys.argv[i+1]
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

if not path or not option or not set_text:
    print('wrong params')
    sys.exit()

psd = PSDImage.open(path)
if len(option) != count_options(psd):
    print(f'invalid option or too many options. options : {len(option)}, options_psd : {count_options(psd)}')
    sys.exit()

photo_stack_with_option(psd, option_f=option, set_text_f=set_text, ttf_f=ttf, color_f=color)
