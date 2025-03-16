# Trading-Card-Scanner

Trading Card Scanner is a tool designed to simplify looking up and storing important information about your Pokemon TCG collection. Our app utilizes the Qualcomm AI YOLOv11-Detection model to recognize the card shapes and ResNet to extract key card information.

<p align="center">
<img src="https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/main/res/cards_on_synthetic_background.png" width="45%">
<img src="https://raw.githubusercontent.com/lo-calvin/Trading-Card-Scanner/main/res/Recgonizing_card_shapes.png" width="45%">
</p>

Once the name and id is from a given card, we call to the PokemonTCG API, which provides all information about the card, from statistics to updated pricing. Our app then displays that information in a user friendly setting...

### Create an environment and install dependencies

I use `python3.11` for this project.

#### Mac/Linux/WSL

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### init db (assuming running from Trading-Card-Scanner dir)

This will delete previous db and start fresh for now. It will create cards.db in Trading-Card-Scanner/src/backend/

`python src/backend/init_db.py `


### Running frontend
`python -m streamlit run src/frontend/app.py`
