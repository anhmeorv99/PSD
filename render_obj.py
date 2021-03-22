import json
import os

from psd_tools import PSDImage

psd = PSDImage.open('/home/anhmeo/Desktop/Once upon a time there was a girl who loves dogs. The end..psd')


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
                list_layers.append({
                    "name": layer.name,
                    "url": f"./lab/{layer.name}.png"
                })
        else:
            if layer.name.lower() == 'background' and layer.parent.parent is None:
                continue
            list_layers.append({
                "name": f"{layer.name}",
                "url": f"./lab/{layer.name}.png"
            })
    return list_layers


content = {
    "layers": get_object(psd)
}

print(json.dumps(content))