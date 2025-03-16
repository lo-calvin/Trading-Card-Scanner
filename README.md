# Trading-Card-Scanner

### Contributors

Calvin Lo: lo.cal@northeastern.edu

Nina Lui: lui.n@northeastern.edu

Jingyu Wang: wang.jingyu6@northeastern.edu

Xiaolai Chen: chen.xiaola@northeastern.edu

Jordan Lewis: lewis.jor@northeastern.edu

Trading Card Scanner is a tool designed to simplify looking up and storing important information about your Pokemon TCG collection. Our app utilizes the Qualcomm AI YOLOv11-Detection model to recognize the card shapes and ResNet to extract key card information.

<p align="center">
<img src="https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/cards_on_synthetic_background.png" width="45%">
<img src="https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/Recgonizing_card_shapes.png" width="45%">
</p>

Once the name and id is from a given card, we call to the PokemonTCG API, which provides all information about the card, from statistics to updated pricing. Our app then displays that information in a user friendly setting and continue to add to your collection.

<p align="center">
  <img src="https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/Predicting_pokemon_ids.png" width="45%">
  <img src="https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/Predicting_trainer_ids.png" width="45%">
</p>

## How to Run

### Create an environment and install dependencies

Ensure `python3.11` is installed for this project.

#### Create env Mac/Linux/WSL

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Initialize Database (assuming running from root directory Trading-Card-Scanner)

This will delete previous db and start fresh for now. It will create cards.db in Trading-Card-Scanner/src/backend/

```
python src/backend/init_db.py
```

### Running frontend

```
python -m streamlit run src/frontend/app.py
```

### Testing App on the Frontend

Once running, you will be able to see the home screen. Here you will have the option to 'Scan from camera' or 'Scan from file'. Either option will allow you to input an image of your cards to be scanned for your collection.

![alt text](https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/homepage.png)

Once scanned you will be able to select which cards are added to your database

![alt text](https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/scannedCards.png)

![alt text](https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/select%20scanned%20data.png)

After selecting your cards you can now view the pricing information under the collections tab

![alt text](https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/refs/heads/main/res/readme%20images/collection.png)
