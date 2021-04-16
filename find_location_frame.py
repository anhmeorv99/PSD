import json
import re

from psd_tools import PSDImage


def find_location_and_text(root):
    text_list = []
    for layer in reversed(list(root.descendants())):
        if layer.kind == 'type':

            text_data = str(layer.engine_dict)
            # print(text_data)
            font_name = re.findall(
                r"'FontSet': \[{'Name': '(.*)'", str(layer.resource_dict))[0]
            font_name = font_name.split(',')[0].replace('\'', '')

            text_content = re.findall(
                r"{'Text': '(.*)'}", text_data)[0].replace('\\r', '')
            text_length = len(text_content)

            text_color = re.findall(
                r"'FillColor': {'Type': 1, 'Values': \[(.+?)]}", text_data)[0].split(', ')
            text_color = rgb_hex(text_color)

            font_size = re.findall(r"'FontSize': (\d+.\d+),", text_data)
            if len(font_size) == 0:
                font_size = re.findall(r"'FontSize': (\d+),", text_data)
            if len(font_size) > 0:
                font_size = font_size[0]
                text_list.append(
                    {
                        'name': layer.name,
                        'position': {
                            'X': layer.offset[0],
                            'Y': layer.offset[1]
                        },
                        'size': {
                            'width': layer.size[0],
                            'height': layer.size[1]
                        },
                        'data': {
                            'text_content': text_content,
                            'text_length': text_length,
                            'font_size': float(font_size),
                            'font_name': font_name,
                            'text_color': text_color
                        }

                    }
                )

    return text_list


def rgb_hex(color):  # https://stackoverflow.com/a/48288173/7182363
    color = [255*float(x) for x in color[1:4]]
    return '#' + ''.join(['{:02X}'.format(int(round(x))) for x in color])
