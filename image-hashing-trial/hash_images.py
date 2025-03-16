import os
from PIL import Image
import imagehash
import json

# define the image folder and the results files for different hash methods
image_folder = 'images-subset'
hash_methods = {
    'average_hash': {'function': imagehash.average_hash, 'params': {}},
    'phash': {'function': imagehash.phash, 'params': {}},
    'dhash': {'function': imagehash.dhash, 'params': {}},
    'whash': {'function': imagehash.whash, 'params': {}},
}

# process images for each hash method
for method_name, method_info in hash_methods.items():
    hash_to_id = {}  # use hash value as key, image ID as value
    results_file = f'database/image_hashes_{method_name}.json'
    
    # iterate through all the images in the image folder
    for image_name in os.listdir(image_folder):
        if image_name.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_name)
            
            # calculate the hash value of the image using current method with its parameters
            hash_value = method_info['function'](Image.open(image_path), **method_info['params'])
            # use hash value as key, image file name (without extension) as value
            hash_to_id[str(hash_value)] = os.path.splitext(image_name)[0]

    # store the results in a JSON file
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(hash_to_id, f, ensure_ascii=False, indent=4)
    
    print(f"{method_name} hashes have been saved to {results_file}") 