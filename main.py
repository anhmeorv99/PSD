import json
import os
import itertools
import cv2
from psd_tools import PSDImage

psd = PSDImage.open('/home/anhmeo/Desktop/Once upon a time there was a girl who loves dogs. The end..psd')

list_layer_parent = []
found_2_dog = 0


def find_parent(layer):
    grant = layer.parent
    if grant is None:
        return []
    list_parent = []
    count_parent = 0
    for parent in grant:
        if parent.kind == 'group' and parent.name.lower() != 'background':
            count_parent += 1
            list_parent.append(parent)
        elif parent.name.lower() == 'background':
            parent.visible = True
    if count_parent > 0:
        return list_parent
    return []


def set_visible(group, mode, root):
    name = ""
    for layer in group:
        if layer.name.lower() != 'background':
            layer.visible = mode
            name += '_' + layer.name
        else:
            if layer.parent.name == root.name:
                layer.visible = True
    return name


def check_duplicate_parent(combination):
    parent_set = set()
    for layer_img in combination:
        parent_set.add(layer_img.parent)

    return len(parent_set) < len(combination)


def export_img(list_groups, grant):
    list_img = []
    for group in list_groups:
        group.visible = True
        if group.name.lower() == 'background':
            continue
        for layer_img in group:
            if layer_img.kind != 'group' and layer_img.name.lower() != 'background':
                layer_img.visible = False
                list_img.append(layer_img)
            elif layer_img.name.lower() == 'background':
                layer_img.visible = True
            else:
                layer_img.visible = False

    list_img = itertools.permutations(list_img, r=len(list_groups))

    for index, combination in enumerate(list_img):
        if not check_duplicate_parent(combination):
            name = set_visible(combination, True, grant)
            if not os.path.isfile(f'./lab/{name}.png'):
                image = grant.composite(ignore_preview=True)
                image.save(f'./lab/{name}.png')
            set_visible(combination, False, grant)
            yield {
                "name": name,
                "url": f'./lab/{name}.png'
            }


def get_object(root, layers, background):
    result = []
    for layer in layers:
        if layer.is_group():
            layer.visible = True
            if layer.name.lower() == background:
                obj = {
                    "name": layer.name,
                    "url": root.composite().save(f"{layer.name}.png")
                }
                result.append(obj)
                continue
            else:
                obj = {
                    f"{layer.name}": get_object(root, layer, background)
                }
                result.append(obj)

        else:
            list_parent = []
            layer_parent = layer.parent
            if layer.parent.name == root.name:
                continue

            list_parent = find_parent(layer_parent)
            if len(list_parent) > 0:
                for parent in list_parent:
                    if parent.name != layer.parent.name:
                        parent.visible = False

            if list_parent in list_layer_parent:
                if len(list_parent) > 0:

                    continue
                else:
                    result.append({
                        "name": f"{layer.name}",
                        "url": f"./lab/{layer.name}.png"
                    })

                    layer.visible = True
                    if not os.path.isfile(f'./lab/{layer.name}.png'):
                        image = root.composite(ignore_preview=True)
                        image.save(f'./lab/{layer.name}.png')
                    continue
            list_layer_parent.append(list_parent)
            list_combination = []
            if len(list_parent) > 1 and list_parent[0].parent.name != root.name:
                for item in export_img(list_parent, root):
                    list_combination.append(item)
                result.append({
                    "name": f"{layer.name}",
                    "url": f"./lab/{layer.name}.png",
                    "combination": list_combination
                })

            elif len(list_parent) == 1:
                grant = list_parent[0].parent
                if not grant.parent or grant.name == root.name:
                    for index, item in enumerate(grant.parent):
                        if item.name.lower() == background or item.name == grant.name:
                            grant.parent[index].visible = True
                        else:
                            grant.parent[index].visible = False

                set_visible(layer_parent, False, root)
                for item in layer_parent:
                    item.visible = True
                    name = item.name
                    result.append({
                        "name": f"{layer.name}",
                        "url": f"./lab/{layer.name}.png"
                    })
                    if not os.path.isfile(f'./lab/{name}.png'):
                        image = root.composite(ignore_preview=True)
                        image.save(f'./lab/{name}.png')
                    item.visible = False
                set_visible(layer_parent.parent, False, root)


set_visible(psd, False, psd)

get_object(psd, psd, 'background')
