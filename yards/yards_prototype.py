"""
yards.py

Script to generate pseudo-random artificial data for games.
Uses distribution curves to place sprites and create bounding boxes.

@authors: Jaden Kim & Chanha Kim
"""

# modules
import os
import glob
import shutil
import argparse
import yaml
from PIL import Image
from numpy.random import choice
from .tools.helper import * # import the helper module correctly

# load config parameters
def load_config(config_file):
    """Returns a configuration file as a dictionary"""
    with open(r'{}'.format(config_file)) as file:
        all_params = yaml.load(file, Loader=yaml.FullLoader)

    return all_params


# parse all_params
def parse_params(all_params):
    """Parses all_params dictionary into separate dictionaries"""
    directories = all_params.pop('directories')
    params = all_params.pop('parameters')
    classes = all_params.pop('classes')
    class_numbers = {c: n for (c, n) in list(zip(classes, [i for i in range(len(classes))]))}
    if not params['label_all_classes']:
        for c in classes:
            if c not in params['labeled_classes']:
                class_numbers[c] = -1

    return directories, params, (classes, class_numbers)


# create output directories
def _create_output_dirs(output_dir):
    """Creates the output directories for dataset if they don't exist"""
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)
    parent_out_dir = (output_dir+out for out in ['images/', 'labels/'])
    child_out_dir = (output_dir+out for out in ['images/train/', 'images/val/', 'labels/train/', 'labels/val/'])
    for out in parent_out_dir: os.mkdir(out)
    for out in child_out_dir: os.mkdir(out)

    return child_out_dir


# create an image
def _create_image(dirs, class_info, params, count, output_dir):
    """Creates a dataset image at the desired directory. Returns bbox cache for creating annotations."""
    # open the map and create a copy of it as a new image
    background_image = Image.open(choice(glob.glob(dirs['maps']+'.png')))
    new_image = background_image.copy().convert('RGBA')
    map_dim = new_image.size
    background_image.close()

    # get the sprite paths
    sprite_paths = _gather_sprite_paths(dirs['sprites'], class_info, params['random_distribution'], params['maximum_sprites_per_image'])
    bbox_cache = []

    # add the sprites to the new image, saving the bounding box information in a cache
    for sprite_path in sprite_paths:
        sprite = Image.open(sprite_path).convert('RGBA')
        if params['transform_sprites']:
            sprite = _transform_sprite(sprite)

        sprite_pos, sprite_clipped = _get_sprite_pos(map_dim, sprite.size, params['clip_sprites'])
        if sprite_clipped:
            sprite, sprite_dim, sprite_pos = _edge_handler(map_dim, sprite.size, sprite_pos, sprite)

        new_image = _draw_sprite_to_background(sprite, new_image, sprite_pos)
        sprite.close()
        bbox = _get_bbox(map_dim, sprite_dim, sprite_pos)
        if sprite_paths[sprite_path] != -1:
            bbox_cache.append((sprite_paths[sprite_path], *bbox))

    # save and close the image
    new_image.save('{}{}.png'.format(output_dir, count))
    new_image.close()

    # return the cache
    return bbox_cache


# create an annotation
def _create_annotation(bbox_cache, count, output_dir):
    """Creates a dataset label at the desired directory."""
    with open('{}{}.txt'.format(output_dir, count)) as file:
        for bbox in bbox_cache:
            file.write('{} {} {} {} {}\n'.format(*bbox))


# run a loop
def loop(all_params):
    """Creates the desired number of images and labels for the dataset."""
    # load parameters
    dirs, params, class_info = all_params
    train_size = int(params['num_images']*params['train_size'])
    image_train_dir, image_val_dir, label_train_dir, label_val_dir = _create_output_dirs(directories['output_dir'])

    # run loop
    print('Writing {} images.'.format(params['num_images']))
    for count in progressbar.progressbar(range(1, num_images+1)):
        bbox_cache = _create_image(dirs, class_info, params, count, image_train_dir if count <= train_size else image_val_dir)
        _create_annotation(bbox_cache, count, label_train_dir if count <= train_size else label_val_dir)
    print('Finished writing {} images.'.format(params['num_images']))

    
# visualize data
def visualize(output_dir, num_visualize):
    """Visualizes some or all of the images."""
    examples_path = output_dir + 'examples/'
    if os.path.isdir(examples_path):
        shutil.rmtree(examples_path)
        os.mkdir(examples_path)

    for image_path in glob.glob(output_dir+'.png'):
