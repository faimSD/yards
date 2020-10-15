# YARDS

YOLO Artificial Retro-game Data Synthesizer



## Description

YARDS is a command-line interface that efficiently produces semi-realistic, retro-game sprite detection datasets without manual labeling. Provided with sprites, background images, and a set of parameters, the package uses sprite frequency spaces to create synthetic gameplay images along with their corresponding labels.

#### Definitions

- **Sprite frequency space** – the discrete probability distribution over the frequency of appearances for that class on a given game-play image.
- **Transparency quadrant** – the quadrants describing the transparent regions of a sprite image.

For a more detailed explanation of how YARDS is implemented, please refer to the corresponding paper: 'http://www.exag.org/papers/EXAG_2020_paper_8.pdf'.



## Dependencies

- Python 3.8.5
- [Poetry](https://python-poetry.org/docs/#installation) (if building/installing from source code)

## Installation

```
pip3 install yards
```

OR

```
git clone https://github.com/faimSD/yards.git && cd yards
poetry install && poetry build
pip3 install --user dist/yards-0.1.2.tar.gz
```



## Usage

```
yards -c config.yaml -v 100
```

#### Command-Line Parameters

- `-c` or `--config` – the path to the YAML file containing configuration parameters for YARDS
- `-v` or `--visualize` – the number of images to visualize (i.e. draw bounding boxes around the sprites in a subset of the output images)

#### Configuration Parameters

- `game_title` – The game's title, which is prepended to each iamge's filename to avoid naming conflicts.
- `num_images` – The total number of images to generate.
- `train_size` – The proportion of total images which should be included in the train set.
- `mix_size` – The proportion of total real images which should be included in the train set. (to be implemented)
- `label_all_classes` – Determines whether all classes should be labeled or if only specific classes should be.
- `labeled_classes` – Determines which classes to label if `label_all_classes` is false. Useful for focusing attention on a single sprite and introducing noise in the form of other sprites or random images.
- `max_sprites_per_class` – The maximum number of sprites per class which can appear in any given image. If set to -1, no cap will be set. Provides a means for limiting noise. Useful primarily when setting `classification_scheme` to random, as it allows for more control of the distribution.
- `transform_sprites` – Another means for introducing noise. If set to true, transforms sprites by rotating a multiple of ninety degrees, mirroring, or scaling to twice their original size. The reason for the set scaling is because pixel art gets distorted by any non-double scaling.
- `clip_sprites` – Determines whether to keep all sprites entirely on screen or to allow some sprite clipping.
- `classification_scheme` – Determines the classification scheme by which to place sprites.
  - `mimic-real` – Analyzes a set of pre-labeled images to approximate the sprite distribution in a dataset and takes as input an array of class numbers, which correspond to the class numbers in the image labels. It then uses the approximated distributions to generate the images.
    - Each class in `classes` when using `mimic-real` should be formatted as `class_label: integer_corresponding_to_class_in_real_images`.
  - `distribution` – Takes a set number of predefined classes such as player, enemy, or item and corresponding sprite frequency spaces for each   class, represented by an array. For instance, player: [0.20, 0.40, 0.40] means that for the player class, zero sprites should appear twenty percent of the time, one sprite should appear forty percent of the time, and two sprites should appear forty percent of the time.
    - Each class in `classes` when using `distribution` should be formatted as `class_label: frequency_space_for_class`.
  - `discrete` – Takes inspiration from games like Street Fighter II where each screen has constant number of sprites, and it takes a constant number of sprites to display on each screenshot.
    - Each class in `classes` when using `discrete` should be formatted as `class_label: constant_number_of_sprites`.
  - `random` – Samples each class with a uniform distribution, given the maximum number of sprites for each class.
    - Each class in `classes` when using `random` should be formatted as `class_label: max_number_of_sprites_for_class`.

#### Config File Format

```yaml
directories:
    maps: '/path/to/background/images/'
    sprites: '/path/to/sprite/images/'
    output: '/path/to/output/directory/'
    real_samples: '/path/to/handlabeled/images/' 

parameters:
    game_title: 'title_of_game'
    num_images: 1000
    train_size: 1.0
    mix_size: 0.0
    label_all_classes: true
    labeled_classes: []
    max_sprites_per_class: -1
    transform_sprites: false
    clip_sprites: true
    classification_scheme: 'mimic-real'

classes:
    player: 0
    enemy: 1
    item: 2
    helpful: 3
    warp: 4
```



## Running the Example

First, install the package from the repository. Then, run the following shell commands. This will generate 50 images based on the parameters set in the example config.yaml file and visualizes all 50 of them.

```
cd example
yards -c config.yaml -v 50
```



## TODO

- [ ] Upload to PyPI
- [ ] Implement mixing of real and synthetic datasets with `mix_size`
- [ ] Create ReadTheDocs documentation
- [ ] Multiprocessing
- [ ] Basic image rendering and filtering functions (e.g. image blurring and pixellating)
- [ ] Color filtering
- [ ] Support for a wider variety of gameplay styles and genres
- [ ] Text detection functions



## Contributors

- Owners: Jaden Kim & Chanha Kim
