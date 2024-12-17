import os

def try_create_dir_from_filepath(filepath : str):
    if os.path.exists(os.path.dirname(filepath)):
        return
    os.makedirs(os.path.dirname(filepath))
