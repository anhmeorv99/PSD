import re

from psd_tools import PSDImage
import json

psd = PSDImage.open('/home/anhmeo/Desktop/1000x1000 (1).psd')


def find_location_and_text(root):
    list_frame = []
    list_text = []
    obj = []
    for layer in reversed(list(root.descendants())):
        if layer.kind == 'shape':
            list_frame.append(
                {
                    'name': layer.name,
                    'position': {
                        "X": layer.offset[0],
                        "Y": layer.offset[1]
                    },
                    'size': {
                        'width': layer.size[0],
                        'height': layer.size[1]
                    }

                }
            )
        if layer.kind == 'type':
            data_ft = str(layer.engine_dict)
            len_text = 0
            text = re.findall(r"{'Text': '(.*)'}", data_ft)
            font_size = re.findall(r"'FontSize': (\d+.\d+),", data_ft)
            if len(text) > 0:
                len_text = len(text[0].replace('\\r', ''))

            if len(font_size) > 0:
                font_size = font_size[0]
                list_text.append(
                    {
                        'name': layer.name,
                        'data': {
                            'length_text': len_text,
                            'font_size': float(font_size)
                        }
                    }
                )

    obj = [
        {
            "frame": list_frame
        },
        {
            "text": list_text
        }
    ]
    return obj


