"""
_cli.py is the command-line program for that the user can use to generate pseudo-random artificial data for games.

@author: Jaden Kim & Chanha Kim
"""

import argparse
import os
# from multiprocessing import cpu_count
from .yards import yards

# get arguments
def _get_args():
    """Parses and returns command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c',
        type=str,
        default=None,
        help='The path to the config.yaml file.'
    )
    parser.add_argument('--visualize', '-v',
        nargs='*',
        default=None,
        help='Whether or not to visualize the output.'
    )
    # parser.add_argument('--parallel', '-p',
    #     action='store_true',
    #     help='Whether or not to parallelize the processes.'
    # )
    
    return parser.parse_args()

def _valid_config(config_path):
    '''Returns true if the path exists'''
    return config_path != None and os.path.exists(config_path)

def _valid_visualize(arguments):
    '''Returns true if arguments are valid'''
    not_none = arguments != None
    if not_none:
        if len(arguments) == 1:
            valid = arguments[0].isnumeric()
        elif len(arguments) == 2:
            valid = os.path.exists(arguments[0]) and arguments[1].isnumeric()
    else:
        valid = False
    return not_none and valid

def main():
    '''Entry point for cli interface'''
    args = _get_args()
    yd = yards()

    if _valid_config(args.config):
        yd.load_config_from_file(args.config)
        yd.loop()
        
        # if args.parallel:
        #     num_cpus = cpu_count()
        #     yd.parallel_loop(num_cpus=num_cpus)
        # else:
        #     yd.loop()

    if _valid_visualize(args.visualize):
        if len(args.visualize) == 1:
            yd.visualize(num_visualize=int(args.visualize[0]))
        elif len(args.visualize) == 2:
            yd.visualize(directory=args.visualize[0], num_visualize=int(args.visualize[1]))





