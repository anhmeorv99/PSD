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
                if not os.path.isfile(f'./lab/{layer.name}.png'):
                    image = layers.composite(ignore_preview=True)
                    image.save(f'./lab/{layer.name}.png')

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
            layer.visible = True
            if not os.path.isfile(f'./lab/{layer.parent.name}_{layer.name}.png'):
                image = layer.composite()
                image.save(f'./lab/{layer.parent.name}_{layer.name}.png')
    return list_layers


content = {
    "Root": get_object(psd)
}

with open('./output.json', 'w') as f:
    f.write(json.dumps(content))
    f.close()