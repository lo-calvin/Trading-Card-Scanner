# Trading-Card-Scanner

### Create an environment and install dependencies

I use `python3.11` for this project.

#### Mac/Linux/WSL

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

# init db (assuming running from Trading-Card-Scanner dir)

This will delete previous db and start fresh for now. It will create cards.db in Trading-Card-Scanner/src/backend/

`python src/backend/init_db.py `
