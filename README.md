# yards
YOLO Artificial Retro-game Data Synthesizer



## Description

YARDS is a command-line interface that efficiently produces semi-realistic, retro-game sprite detection datasets without manual labeling. Provided with sprites, background images, and a set of parameters, the package uses sprite frequency spaces to create synthetic gameplay images along with their corresponding labels.



## How to install

```
pip install yards
```

OR

```
git clone https://github.com/faimSD/yards.git && cd yards
poetry install && poetry build
pip install --user dist/yards-0.1.1.tar.gz
```



## How to use

### Config File Format & Parameters

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



## TODO

- [ ] Create ReadTheDocs documentation
- [ ] Multiprocessing
- [ ] Basic image rendering and filtering functions (e.g. image blurring and pixellating)
- [ ] Color filtering
- [ ] Support for a wider variety of gameplay styles and genres
- [ ] Text detection functions



## Contributors

- Owners: Jaden Kim & Chanha Kim