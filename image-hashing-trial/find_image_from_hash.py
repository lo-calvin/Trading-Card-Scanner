# load image scrapped into hashes dict
import json
from PIL import Image
import imagehash

average_hash_file = 'database/image_hashes_average_hash.json'
dhash_file = 'database/image_hashes_dhash.json'
phash_file = 'database/image_hashes_phash.json'
whash_file = 'database/image_hashes_whash.json'

# load the dictionary (database)
with open(average_hash_file, 'r', encoding='utf-8') as f:
    average_hash_data = json.load(f)
    
with open(dhash_file, 'r', encoding='utf-8') as f:
    dhash_data = json.load(f)
    
with open(phash_file, 'r', encoding='utf-8') as f:
    phash_data = json.load(f)
    
with open(whash_file, 'r', encoding='utf-8') as f:
    whash_data = json.load(f)
    

# load the cropped images
cropped_image_path = "cropped/cropped_cutout_0.png"
cropped_image = Image.open(cropped_image_path)
cropped_phash = imagehash.phash(cropped_image)
cropped_dhash = imagehash.dhash(cropped_image)
cropped_whash = imagehash.whash(cropped_image)
cropped_average_hash = imagehash.average_hash(cropped_image)

# find the closest hash
def find_closest_hash(cropped_hash, hash_data):
    closest_id = None
    min_distance = float('inf')
    
    for stored_hash, image_id in hash_data.items():
        distance = cropped_hash - imagehash.hex_to_hash(stored_hash)
            
        if distance < min_distance:
            min_distance = distance
            closest_id = image_id
            
    return closest_id, min_distance
        


# Find the closest distance of each hash
closest_phash_id, phash_distance = find_closest_hash(cropped_phash, phash_data)
closest_dhash_id, dhash_distance = find_closest_hash(cropped_dhash, dhash_data)
closest_average_hash_id, average_hash_distance = find_closest_hash(cropped_average_hash, average_hash_data)
closest_whash_id, whash_distance = find_closest_hash(cropped_whash, whash_data)

# result
print(f"Closest image by pHash: {closest_phash_id} with distance {phash_distance}")
print(f"Closest image by dHash: {closest_dhash_id} with distance {dhash_distance}")
print(f"Closest image by average hash: {closest_average_hash_id} with distance {average_hash_distance}")
print(f"Closest image by whash: {closest_whash_id} with distance {whash_distance}")

def calculate_weighted_similarity(phash_distance, dhash_distance, average_hash_distance, whash_distance):
    """calculate the weighted similarity"""
    weights = {
        'phash': 0.8,        # phash is most sensitive to structural changes
        'dhash': 0.5,        # dhash is most sensitive to gradient changes
        'average_hash': 1,  # average hash is the most stable but least sensitive
        'whash': 0.3         # whash is most sensitive to texture changes
    }
    
    total_weight = sum(weights.values())
    
    weighted_distance = (
        phash_distance * weights['phash'] +
        dhash_distance * weights['dhash'] +
        average_hash_distance * weights['average_hash'] +
        whash_distance * weights['whash']
    ) / total_weight
    
    return weighted_distance

# after finding all distances, calculate the weighted result
distances = {
    closest_phash_id: phash_distance,
    closest_dhash_id: dhash_distance,
    closest_average_hash_id: average_hash_distance,
    closest_whash_id: whash_distance
}

# find all possible image IDs
unique_image_ids = set([closest_phash_id, closest_dhash_id, 
                       closest_average_hash_id, closest_whash_id])

# calculate the weighted distance for each unique image ID
best_match = None
min_weighted_distance = float('inf')

for image_id in unique_image_ids:
    # if the hash method does not match this image_id, use a large but finite value
    max_reasonable_distance = 30  # set a reasonable maximum distance value
    
    current_phash_distance = phash_distance if closest_phash_id == image_id else max_reasonable_distance
    current_dhash_distance = dhash_distance if closest_dhash_id == image_id else max_reasonable_distance
    current_average_distance = average_hash_distance if closest_average_hash_id == image_id else max_reasonable_distance
    current_whash_distance = whash_distance if closest_whash_id == image_id else max_reasonable_distance
    
    weighted_distance = calculate_weighted_similarity(
        current_phash_distance,
        current_dhash_distance,
        current_average_distance,
        current_whash_distance
    )
    
    if weighted_distance < min_weighted_distance:
        min_weighted_distance = weighted_distance
        best_match = image_id

print(f"\nFinal weighted result:")
print(f"The most matching image ID: {best_match}")
print(f"Weighted distance: {min_weighted_distance:.2f}")