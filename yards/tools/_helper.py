"""
Helper Functions for Main Script

@authors: Jaden Kim & Chanha Kim
"""
import numpy as np
from numpy.random import choice, randint
from PIL import Image, ImageOps
import os, glob, shutil


def _get_sprite_counts(classes, classification_scheme='distribution', sprite_cap=-1):
    """Returns a <class, count> dictionary of sprite counts
        for each class to be pasted in the new image."""
    sprite_counts = {}
    # first handle the raw counts
    if classification_scheme == 'random':
        for c in classes:
            sprite_counts[c] = choice([i for i in range(classes[c]+1)])
            if sprite_counts[c] > sprite_cap and sprite_cap != -1:
                sprite_counts[c] = sprite_cap
    elif classification_scheme == 'distribution':
        for c in classes:
            sprite_counts[c] = choice([i for i in range(len(classes[c]))], p=classes[c])
            if sprite_counts[c] > sprite_cap and sprite_cap != -1:
                sprite_counts[c] = sprite_cap
    elif classification_scheme == 'discrete':
        class_list = list(classes.keys())
        num_players = classes[class_list[0]]
        for i in range(num_players):
            c = choice(class_list)
            if c in list(sprite_counts.keys()):
                sprite_counts[c] += 1
            else:
                sprite_counts[c] = 1
    else:
        print('Invalid classification scheme.')

    return sprite_counts


def _get_sprite_path(class_path_cache):
    """Returns the file path of a random sprite from the sprite directory."""
    return choice(class_path_cache)


def gather_sprite_paths(sprite_path_cache, class_info, classification_scheme, sprite_cap):
    """Returns a <path, class number> dictionary of the file paths of all the sprites to be pasted on an image."""
    classes, class_numbers = class_info
    sprite_paths = {}
    sprite_counts = _get_sprite_counts(classes, classification_scheme, sprite_cap)
    for c in sprite_counts:
        for i in range(sprite_counts[c]):
            sprite_paths[_get_sprite_path(sprite_path_cache[c])] = class_numbers[c]

    return sprite_paths


def transform_sprite(sprite, map_dim):
    transformed_sprite = sprite
    operations = {"mirror":bool(choice(2)), "rotate":choice([0, Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270]), "resize":bool(choice(2))}

    if operations["mirror"]:
        transformed_sprite = transformed_sprite.transpose(Image.FLIP_LEFT_RIGHT)

    if operations["rotate"] != 0:
        transformed_sprite = transformed_sprite.transpose(operations["rotate"])

    if operations["resize"] and (transformed_sprite.size[0] < int(map_dim[0]/2) and transformed_sprite.size[1] < int(map_dim[1]/2)):
        transformed_sprite = transformed_sprite.resize((transformed_sprite.size[0]*2, transformed_sprite.size[1]*2), Image.NEAREST)

    return transformed_sprite


def get_sprite_pos(map_dim, sprite_dim, clip_sprites):
    """Returns a sprite position for a given map and sprite."""
    map_w, map_h = map_dim
    sprite_w, sprite_h = sprite_dim

    if clip_sprites:
        x_pos = randint(-sprite_w, map_w)
        y_pos = randint(-sprite_h, map_h)
    else:
        x_pos = randint(0, map_w - sprite_w)
        y_pos = randint(0, map_h - sprite_h)

    sprite_clipped = True if ((x_pos < 0 or x_pos >= map_w - sprite_w) or (y_pos < 0 or y_pos >= map_h - sprite_h)) else False

    return (x_pos, y_pos), sprite_clipped


