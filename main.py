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
                # if not os.path.isfile(f'./lab/{layer.name}.png'):
                #     image = layer.composite()
                #     image.save(f'./lab/{layer.name}.png')
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
            layer.visible = True
            list_layers.append({
                "name": f"{layer.name}",
                "url": f"./lab/{layer.name}.png"
            })
            if not os.path.isfile(f'./lab/{layer.name}.png'):
                image = layer.composite()
                image.save(f'./lab/{layer.name}.png')
    return list_layers


content = {
    "layers": get_object(psd)
}

print(json.dumps(content))
