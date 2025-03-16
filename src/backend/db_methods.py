# This file contains the various call methods to the database

import os
import requests
from dotenv import load_dotenv
from .init_db import get_db_connection
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

API_KEY = os.getenv("API_KEY")

API_URL = "https://api.pokemontcg.io/v2/cards/"

# Set up headers with API key
headers = {"Authorization": f"Bearer {API_KEY}"}


def get_card(id):
    '''
    Fetches the card from the tcg api and returns a json dict containing
    the card information
    @param id: The card's id
    return card: The json dict containing the card information
    '''
    # Make GET request
    card = requests.get(API_URL + id, headers=headers)

    card_info = card.json()

    # Check if request was successful
    if card.status_code == 200:
        # Print JSON response
        logging.info(
            f"Success {card.status_code}! Retrieved info for card -> {card_info['data']['id']}: {card_info['data']['name']}")
        return card_info
    else:
        logging.info("Error:", card.status_code, card.text)

# ============================== Data Extraction Functions ==================================


def extract_card_table_data(card):
    '''
    Extracts the information for the card table from the json
    This includes, id, name, supertype, subtype, set_name, rarity, image and url
    @param card: The dict containing card information
    '''
    card_data = card['data']

    # Extract fields
    card_id = card_data['id']
    name = card_data['name']
    supertype = card_data['supertype']
    subtypes = ', '.join(card_data.get('subtypes', [])
                         )  # Convert list to string
    set_name = card_data['set']['name']
    # Some cards may not have rarity
    rarity = card_data.get('rarity', 'Unknown')
    image_url = card_data['images']['small']
    url = card_data['tcgplayer']['url']

    return (
        card_id,
        name,
        supertype,
        subtypes,
        set_name,
        rarity,
        image_url,
        url
    )


def extract_pokemon_table_data(card):
    '''
    Extracts the information for the pokemon table from the json
    This includes, id, name, hp, type, evolves_from, evolves_to, release_date,
    and set_name
    @param card: The dict containing card information
    '''
    card_data = card['data']

    pokemon_id = card_data['id']
    name = card_data['name']
    # Include supertype for all cards
    supertype = card_data.get('supertype', 'NA')

    if supertype == 'Pokémon':  # Extract Pokémon-specific fields
        hp = int(card_data.get('hp', 0))
        types = ', '.join(card_data.get('types', [])
                          ) if 'types' in card_data else 'NA'
        evolves_from = card_data.get('evolvesFrom', 'NA')
        evolves_to = ', '.join(card_data.get(
            'evolvesTo', [])) if 'evolvesTo' in card_data else 'NA'
    else:  # Handle Trainer or other card types
        hp = None
        types = 'NA'
        evolves_from = 'NA'
        evolves_to = 'NA'

    release_date = card_data['set']['releaseDate']
    set_name = card_data['set']['name']

    return (
        pokemon_id,
        name,
        supertype,
        hp,
        types,
        evolves_from,
        evolves_to,
        release_date,
        set_name
    )


def extract_tcgplayer_table_data(card):
    '''
    Extracts the information for the tcgplayer table from the json
    This includes: url and updated_at information
    @param card: The dict containing card information
    '''
    tcgplayer_data = card['data'].get('tcgplayer', {})

    if not tcgplayer_data:
        return None

    url = tcgplayer_data['url']
    updated_at = tcgplayer_data['updatedAt']

    return (url, updated_at)


def extract_price_table_data(card):
    '''
    Extracts the information for the price table from the json
    This includes: url, type(holo, reverse holo, etc), and 
    the pricing - low, mid, high, market, direct_low
    @param card: The dict containing card information
    '''
    tcgplayer_data = card['data'].get('tcgplayer', {})
    prices_data = tcgplayer_data.get('prices', {})

    price_entries = []
    for price_type, values in prices_data.items():
        tcgplayer_url = tcgplayer_data['url']
        low = values.get('low', 0.0)
        mid = values.get('mid', 0.0)
        high = values.get('high', 0.0)
        market = values.get('market', 0.0)
        direct_low = values.get('directLow', 0.0)

        price_entries.append(
            (tcgplayer_url, price_type, low, mid, high, market, direct_low))

    return price_entries


