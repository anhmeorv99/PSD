from dotenv import dotenv_values
import concurrent
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import find_location_frame
from psd_tools import PSDImage

from log.log_manage import reset_log, get_log, add_log

list_image_object = []

print(dotenv_values())
OUTPUT_DIR = dotenv_values()['OUTPUT_DIR']
INPUT_FILE = dotenv_values()['INPUT_FILE']


def send_with_thread_executor(max_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for image in list_image_object:
            futures.append(
                executor.submit(
                    write_file_png, image[0], image[1], image[2], image[3]
                )
            )


def count_images(layers):
    for layer in layers:
        if layer.kind == 'group':
            if layer.name.lower() == 'background' or 'text -' in layer.name.lower():
                continue
            count_images(layer)
        else:
            add_log('total', 1)


def gen_path(current_path, branch, reverse=True):
    if len(branch) == 1:
        return current_path
    if len(branch) > 1:
        if reverse:
            branch.reverse()

        for index in range(0, len(branch) - 1, 1):
            if os.path.exists(f'{current_path}/{branch[index]}'):
                current_path += f'/{branch[index]}'
                continue
            os.mkdir(os.path.join(current_path, branch[index]))
            current_path += f'/{branch[index]}'
        return current_path


def set_visible(group, mode):
    for layer in group:
        if layer.kind == 'group' and layer.name.lower() != 'background':
            layer.visible = mode
        else:
            if layer.kind == 'group':
                layer.visible = False
            else:
                layer.visible = True


def visible_background(root, mode):
    for layer in root:
        if layer.name.lower() == 'background':
            layer.visible = mode


def set_visible_all(root, mode):
    for layer in root:
        if layer.kind == 'group':
            layer.visible = mode
            set_visible_all(layer, mode)
        else:
            layer.visible = mode


def visible_branch(root, branch):
    if len(branch) == 0:
        return
    for layer in root:
        if layer.name in branch or layer.name.lower() == 'background':
            if layer.name.lower() == 'background' and layer.kind == 'group':
                continue
            layer.visible = True
            if layer.name in branch:

                branch.remove(layer.name)
                if layer.kind == 'group':
                    visible_branch(layer, branch)


def write_file_png(name, path, branch, current_path):
    if not os.path.isfile(f'{current_path}/{name}.png'):
        layer_img = PSDImage.open(path)
        set_visible_all(layer_img, False)
        set_visible(layer_img, False)
        visible_branch(layer_img, branch)
        image = layer_img.composite(ignore_preview=True)
        image.save(f'{current_path}/{name}.png')
        add_log('image', 1)
        print(f'save successfully file: {name}')
        get_log()


def write_file_thumbnail_png(layer, current_path):
    if not os.path.isfile(f'{current_path}/{layer.name}.png'):
        layer.visible = True
        image = layer.composite()
        image.save(f'{current_path}/{layer.name}.png')
        print(f'save successfully file: {layer.name}')
        add_log('image', 1)
        get_log()
        layer.visible = False


def render_img(layers, path):
    list_layers = []
    for layer in layers:
        if layer.kind == 'group':
            if layer.name.lower() == 'background':
                if not os.path.isfile(f'{OUTPUT_DIR}/{layer.name}.png'):
                    layer_img = PSDImage.open(path)
                    visible_background(layer_img, True)
                    image = layer_img.composite(ignore_preview=True)
                    image.save(f'{OUTPUT_DIR}/{layer.name}.png')
                    print(f'save successfully file: {layer.name}')
                list_layers.append({
                    'name': layer.name,

                })
                if not os.path.isfile(f'{OUTPUT_DIR}/thumbnail/{layer.name}.png'):
                    layer.visible = True
                    image = layer.composite()
                    image.save(f'{OUTPUT_DIR}/thumbnail/{layer.name}.png')
                    layer.visible = False
                    print(f'save successfully file: {layer.name}')
                list_layers.append({
                    'name': layer.name,
                    'url': f'{OUTPUT_DIR}/{layer.name}.png',
                    'thumbnail': f'{OUTPUT_DIR}/thumbnail/{layer.name}.png'
                })
                continue
            if 'text -' in layer.name.lower():
                list_layers.append({
                    f'{layer.name}': find_location_frame.find_location_and_text(layer)
                })
                # with open(f'./output_json/property_frame_and_text_{layer.name}.json', 'w') as f:
                #     f.write(find_location_frame.find_location_and_text(layer))
                #     f.close()
                continue
            layer.visible = True
            obj = {
                f'{layer.name}': render_img(layer, path),
            }
            list_layers.append(obj)
        else:
            tmp = layer
            branch = []
            current_path = OUTPUT_DIR
            thumbnail_current_path = f'{OUTPUT_DIR}/thumbnail'
            while tmp.parent is not None:
                branch.append(tmp.name)
                tmp = tmp.parent
            current_path = gen_path(current_path, branch)

            while tmp.parent is not None:
                branch.append(tmp.name)
                tmp = tmp.parent

            thumbnail_current_path = gen_path(
                thumbnail_current_path, branch, reverse=False)
            if layer.name.lower() == 'background' and layer.parent.parent:
                write_file_png(layer.name, path, branch, current_path)
                write_file_thumbnail_png(layer, thumbnail_current_path)
                continue

            list_layers.append({
                'name': f'{layer.name}',
                'url': f'{current_path}/{layer.name}.png',
                'thumbnail': f'{thumbnail_current_path}/{layer.name}.png'
            })
            write_file_thumbnail_png(layer, thumbnail_current_path)

            list_image_object.append([layer.name, path, branch, current_path])
            if len(list_image_object) > 0:
                send_with_thread_executor(5)

    return list_layers


def start(path):
    reset_log()
    global OUTPUT_DIR
    OUTPUT_DIR = "./OUTPUT" + "/" + os.path.basename(path)
    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(f"{OUTPUT_DIR}/thumbnail"):
        os.makedirs(f"{OUTPUT_DIR}/thumbnail")
    psd = PSDImage.open(path)

    set_visible_all(psd, False)
    set_visible(psd, False)
    print('Start render image :')
    count_images(psd)
    count_images(psd)
    content = render_img(psd, path)

    content_output = {
        "Root": content
    }

    print('DONE')
    with open('./output.json', 'w') as f:
        f.write(json.dumps(content_output))
        f.close()


if __name__ == '__main__':
    start(INPUT_FILE)
