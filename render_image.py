import concurrent
import json
import os
import itertools
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
from psd_tools import PSDImage

list_image_object = []


def send_with_thread_executor(max_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for image in list_image_object:
            futures.append(
                executor.submit(
                    write_file_png, image[0], image[1], image[2], image[3]
                )
            )


def gen_path(current_path, branch):
    if len(branch) == 1:
        return current_path
    if len(branch) > 1:

        branch.reverse()
        for index in range(0, len(branch) - 1, 1):
            if os.path.exists(f"{current_path}/{branch[index]}"):
                current_path += f'/{branch[index]}'
                continue
            os.mkdir(os.path.join(current_path, branch[index]))
            current_path += f'/{branch[index]}'
        return current_path


def set_visible(group, mode):
    for layer in group:
        if layer.kind == 'group' and layer.name.lower() != 'background':
            layer.visible = mode
        else:
            if layer.kind == 'group':
                layer.visible = False
            else:
                layer.visible = True


def set_visible_all(root, mode):
    for layer in root:
        if layer.kind == 'group':
            layer.visible = mode
            set_visible_all(layer, mode)
        else:
            layer.visible = mode


def visible_branch(root, branch):
    if len(branch) == 0:
        return
    for layer in root:
        if layer.name in branch or layer.name.lower() == 'background':
            layer.visible = True
            if layer.name in branch:
                branch.remove(layer.name)
                if layer.kind == 'group':
                    visible_branch(layer, branch)


def write_file_png(name, path, branch, current_path):
    if not os.path.isfile(f'{current_path}/{name}.png'):
        layer_img = PSDImage.open(path)
        set_visible_all(layer_img, False)
        set_visible(layer_img, False)
        visible_branch(layer_img, branch)
        image = layer_img.composite(ignore_preview=True)
        image.save(f'{current_path}/{name}.png')
        print(f'save successfully file: {name}')


def render_img(layers, path):
    list_layers = []
    for layer in layers:
        if layer.kind == 'group':
            if layer.name.lower() == 'background':
                list_layers.append({
                    "name": layer.name,
                    "url": f"./lab1/{layer.name}_.png"
                })
                continue
            layer.visible = True
            obj = {
                f"{layer.name}": render_img(layer, path),
            }
            list_layers.append(obj)
        else:

            tmp = layer
            branch = []
            current_path = './lab1'
            while tmp.parent is not None:
                branch.append(tmp.name)
                tmp = tmp.parent

            if layer.name.lower() == 'background' and layer.parent is None:
                continue

            current_path = gen_path(current_path, branch)
            list_layers.append({
                "name": f"{layer.name}",
                "url": f"{current_path}/{layer.name}.png"
            })

            list_image_object.append([layer.name, path, branch, current_path])
            if len(list_image_object) > 10:
                send_with_thread_executor(5)
                list_image_object.clear()

    return list_layers


def start():
    psd = PSDImage.open('/home/anhmeo/Desktop/Once upon a time there was a girl who loves dogs. The end..psd')
    set_visible_all(psd, False)
    set_visible(psd, False)

    content = {
        "Root": render_img(psd, '/home/anhmeo/Desktop/Once upon a time there was a girl who loves dogs. The end..psd')
    }

    with open('./output.json', 'w') as f:
        f.write(json.dumps(content))
        f.close()


if __name__ == '__main__':
    start()