# ============================= Database Insert Functions ===============================


def insert_into_card_table(card):
    '''
    Inserts card information into the Card table
    Updates count if the card already exists.
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    card_data = extract_card_table_data(card)

    # Check if the card already exists
    cursor.execute("SELECT count FROM Card WHERE id = ?", (card_data[0],))
    existing_card = cursor.fetchone()

    if existing_card:
        new_count = existing_card[0] + 1
        cursor.execute("UPDATE Card SET count = ? WHERE id = ?",
                       (new_count, card_data[0]))
    else:
        cursor.execute("""
            INSERT INTO Card (id, name, supertype, subtype, set_name, rarity, image_url, url, count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, card_data)

    conn.commit()
    conn.close()


def insert_into_pokemon_table(card):
    '''
    Inserts card information into the Pokemon table
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    pokemon_data = extract_pokemon_table_data(card)
    cursor.execute("""
        INSERT OR IGNORE INTO Pokemon (id, name, supertype, hp, type, evolves_from, evolves_to, release_date, set_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, pokemon_data)

    conn.commit()
    conn.close()


def insert_into_tcgplayer_table(card):
    '''
    Inserts card information into the TCGPlayer table
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    tcgplayer_data = extract_tcgplayer_table_data(card)
    if tcgplayer_data:
        cursor.execute("""
            INSERT OR IGNORE INTO TCGPlayer (url, updated_at)
            VALUES (?, ?)
        """, tcgplayer_data)

    conn.commit()
    conn.close()


def insert_into_prices_table(card):
    '''
    Inserts card information into the Prices table
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    prices_data = extract_price_table_data(card)
    for price in prices_data:
        cursor.execute("""
            INSERT OR REPLACE INTO Prices (tcgplayer_url, type, low, mid, high, market, direct_low)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, price)

    conn.commit()
    conn.close()


def populate_tables(id):
    '''
    Populates all database tables with necessary information
    based upon card id
    '''
    card = get_card(id)
    if card:
        insert_into_card_table(card)
        insert_into_pokemon_table(card)
        insert_into_prices_table(card)
        insert_into_tcgplayer_table(card)
        logging.info(f"Successfully inserted data for card {id}")


# ============================= Database Retrieval Functions ===============================

def get_card_info(id):
    '''
    Retrieves information from the card table of a given id
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Card WHERE id = ?", (id,))
    card = cursor.fetchone()

    conn.close()
    logging.info(f"Retrieved card: {card}")
    return card


def get_pokemon_info(id):
    '''
    Retrieves information from the pokemon table for a given id
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Pokemon WHERE id = ?", (id,))
    pokemon = cursor.fetchone()

    conn.close()
    logging.info(f"Retrieved pokemon information: {pokemon}")
    return pokemon


def get_price_info(id):
    '''
    Retrieves information from the pricing table for a given id
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Prices.* FROM Prices
        JOIN TCGPlayer ON Prices.tcgplayer_url = TCGPlayer.url
        WHERE TCGPlayer.url = (SELECT url FROM Card WHERE id = ?)
    """, (id,))

    prices = cursor.fetchall()

    conn.close()
    logging.info(f"Retrieved pricing: {prices}")
    return prices


# TODO combine certain elements for different dataframes

def retrieve_card_pricing_table():
    '''
    Retrieves all cards with pricing information, grouping prices under
    "normal", "holofoil", and "reverse holofoil" categories.
    Displays: Image, Name, Set, Rarity, Number Owned, Normal Price, 
    Holofoil Price, Reverse Holofoil Price, Price URL.
    Returns a pandas DataFrame.
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        Card.image_url, 
        Card.name, 
        Card.set_name, 
        Card.rarity, 
        Card.count, 
        MAX(CASE WHEN Prices.type = 'normal' THEN Prices.market END) AS normal_price,
        MAX(CASE WHEN Prices.type = 'holofoil' THEN Prices.market END) AS holofoil_price,
        MAX(CASE WHEN Prices.type = 'reverseHolofoil' THEN Prices.market END) AS reverse_holofoil_price,
        TCGPlayer.url 
    FROM Card
    LEFT JOIN TCGPlayer ON Card.url = TCGPlayer.url
    LEFT JOIN Prices ON TCGPlayer.url = Prices.tcgplayer_url
    GROUP BY Card.id
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    # Convert to pandas DataFrame
    df = pd.DataFrame(results, columns=[
        "Image", "Name", "Set", "Rarity", "Number Owned",
        "Normal Price", "Holofoil Price", "Reverse Holofoil Price", "Price URL"
    ])

    return df


