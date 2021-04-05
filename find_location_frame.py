import re

from psd_tools import PSDImage


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
                        'X': layer.offset[0],
                        'Y': layer.offset[1]
                    },
                    'size': {
                        'width': layer.size[0],
                        'height': layer.size[1]
                    }

                }
            )
        if layer.kind == 'type':
            data_ft = str(layer.engine_dict)
            font_name = re.findall(r"'FontSet': \[{'Name': '(.*)'", str(layer.resource_dict))[0]
            font_name = font_name.split(',')[0].replace('\'', '')
            len_text = 0
            text = re.findall(r"{'Text': '(.*)'}", data_ft)
            font_size = re.findall(r"'FontSize': (\d+.\d+),", data_ft)
            if len(text) > 0:
                len_text = len(text[0].replace('\\r', ''))
            if len(font_size) == 0:
                font_size = re.findall(r"'FontSize': (\d+),", data_ft)
            if len(font_size) > 0:
                font_size = font_size[0]
                list_text.append(
                    {
                        'name': layer.name,
                        'data': {
                            'length_text': len_text,
                            'font_size': float(font_size),
                            'font_name': font_name
                        }
                    }
                )

    obj = [
        {
            'frame': list_frame
        },
        {
            'text': list_text
        }
    ]
    return obj

#
# psd = PSDImage.open('/home/anhmeo/Desktop/dog1 (1).psd')
#
#
# print(find_location_and_text(psd))

