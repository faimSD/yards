"""
"validator modules that validates packages"
@author: Jaden Kim & Chanha Kim
@date  : 7/20/2020
"""

def validate_config(config):
    '''Returns true if the config is valid'''
    correct_keys = {'directories', 'parameters', 'classes'}
    config_keys = set(config.keys())

    return (correct_keys - config_keys) == set()


def validate_directories(paths):
    '''Returns true if the directory paths are valid'''
    from os.path import isdir
    from os import mkdir
    
    # ensure that the keys are correct
    correct_keys = {'maps', 'sprites', 'output'}    # real data is optional
    dirs_keys = set(paths.keys())
    are_keys_correct = min([key in dirs_keys for key in correct_keys])
    # ensure that the directories exist
    dirs_paths = list(paths.values())
    if not isdir(paths['output']):
        mkdir(paths['output'])

    are_paths_correct = min([isdir(path) for path in dirs_paths])

    return are_keys_correct and are_paths_correct


def validate_parameters(parameters):
    '''Returns true if the parameters are valid'''
    correct_keys = {'game_title', 'num_images', 'train_size', 'mix_size',
                   'label_all_classes', 'labeled_classes', 'max_sprites_per_class',
                   'transform_sprites', 'clip_sprites', 'classification_scheme'}
    params_keys = set(parameters.keys())
    are_keys_correct = (correct_keys - params_keys) == set()

    def checklist(ls):
        ret = min([isinstance(el, str) for el in ls])
        return ret

    are_values_correct = True
    if not isinstance(parameters['game_title'], str):
        are_values_correct = False
    if not isinstance(parameters['num_images'], int) or parameters['num_images'] < 0:
        are_values_correct = False
    if not isinstance(parameters['train_size'], float) or parameters['train_size'] < 0.0 or parameters['train_size'] > 1.0:
        are_values_correct = False
    if not isinstance(parameters['mix_size'], float) or parameters['mix_size'] < 0.0 or parameters['mix_size'] > 1.0:
        are_values_correct = False
    if not isinstance(parameters['label_all_classes'], bool):
        are_values_correct = False
    if not parameters['label_all_classes'] and not checklist(parameters['labeled_classes']):
        are_values_correct = False
    if not isinstance(parameters['max_sprites_per_class'], int):
        are_values_correct = False
    if not isinstance(parameters['transform_sprites'], bool):
        are_values_correct = False
    if not isinstance(parameters['clip_sprites'], bool):
        are_values_correct = False
    if not (parameters['classification_scheme'] == 'distribution' or parameters['classification_scheme'] == 'discrete' or parameters['classification_scheme'] == 'random' or parameters['classification_scheme'] == 'mimic-real'):
        are_values_correct = False

    return are_keys_correct and are_values_correct


def validate_classes(classes, classification_scheme):
    '''Returns true if the classes are valid'''
    classes_keys = list(classes.keys())
    are_keys_correct = min([type(key) == str for key in classes_keys])
    classes_values = list(classes.values())
    if classification_scheme == 'distribution':
        are_values_correct = min([type(value) == list for value in classes_values]) and min([all(isinstance(sub_value, float) for sub_value in value) for value in classes_values])
    elif classification_scheme == 'random':
        are_values_correct = min([type(value) == int for value in classes_values])
    elif classification_scheme == 'discrete':
        are_values_correct = (min(classes_values) == max(classes_values)) and min([type(value) == int for value in classes_values])
    elif classification_scheme == 'mimic-real':
        are_values_correct = min([type(value) == int for value in classes_values])
    else:
        are_values_correct = False

    return are_keys_correct and are_values_correct

