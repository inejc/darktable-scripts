import os
import re
import shutil
import xml.etree.ElementTree as XmlElementTree

import fire


def copy_rated_images(from_path, to_path):
    num_images_copied = 0

    for dir_path, _, file_names in os.walk(from_path):
        for file_name in file_names:
            if file_name.endswith('.xmp'):
                num_images_copied += int(handle_sidecar_file(
                    from_path,
                    to_path,
                    os.path.join(dir_path, file_name),
                ))

    print(f"Copied {num_images_copied} images.")


def handle_sidecar_file(from_path, to_path, sidecar_file_path):
    if read_rating_from_sidecar_file(sidecar_file_path) == 0:
        return False

    # Compute the needed paths.
    source_dir, _ = os.path.split(sidecar_file_path)
    common_prefix = os.path.commonprefix([from_path, sidecar_file_path])
    relative_path = os.path.relpath(sidecar_file_path, common_prefix)
    destination_path = os.path.join(to_path, relative_path)
    destination_dir, sidecar_file_name = os.path.split(destination_path)
    image_file_name = re.sub(r'\.xmp$', '', sidecar_file_name)

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Copy the sidecar file.
    shutil.copy(
        os.path.join(source_dir, sidecar_file_name),
        os.path.join(destination_dir, sidecar_file_name),
    )

    # Copy the image. Some images might not exist because there could be
    # more than one sidecar file per image.
    try:
        shutil.copy(
            os.path.join(source_dir, image_file_name),
            os.path.join(destination_dir, image_file_name),
        )
        return True
    except FileNotFoundError:
        print(f"Skipping image {image_file_name} because it does not exist.")

    return False


def read_rating_from_sidecar_file(file_path):
    root = XmlElementTree.parse(file_path).getroot()
    rating = root \
        .find('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF') \
        .find('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description') \
        .get('{http://ns.adobe.com/xap/1.0/}Rating')
    return int(rating)


if __name__ == '__main__':
    fire.Fire(copy_rated_images)
