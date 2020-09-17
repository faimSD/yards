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
    # ensure that the keys are correct
    correct_keys = {'maps', 'sprites', 'real_samples', 'output'}
    dirs_keys = set(paths.keys())
    are_keys_correct = (correct_keys - dirs_keys) == set()
    # ensure that the directories exist
    dirs_paths = list(paths.values())
    are_paths_correct = min([isdir(path) for path in dirs_paths])

    return are_keys_correct and are_paths_correct


def validate_parameters(parameters):
    '''Returns true if the parameters are valid'''
    is_valid = True
    good_params = ['game_title', 'num_images', 'train_size', 'real_size',
                   'label_all_classes', 'labeled_classes', 'max_sprites_per_class',
                   'transform_sprites', 'clip_sprites', 'classification_scheme']

    def diff(first, second):
        return set(first) - set(second)

    def checklist(lst):
        return bool(lst) and all(isinstance(i, basestring) for i in lst)

    if diff(good_params, list(parameters.keys())) != set():
        is_valid = False
    if !isinstance(parameters['game_title'], basestring):
        is_valid = False
    if !isinstance(parameters['num_images'], int) or parameters['num_images'] < 0:
        is_valid = False
    if !isinstance(parameters['train_size'], float) or parameters['train_size'] < 0.0
    or parameters['train_size'] > 1.0:
        is_valid = False
    if !isinstance(parameters['real_size'], float) or parameters['real_size'] < 0.0
    or parameters['real_size'] > 1.0:
        is_valid = False
    if !isinstance(parameters['label_all_classes'], bool):
        is_valid = False
    if !checklist(parameters[labeled_classes]):
        is_valid = False
    if !isinstance(parameters['max_sprites_per_class'], int) or parameters['label_all_classes'] < -1:
        is_valid = False
    if !isinstance(parameters['transform_sprites'], bool):
        is_valid = False
    if !isinstance(parameters['clip_sprites'], bool):
        is_valid = False
    if parameters['classification_scheme'] != 'distribution' or parameters['classification_scheme'] != 'discrete'
    or parameters['classification_scheme'] != 'random':
        is_valid = False

    return is_valid


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
    else:
        are_values_correct = False

    return are_keys_correct and are_values_correct

