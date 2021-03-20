import json
import os
import itertools

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
    if count_parent > 1:
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
        for layer_img in group:
            if layer_img.kind != 'group' and layer_img.name.lower() != 'background':
                layer_img.visible = False
                list_img.append(layer_img)
            else:
                layer_img.visible = True

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


def get_object(layers):
    list_layers = []

    for layer in layers:
        if layer.is_group():
            layer.visible = True
            if layer.name.lower() != 'background':
                obj = {
                    f"{layer.name}": get_object(layer),
                }
                list_layers.append(obj)
            else:
                if not os.path.isfile(f'./lab/{layer.name}.png'):
                    list_layers.append({
                        "name": f"{layer.name}",
                        "url": f"./lab/{layer.name}.png"
                    })
                    image = layer.composite()
                    image.save(f'./lab/{layer.name}.png')
                continue
        else:
            if layer.name.lower() == 'background':
                continue
            layer.visible = True
            list_layers.append({
                "name": f"{layer.name}",
                "url": f"./lab/{layer.name}.png"
            })
            if not os.path.isfile(f'./lab/{layer.name}.png'):
                image = layer.composite()
                image.save(f'./lab/{layer.name}.png')
            layer.visible = False
            layer_parent = layer.parent
            list_parent = find_parent(layer_parent)
            if list_parent in list_layer_parent:
                continue
            list_layer_parent.append(list_parent)
            list_combination = []
            if len(list_parent) > 0:
                set_visible(list_parent, True)
                for item in export_img(list_parent, list_parent[0].parent):
                    list_combination.append(item)
                list_layers.append({
                    "layer_name": layer.parent.name,
                    "combinations": list_combination,
                })

    return list_layers


content = {
    "layers": get_object(psd)
}

print(json.dumps(content))