def _get_transparencies(sprite):
    """Returns the 'transparent' quadrants for an image."""
    # get a binarray array from the image
    bin_array = (np.asarray(sprite.convert('RGBA').getchannel('A')) > 128).astype(int)

    # find indices
    indices = np.argwhere(bin_array == 1)
    min_row, min_col = np.amin(indices, axis=0 )
    max_row, max_col = np.amax(indices, axis=0)

    # find row/col x min/max values
    min_row_cols = indices[np.squeeze(np.argwhere(indices[:, 0] == min_row)), :].reshape(-1, 2)
    min_col_rows = indices[np.squeeze(np.argwhere(indices[:, 1] == min_col)), :].reshape(-1, 2)
    max_row_cols = indices[np.squeeze(np.argwhere(indices[:, 0] == max_row)), :].reshape(-1, 2)
    max_col_rows = indices[np.squeeze(np.argwhere(indices[:, 1] == max_col)), :].reshape(-1, 2)

    # (x,y) positions of the quadrants
    ul = {'x':np.min(min_row_cols[:, 1]), 'y':np.min(min_col_rows[:, 0])}
    ur = {'x':np.max(min_row_cols[:, 1]), 'y':np.min(max_col_rows[:, 0])}
    bl = {'x':np.min(max_row_cols[:, 1]), 'y':np.max(min_col_rows[:, 0])}
    br = {'x':np.max(max_row_cols[:, 1]), 'y':np.max(max_col_rows[:, 0])}

    return (ul, ur, bl, br)


def edge_handler(map_dim, sprite_dim, sprite_pos, sprite):
    """Handles edge cases"""
    # load parameters
    (map_w, map_h), (sprite_w, sprite_h), (x_pos, y_pos) = map_dim, sprite_dim, sprite_pos
    ul, ur, bl, br = _get_transparencies(sprite)

    # left edge
    if x_pos < 0:
        if np.max([sprite_w - ur['x'], sprite_w - br['x']]) >= (x_pos + sprite_w):
            crop_x = int(np.average([ur['x'], br['x'], ul['x'], bl['x']]))
        else:
            crop_x = abs(x_pos)
        sprite = sprite.crop((crop_x, 0, sprite_w, sprite_h))
        sprite_w = sprite.size[0]
        x_pos = 0
    # right edge
    elif x_pos >= map_w - sprite_w:
        if np.max([ul['x'], bl['x']]) >= (map_w - x_pos):
            crop_x = int(np.average([ul['x'], bl['x'], ur['x'], br['x']]))
        else:
            crop_x = map_w - x_pos
        sprite = sprite.crop((0, 0, crop_x, sprite_h))
        sprite_w = sprite.size[0]
        x_pos = map_w - sprite_w

    # top edge
    if y_pos < 0:
        if np.max([sprite_h - bl['y'], sprite_h - br['y']]) >= (y_pos + sprite_h):
            crop_y = int(np.average([bl['y'], br['y'], ul['y'], ur['y']]))
        else:
            crop_y = abs(y_pos)
        sprite = sprite.crop((0, crop_y, sprite_w, sprite_h))
        sprite_h = sprite.size[1]
        y_pos = 0
    # bottom edge
    elif y_pos >= map_h - sprite_h:
        if np.max([ul['y'], ur['y']]) >= (map_h - y_pos):
            crop_y = int(np.average([ul['y'], ur['y'], bl['y'], br['y']]))
        else:
            crop_y = map_h - y_pos
        sprite = sprite.crop((0, 0, sprite_w, crop_y))
        sprite_h = sprite.size[1]
        y_pos = map_h - sprite_h

    return sprite, (sprite_w, sprite_h), (x_pos, y_pos)


def get_bbox(map_dim, sprite_dim, sprite_pos):
    """Returns the bounding box for a sprite that was pasted at position pos"""
    (map_w, map_h), (sprite_w, sprite_h), (x_pos, y_pos) = map_dim, sprite_dim, sprite_pos
    rel_x = (x_pos + sprite_w / 2) / map_w
    rel_y = (y_pos + sprite_h / 2) / map_h
    rel_w = sprite_w / map_w
    rel_h = sprite_h / map_h

    return (rel_x, rel_y, rel_w, rel_h)


def draw_sprite_to_background(sprite, background, pos):
    """Draws the sprite to background and returns the background."""
    background.alpha_composite(sprite, dest=pos)

    return background
