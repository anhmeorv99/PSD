import json
import os
import itertools
import threading

import cv2
from psd_tools import PSDImage

list_layer_parent = []


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


def write_file_png(name, path, branch):
    if not os.path.isfile(f'./lab1/{name}.png'):
        layer_img = PSDImage.open(path)
        set_visible_all(layer_img, False)
        set_visible(layer_img, False)
        visible_branch(layer_img, branch)
        image = layer_img.composite(ignore_preview=True)
        image.save(f'./lab1/{name}.png')


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
            name = ''
            branch = []
            while tmp.parent is not None:
                name += tmp.name + '+'
                branch.append(tmp.name)
                tmp = tmp.parent

            if layer.name.lower() == 'background' and layer.parent is None:
                continue
            list_layers.append({
                "name": f"{layer.name}",
                "url": f"./lab1/{name}.png"
            })

            write_file_png(name, path, branch)

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

    try:
        start()
        t1 = threading.Thread(target=write_file_png)
        t2 = threading.Thread(target=write_file_png)
        t3 = threading.Thread(target=write_file_png)
        t4 = threading.Thread(target=write_file_png)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
    except Exception as e:
        print(e)
