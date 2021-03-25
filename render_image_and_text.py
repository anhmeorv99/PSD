from PIL import Image

import find_location_frame
from psd_tools import PSDImage
import render_text_img

list_image_object = []


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


def find_option(root, option):
    branch = []
    img = None
    for layer in reversed(list(root.descendants())):
        if layer.name == option:
            img = layer
            break
    if img is None:
        return None
    tmp = img
    while tmp.parent is not None:
        branch.append(tmp.name)
        tmp = tmp.parent
    visible_branch(root, branch)
    return img


def set_visible_have_background(group, mode):
    for layer in group:
        if layer.kind == 'group' and layer.name.lower() != 'background':
            layer.visible = mode
        else:
            layer.visible = True


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


def photo_stack_with_option(root, option=None, set_text=None, color=None, ttf=None):
    if not option:
        print('must option')
        return
    set_visible_have_background(root, False)
    check_option = find_option(root, option)
    if check_option:
        for layer in root:
            if layer.kind == 'group' and 'text -' in layer.name.lower():
                frame_text = find_location_frame.find_location_and_text(layer)
                frame = frame_text[0]
                text = frame_text[1]
                location = (frame['frame'][0]['position']['X'], frame['frame'][0]['position']['Y'])
                font_size = text['text'][0]['data']['font_size']

                img_text = render_text_img.write_text_file_png(f'{layer.name}.png',
                                                               root.size,
                                                               int(font_size),
                                                               ttf,
                                                               set_text,
                                                               location,
                                                               color
                                                               )
                image = root.composite(ignore_preview=True)
                image.save(f'{option}.png')
                save_output_file(f"{option}.png", f'{layer.name}.png', option)


psd = PSDImage.open('/home/anhmeo/Desktop/1000x1000 (1).psd')
photo_stack_with_option(psd, option='Beagle', set_text='Hello world!', ttf='./font/OpenSans-ExtraBold.ttf', color='#FF0000')

#
# psd = PSDImage.open('/home/anhmeo/Desktop/1000x1000 (1).psd')
# for layer in reversed(list(psd.descendants())):
#     if layer.name == 'Beagle':
#         # print(layer.parent)