def retrieve_pokemon_information_table():
    '''
    Retrieves all cards with pricing information, displaying:
    image, name, set, rarity, market price, low price, high price, price url.
    Returns a pandas DataFrame.
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        Card.image_url, 
        Card.name, 
        Card.set_name, 
        Card.rarity, 
        Card.count, 
        Pokemon.supertype, 
        Pokemon.hp, 
        Pokemon.type, 
        Pokemon.evolves_from, 
        Pokemon.evolves_to, 
        Pokemon.release_date, 
        TCGPlayer.url 
    FROM Pokemon
    JOIN Card ON Pokemon.id = Card.id
    LEFT JOIN TCGPlayer ON Card.url = TCGPlayer.url
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    # Convert to pandas DataFrame
    df = pd.DataFrame(results, columns=[
        "Image", "Name", "Set", "Rarity", "Number Owned", "Supertype", "HP", "Type",
        "Evolves From", "Evolves To", "Release Date", "Price URL"
    ])

    return df


# ============================= Database Deletion Functions ===============================


def delete_card(id):
    '''
    Deletes a card or decrements its count from the Card table.
    If count > 1, decrements the count.
    If count == 1, deletes the card and related records from all tables.
    @param id: The card to delete
    @return: No return 
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get current count of the card
        cursor.execute("SELECT count FROM Card WHERE id = ?", (id,))
        result = cursor.fetchone()

        if not result:
            logging.warning(f"Card {id} not found in the database.")
            return

        current_count = result[0]

        if current_count > 1:
            # If there are multiple copies, just decrement the count
            cursor.execute(
                "UPDATE Card SET count = count - 1 WHERE id = ?", (id,))
            logging.info(
                f"Decremented count for card {id}. New count: {current_count - 1}")
        else:
            # If only 1 copy exists, delete it completely from all tables
            logging.info(f"Deleting card {id} and all related data.")

            # Get TCGPlayer URL for related deletions
            cursor.execute("SELECT url FROM Card WHERE id = ?", (id,))
            tcgplayer_url = cursor.fetchone()

            if tcgplayer_url:
                tcgplayer_url = tcgplayer_url[0]

                # Delete from Prices table (linked via TCGPlayer URL) and subsequent tables
                cursor.execute(
                    "DELETE FROM Prices WHERE tcgplayer_url = ?", (tcgplayer_url,))
                cursor.execute(
                    "DELETE FROM TCGPlayer WHERE url = ?", (tcgplayer_url,))

            cursor.execute("DELETE FROM Pokemon WHERE id = ?", (id,))
            cursor.execute("DELETE FROM Card WHERE id = ?", (id,))

            logging.info(
                f"Successfully deleted card {id} and all related data.")

        conn.commit()
    except Exception as e:
        logging.error(f"Error deleting card {id}: {e}")
    finally:
        conn.close()


def main():

    # cards = ['swsh4-25', 'xy1-1', 'xyp-XY27',
    #          'xyp-XY25', 'sm35-1', 'ex9-1', 'ex9-86']
    # for card in cards:
    #     populate_tables(card)
    #     get_card_info(card)
    #     get_pokemon_info(card)
    #     get_price_info(card)

    card_pricing_df = retrieve_card_pricing_table()
    print(card_pricing_df)
    poke_info = retrieve_pokemon_information_table()
    print(poke_info)


if __name__ == "__main__":
    main()
