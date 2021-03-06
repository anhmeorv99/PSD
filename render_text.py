import re

from psd_tools import PSDImage


def find_text(root, text):
    for layer in reversed(list(root.descendants())):
        if layer.name == text:
            for child in reversed(list(layer.descendants())):
                if child.kind == 'type':

                    data_ft = str(child.engine_dict)
                    font_name = re.findall(r"'FontSet': \[{'Name': '(.*)'", str(child.resource_dict))[0]
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
                        return {
                            'name': child.name,
                            'position': {
                                'X': child.offset[0],
                                'Y': child.offset[1]
                            },
                            'size': {
                                'width': child.size[0],
                                'height': child.size[1]
                            },
                            'data': {
                                'length_text': len_text,
                                'font_size': float(font_size),
                                'font_name': font_name
                            }

                        }

    return None


# psd = PSDImage.open('/home/anhmeo/Desktop/dog1 (1).psd')
#
# print(find_text(psd, "Text - 2 Enter Your Dog's name"))
