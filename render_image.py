import concurrent
import json
import os
from concurrent.futures import ThreadPoolExecutor
import find_location_frame
from psd_tools import PSDImage

list_image_object = []
list_image_object_thumbnail = []


def send_with_thread_executor(max_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for image in list_image_object:
            futures.append(
                executor.submit(
                    write_file_png, image[0], image[1], image[2], image[3]
                )
            )


def send_with_thread_executor_thumbnail(max_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for image in list_image_object:
            futures.append(
                executor.submit(
                    write_file_thumbnail_png, image[0], image[1]
                )
            )


def gen_path(current_path, branch):
    if len(branch) == 1:
        return current_path
    if len(branch) > 1:

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
        print(f'save successfully file: {name}')


def write_file_thumbnail_png(layer, current_path):
    if not os.path.isfile(f'{current_path}/{layer.name}.png'):
        layer.visible = True
        image = layer.composite()
        image.save(f'{current_path}/{layer.name}.png')
        print(f'save successfully file: {layer.name}')
        layer.visible = False


def render_img(layers, path):
    list_layers = []
    for layer in layers:
        if layer.kind == 'group':
            if layer.name.lower() == 'background':
                if not os.path.isfile(f'./lab1/{layer.name}.png'):
                    layer_img = PSDImage.open(path)
                    visible_background(layer_img, True)
                    image = layer_img.composite(ignore_preview=True)
                    image.save(f'./lab1/{layer.name}.png')
                    print(f'save successfully file: {layer.name}')
                list_layers.append({
                    'name': layer.name,
                    'url': f'./lab1/{layer.name}.png'
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
            current_path = './lab1'
            while tmp.parent is not None:
                branch.append(tmp.name)
                tmp = tmp.parent
            current_path = gen_path(current_path, branch)

            if layer.name.lower() == 'background' and layer.parent.parent:
                write_file_png(layer.name, path, branch, current_path)
                continue

            list_layers.append({
                'name': f'{layer.name}',
                'url': f'{current_path}/{layer.name}.png'
            })

            list_image_object.append([layer.name, path, branch, current_path])
            if len(list_image_object) > 10:
                send_with_thread_executor(5)
                list_image_object.clear()

    return list_layers


def render_img_thumbnail(layers, path):
    list_layers = []
    for layer in layers:
        if layer.kind == 'group':
            if layer.name.lower() == 'background':
                if not os.path.isfile(f'./lab1/thumbnail/{layer.name}.png'):
                    layer.visible = True
                    image = layer.composite()
                    image.save(f'./lab1/thumbnail/{layer.name}.png')
                    layer.visible = False
                    print(f'save successfully file: {layer.name}')
                list_layers.append({
                    'name': layer.name,
                    'url': f'./lab1/thumbnail/{layer.name}.png'
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
                f'{layer.name}': render_img_thumbnail(layer, path),
            }
            list_layers.append(obj)
        else:

            tmp = layer
            branch = []
            current_path = './lab1/thumbnail'
            while tmp.parent is not None:
                branch.append(tmp.name)
                tmp = tmp.parent
            current_path = gen_path(current_path, branch)

            if layer.name.lower() == 'background' and layer.parent.parent:
                write_file_thumbnail_png(layer, current_path)
                continue

            list_layers.append({
                'name': f'{layer.name}',
                'url': f'{current_path}/{layer.name}.png'
            })

            list_image_object_thumbnail.append([layer, current_path])
            if len(list_image_object) > 10:
                send_with_thread_executor_thumbnail(5)
                list_image_object_thumbnail.clear()

    return list_layers


def start(path):
    psd = PSDImage.open(path)
    set_visible_all(psd, False)
    set_visible(psd, False)

    content = {
        "Root": render_img(psd, path),
    }

    psd = PSDImage.open(path)

    content_thumbnail = {
        "thumbnail": render_img_thumbnail(psd, path)
    }

    content_output = {
        'Root': content['Root'],
        'thumbnail': content_thumbnail['thumbnail']
    }

    with open('./output.json', 'w') as f:
        f.write(json.dumps(content_output))
        f.close()


if __name__ == '__main__':
    start('/home/anhmeo/Desktop/Once upon a time there was a girl who loves dogs. The end..psd')
