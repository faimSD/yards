"""
yards is a class version of the original yards program.

Script to generate pseudo-random artificial data for games.
Uses distribution curves to place sprites and create bounding boxes.

@authors: Jaden Kim & Chanha Kim
@date   : 7/20/2020
"""

# modules
import os
import glob
import shutil
import yaml
import tqdm
from PIL import Image, ImageDraw
from numpy.random import choice
from numpy import unique
from .tools import _helper # import the helper module correctly
from .tools import _validator

class yards():

    def __init__(self, config_path = None):
        '''Initializing a yards object'''
        if config_path != None:
            self.load_config_from_file(config_path)
        else:
            self._config_path = None
            self._config = None
            self._dirs = None
            self._params = None
            self._classes = None
            self._class_numbers = None
            self._output_dirs = None
            self._map_path_cache = None
            self._sprite_path_cache = None

    # Setting configurations and getters/setters

    def _create_output_dirs(self):
        '''Helper that creates output directories'''
        if os.path.isdir(self._dirs['output']):
            shutil.rmtree(self._dirs['output'])
            os.mkdir(self._dirs['output'])

        os.mkdir(self._dirs['output'] +'images/')
        os.mkdir(self._dirs['output'] +'labels/')

        self._output_dirs = {
            'images_train': self._dirs['output'] + 'images/train/',
            'images_val': self._dirs['output'] + 'images/val/',
            'labels_train': self._dirs['output'] + 'labels/train/',
            'labels_val': self._dirs['output'] + 'labels/val/'
        }
        for out in self._output_dirs.values(): os.mkdir(out)

    def _parse_params(self):
        '''Parses all_params dictionary into separate dictionaries'''
        self.set_directories(self._config['directories'])
        self.set_parameters(self._config['parameters'])
        self.set_classes(self._config['classes'])

    def _cache_paths(self):
        '''Caches all the params into separate dictionaries'''
        self._map_path_cache = glob.glob(self._dirs['maps']+'*.png')
        self._sprite_path_cache = {}
        for c in self._classes:
            self._sprite_path_cache[c] = glob.glob(self._dirs['sprites']+'{}/*.png'.format(c))

    def load_config_from_file(self, config_path):
        '''Loads configuration from a file'''
        self._config_path = config_path
        with open(r'{}'.format(self._config_path)) as file:
            self._config = yaml.load(file, Loader=yaml.FullLoader)
        self._parse_params()
        self._create_output_dirs()

    def set_config(self, config):
        '''Sets a configuration from a dictionary'''
        if _validator.validate_config(config):
            self._config = config
            self._parse_params()
            self._create_output_dirs()
        else:
            print('Configuration is not valid')

    def get_config(self):
        '''Returns the configuration'''
        return self._config

    def set_directories(self, paths):
        '''Sets the directories'''
        if _validator.validate_directories(paths):
            self._dirs = paths
        else:
            print('Directories are not valid')

    def get_directories(self):
        '''Returns the directories'''
        return self._dirs

    def set_parameters(self, parameters):
        '''Sets the parameters'''
        if _validator.validate_parameters(parameters):
            self._params = parameters
            self._params['num_train'] = self._params['train_size'] * self._params['num_images']
        else:
            print('Parameters are not valid')

    def get_parameters(self):
        '''Returns the parameters'''
        return self._parameters

    def set_classes(self, classes):
        '''Sets the classes'''
        if _validator.validate_classes(classes, self._params['classification_scheme']):
            if self._params['classification_scheme'] == 'mimic-real':
                self.approximate_frequency_spaces_from_real_data(classes)
            else:
                self._classes = classes
            if self._params != None:
                if self._params['label_all_classes']:
                    self._class_numbers = {c: n for (c, n) in list(zip(self._classes, [i for i in range(len(self._classes))]))}
                else:
                    self._class_numbers = {c: n for (c, n) in list(zip(self._params['labeled_classes'], [i for i in range(len(self._params['labeled_classes']))]))}
                    for c in list(set(self._classes.keys()) - set(self._params['labeled_classes'])):
                        self._class_numbers[c] = -1
            else:
                print("You haven't loaded the parameters yet. If you're labeling select classes, then load parameters first before loading classes.")

            if self._dirs != None:
                self._cache_paths()
            else:
                print("You haven't loaded the directory paths yet. Load the directories first before loading the classes.")

        else:
            print('Classes are not valid.')

    def get_classes(self):
        '''Returns the classes'''
        return self._classes

    def approximate_frequency_spaces_from_real_data(self, class_ids):
        """Approximates frequency spaces by analyzing real samples."""
        # set up some local variables
        real_samples_labels_dir = self._dirs['real_samples'] + "labels/"
        real_samples_labels_paths = glob.glob(real_samples_labels_dir + "*.txt")
        num_samples = len(real_samples_labels_paths)
        classes = {num: [] for num in class_ids.values()}
        print("Approximating frequency spaces from {num} samples...".format(num = num_samples))
        # read in class info
        for path in tqdm.tqdm(real_samples_labels_paths):
            for c in classes: classes[c].append(0)
            with open(path, "r") as file:
                for line in file:
                    class_id = int([float(i) for i in line.split()][0])
                    if class_id in classes:
                        classes[class_id][-1] += 1

        # analyze frequencies
        for c in class_ids:
            class_id = class_ids[c]
            classes[class_id] = list(unique(classes[class_id], return_counts = True))
            total = sum(classes[class_id][1])
            classes[class_id][1] = [num / total for num in classes[class_id][1]]
            classes[class_id][0] = list(classes[class_id][0])
            classes[c] = classes[class_id]
            del classes[class_id]
            print(c + ":\t\t", classes[c])

        print("Finished approximating frequency spaces.")

        self._classes = classes

    def _create_image(self, count, output_dir):
        '''Creates an image'''
        background_image = Image.open(choice(self._map_path_cache))
        new_image = background_image.copy().convert('RGBA')
        map_dim = new_image.size
        background_image.close()

        # get the sprite paths
        sprite_paths = _helper.gather_sprite_paths(self._sprite_path_cache, (self._classes, self._class_numbers), self._params['classification_scheme'], self._params['max_sprites_per_class'])
        bbox_cache = []

        # add the sprites to the new image, saving the bounding box information in a cache
        for sprite_path in sprite_paths:
            sprite = Image.open(sprite_path).convert('RGBA')
            if self._params['transform_sprites']:
                sprite = _helper.transform_sprite(sprite, map_dim)
            sprite_dim = sprite.size

            sprite_pos, is_sprite_clipped = _helper.get_sprite_pos(map_dim, sprite_dim, self._params['clip_sprites'])
            if is_sprite_clipped:
                sprite, sprite_dim, sprite_pos = _helper.edge_handler(map_dim, sprite_dim, sprite_pos, sprite)

            new_image = _helper.draw_sprite_to_background(sprite, new_image, sprite_pos)
            sprite.close()
            bbox = _helper.get_bbox(map_dim, sprite_dim, sprite_pos)
            if sprite_paths[sprite_path] != -1:
                bbox_cache.append((sprite_paths[sprite_path], *bbox))

        # save and close the image
        new_image.save('{}{}-{}.png'.format(output_dir, self._params['game_title'], count))
        new_image.close()

        # return the cache
        return bbox_cache

    def _create_annotation(self, bbox_cache, count, output_dir):
        """Creates a dataset label at the desired directory."""
        with open('{}{}-{}.txt'.format(output_dir, self._params['game_title'], count), 'w') as file:
            for bbox in bbox_cache:
                file.write('{} {} {} {} {}\n'.format(*bbox))

    def _create_image_and_annotate(self, count):
        bbox_cache = self._create_image(count, self._output_dirs['images_train'] if count <= self._params['num_train'] else self._output_dirs['images_val'])
        self._create_annotation(bbox_cache, count, self._output_dirs['labels_train'] if count <= self._params['num_train'] else self._output_dirs['labels_val'])
        return None

    def loop(self):
        """Creates the images."""
        print('Writing {} images...'.format(self._params['num_images']))
        for count in tqdm.tqdm(range(1, 1+self._params['num_images'])):
            bbox_cache = self._create_image(count, self._output_dirs['images_train'] if count <= self._params['num_train'] else self._output_dirs['images_val'])
            self._create_annotation(bbox_cache, count, self._output_dirs['labels_train'] if count <= self._params['num_train'] else self._output_dirs['labels_val'])
        print('Finished writing {} images.'.format(self._params['num_images']))

    def visualize(self, directory='train', num_visualize=50):
        """Draws bounding boxes around the images."""
        if directory == 'train' or directory == 'val':
            if directory == 'train':
                image_dir = self._output_dirs['images_train']
                label_dir = self._output_dirs['labels_train']
            elif directory == 'label':
                image_dir = directory['images']
                label_dir = directory['labels']
            examples_dir = self._dirs['output']+'examples/'
            
        else:
            if directory[-1] != '/':
                directory += '/'
            image_dir = directory + 'images/'
            label_dir = directory + 'labels/'
            examples_dir = directory+'examples/'

        if os.path.isdir(examples_dir):
            shutil.rmtree(examples_dir)
        os.mkdir(examples_dir)

        image_paths = glob.glob(image_dir+'*.png')[0:num_visualize]

        print('Visualizing {} example images...'.format(num_visualize))
        colors = {}
        for i in tqdm.tqdm(range(len(image_paths))):
            bboxes = []
            image_name = os.path.splitext(os.path.split(image_paths[i])[1])[0]
            with open(label_dir+'{}.txt'.format(image_name)) as file:
                for line in file:
                    line = [float(i) for i in line.split()]
                    bboxes.append(line)
            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)
            for bbox in bboxes:
                c = int(bbox[0])
                x1 = int(image.size[0]*bbox[1] - image.size[0]*bbox[3]/2)
                y1 = int(image.size[1]*bbox[2] - image.size[1]*bbox[4]/2)
                x2 = int(image.size[0]*bbox[1] + image.size[0]*bbox[3]/2)
                y2 = int(image.size[1]*bbox[2] + image.size[1]*bbox[4]/2)
                if c not in list(colors.keys()):
                    colors[c] = tuple(choice(range(256), size=3))
                draw.rectangle([x1, y1, x2, y2], fill=None, outline=colors[c])

            image.save(examples_dir+'annotated-{}.png'.format(image_name))
            image.close()
        print('Finished visualizing {} example images.'.format(num_visualize))


