# Trading-Card-Scanner

Trading Card Scanner is a tool designed to simplify looking up and storing important information about your Pokemon TCG collection. Our app utilizes the Qualcomm AI YOLOv11-Detection model to recognize the card shapes and ResNet to extract key card information.

### Create an environment and install dependencies

I use `python3.11` for this project.

#### Mac/Linux/WSL

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

#### init db (assuming running from Trading-Card-Scanner dir)

This will delete previous db and start fresh for now. It will create cards.db in Trading-Card-Scanner/src/backend/

```
python src/backend/init_db.py
```
