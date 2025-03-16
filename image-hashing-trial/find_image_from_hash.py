import json
from PIL import Image
import imagehash
from typing import Dict, Any, Tuple, Optional, Union

def match_image_with_hashes(
    image_path: str,
    hash_files: Dict[str, str],
    hash_weights: Optional[Dict[str, float]] = None,
    max_reasonable_distance: int = 30
) -> Dict[str, Any]:
    """
    Find the most matching image from the database using multiple hash methods.
    
    Args:
        image_path (str): Path to the image to match
        hash_files (dict): Dictionary containing paths to hash database files
            Required keys: 'average_hash', 'dhash', 'phash', 'whash'
        hash_weights (dict, optional): Weights for different hash methods
        max_reasonable_distance (int, optional): Maximum distance to consider for non-matching hashes
        
    Returns:
        dict: Dictionary containing matching results and distances
    """
    if hash_weights is None:
        hash_weights = {
            'phash': 1.0,        # phash is most sensitive to structural changes
            'dhash': 0.3,        # dhash is most sensitive to gradient changes
            'average_hash': 0.6, # average hash is the most stable but least sensitive
            'whash': 0.2         # whash is most sensitive to texture changes
        }
    
    # Load hash databases
    hash_data = {}
    for hash_type, file_path in hash_files.items():
        with open(file_path, 'r', encoding='utf-8') as f:
            hash_data[hash_type] = json.load(f)
    
    # Calculate hashes for the image
    input_image = Image.open(image_path)
    hashes = {
        'phash': imagehash.phash(input_image),
        'dhash': imagehash.dhash(input_image),
        'average_hash': imagehash.average_hash(input_image),
        'whash': imagehash.whash(input_image)
    }
    
    # Find closest matches for each hash type
    closest_matches = {}
    distances = {}
    
    for hash_type, hash_value in hashes.items():
        closest_id, distance = find_closest_hash(hash_value, hash_data[hash_type])
        closest_matches[hash_type] = closest_id
        distances[hash_type] = distance
    
    # Calculate weighted result
    unique_image_ids = set(closest_matches.values())
    weighted_results = {}
    
    for image_id in unique_image_ids:
        current_distances = {
            hash_type: distances[hash_type] if closest_matches[hash_type] == image_id 
            else max_reasonable_distance
            for hash_type in hash_weights.keys()
        }
        
        weighted_distance = calculate_weighted_distance(current_distances, hash_weights)
        weighted_results[image_id] = weighted_distance
    
    # Find the best match
    best_match = min(weighted_results.items(), key=lambda x: x[1])
    
    return {
        'raw_hashes': {hash_type: str(hash_val) for hash_type, hash_val in hashes.items()},
        'individual_matches': {
            hash_type: {
                'id': match_id, 
                'distance': distances[hash_type]
            }
            for hash_type, match_id in closest_matches.items()
        },
        'all_weighted_matches': {
            image_id: {
                'weighted_distance': distance,
                'similarity_score': calculate_similarity_score(distance)
            }
            for image_id, distance in weighted_results.items()
        },
        'best_match': {
            'id': best_match[0],
            'weighted_distance': best_match[1],
            'similarity_score': calculate_similarity_score(best_match[1])
        }
    }

def find_closest_hash(query_hash: Union[imagehash.ImageHash, str], 
                     hash_data: Dict[str, str]) -> Tuple[str, int]:
    """
    Find the closest matching hash in the database.
    
    Args:
        query_hash: Hash of the query image
        hash_data: Dictionary mapping hash strings to image IDs
        
    Returns:
        Tuple containing (image_id, distance)
    """
    closest_id = None
    min_distance = float('inf')
    
    for stored_hash, image_id in hash_data.items():
        # Convert stored hash string to ImageHash object if needed
        if isinstance(stored_hash, str):
            stored_hash_obj = imagehash.hex_to_hash(stored_hash)
        else:
            stored_hash_obj = stored_hash
            
        # Calculate distance
        distance = query_hash - stored_hash_obj
            
        if distance < min_distance:
            min_distance = distance
            closest_id = image_id
            
    return closest_id, min_distance

def calculate_weighted_distance(distances: Dict[str, int], 
                              weights: Dict[str, float]) -> float:
    """
    Calculate weighted distance across multiple hash methods.
    
    Args:
        distances: Dictionary mapping hash types to their distances
        weights: Dictionary mapping hash types to their weights
        
    Returns:
        Weighted average distance
    """
    total_weight = sum(weights.values())
    
    weighted_sum = sum(
        distances[hash_type] * weights[hash_type]
        for hash_type in weights.keys()
    )
    
    return weighted_sum / total_weight

def calculate_similarity_score(distance: float, 
                             max_distance: float = 30.0) -> float:
    """
    Convert a distance value to a similarity score (0-100).
    
    Args:
        distance: The weighted distance
        max_distance: Maximum reasonable distance
        
    Returns:
        Similarity score between 0 and 100
    """
    # Clamp distance to max_distance
    clamped_distance = min(distance, max_distance)
    
    # Convert to similarity score (100 = perfect match, 0 = completely different)
    similarity = 100 * (1 - (clamped_distance / max_distance))
    
    return max(0, similarity)

# Example usage:
if __name__ == "__main__":
    hash_files = {
        'average_hash': 'database/image_hashes_average_hash.json',
        'dhash': 'database/image_hashes_dhash.json',
        'phash': 'database/image_hashes_phash.json',
        'whash': 'database/image_hashes_whash.json'
    }
    
    result = match_image_with_hashes(
        image_path="cropped/cropped_cutout_1.png",
        hash_files=hash_files
    )
    
    # Print raw hashes
    print("Raw image hashes:")
    for hash_type, hash_val in result['raw_hashes'].items():
        print(f"{hash_type}: {hash_val}")
    
    # Print individual hash results
    print("\nIndividual hash results:")
    for hash_type, match_info in result['individual_matches'].items():
        print(f"Closest image by {hash_type}: {match_info['id']} "
              f"with distance {match_info['distance']}")
    
    # Print final result
    print(f"\nFinal weighted result:")
    print(f"The most matching image ID: {result['best_match']['id']}")
    print(f"Weighted distance: {result['best_match']['weighted_distance']:.2f}")
    print(f"Similarity score: {result['best_match']['similarity_score']:.2f}%")
    
    # Print all weighted matches
    print("\nAll weighted matches:")
    for image_id, match_info in sorted(
        result['all_weighted_matches'].items(), 
        key=lambda x: x[1]['similarity_score'], 
        reverse=True
    ):
        print(f"Image ID: {image_id}, "
              f"Similarity: {match_info['similarity_score']:.2f}%, "
              f"Distance: {match_info['weighted_distance']:.2f}")