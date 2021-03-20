import json
import os
import itertools
import cv2
from psd_tools import PSDImage

psd = PSDImage.open('/home/anhmeo/Desktop/Once upon a time there was a girl who loves dogs. The end..psd')

list_layer_parent = []


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


def set_visible(group, mode):
    name = ""
    for layer in group:
        layer.visible = mode
        name += '_' + layer.name
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
            name = set_visible(combination, True)
            if not os.path.isfile(f'./lab/{name}.png'):
                image = grant.composite()
                image.save(f'./lab/{name}.png')
            set_visible(combination, False)
            yield {
                "name": name,
                "url": f'./lab/{name}.png'
            }


def get_object(root, layers):
    list_layers = []

    for layer in layers:
        if layer.is_group():
            layer.visible = True
            if layer.name.lower() != 'background':
                obj = {
                    f"{layer.name}": get_object(root, layer),
                }
                list_layers.append(obj)
            else:
                layer.visible = True
            #     if not os.path.isfile(f'./lab/{layer.name}.png'):
            #         list_layers.append({
            #             "name": f"{layer.name}",
            #             "url": f"./lab/{layer.name}.png"
            #         })
            #         image = layers.composite()
            #         image.save(f'./lab/{layer.name}.png')
            #     continue
        else:
            if layer.name.lower() == 'background':
                layer.visible = True

            layer_parent = layer.parent
            list_parent = find_parent(layer_parent)
            if list_parent in list_layer_parent:
                if len(list_parent) > 0:
                    continue
                else:
                    layer.visible = True
                    if not os.path.isfile(f'./lab/{layer.name}.png'):
                        list_layers.append({
                            "name": f"{layer.name}",
                            "url": f"./lab/{layer.name}.png"
                        })
                        image = layers.composite()
                        image.save(f'./lab/{layer.name}.png')
                    continue
            list_layer_parent.append(list_parent)
            list_combination = []
            obj = {
                "name": layer.parent.name,
                "combinations": [],
                "child": []

            }
            if len(list_parent) > 1:
                set_visible(list_parent, True)
                for item in export_img(list_parent, list_parent[0].parent):
                    list_combination.append(item)
                obj["combinations"] = list_combination
            elif len(list_parent) == 1:
                grant = list_parent[0].parent
                for index, item in enumerate(grant.parent):
                    if item.name.lower() == 'background' or item.name == grant.name:
                        grant.parent[index].visible = True
                    else:
                        grant.parent[index].visible = False

                set_visible(layer_parent, False)
                for item in layer_parent:
                    item.visible = True
                    name = item.name
                    obj["child"].append({
                        "name": f"{item.name}",
                        "url": f"./lab/{item.name}.png"
                    })
                    if not os.path.isfile(f'./lab/{name}.png'):
                        tmp = item.parent
                        try:
                            while True:
                                if tmp.parent.name != root.name:
                                    tmp = tmp.parent
                                    tmp.visible = True
                                else:
                                    break
                        except Exception:
                            pass

                        image = tmp.composite()
                        image.save(f'./lab/{name}.png')
                    item.visible = False

            list_layers.append(obj)
    return list_layers


content = {
    "layers": get_object(psd, psd)
}

print(json.dumps(content))
