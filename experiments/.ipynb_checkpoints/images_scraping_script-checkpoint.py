import os
import json
import requests

# Define the input and output directories
input_folder = 'cards'  # Update with the path to your folder with JSON files
output_folder = 'images'  # Update with the path where images should be saved

# Create the output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through each file in the input directory
for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        file_path = os.path.join(input_folder, filename)
        
        # Open and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                
                # Loop through each entry in the JSON data
                for entry in data:
                    try:
                        # Extract the large image URL
                        image_url = entry.get('images', {}).get('large')
                        
                        if image_url:
                            # Define the filename for the image
                            image_name = f"{entry.get('id', 'unknown')}.png"
                            image_path = os.path.join(output_folder, image_name)
                            
                            # Download and save the image
                            response = requests.get(image_url)
                            if response.status_code == 200:
                                with open(image_path, 'wb') as img_file:
                                    img_file.write(response.content)
                                print(f"Downloaded {image_name}")
                            else:
                                print(f"Failed to download image for {entry.get('id', 'unknown')}")
                    
                    except Exception as e:
                        print(f"Error processing entry in {filename}: {e}")
            
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {filename}: {e}")
