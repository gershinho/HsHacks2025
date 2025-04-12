from flask import Flask, render_template, request, redirect, url_for
import requests
import random
from flask_babel import Babel

app = Flask(__name__)

SPOONACULAR_API_KEY = 'ec919ca796094077bd8bc1fe9635935b'  # Replace with your key
SEARCH_ENDPOINT = "https://api.spoonacular.com/recipes/complexSearch"
EXTRACT_ENDPOINT = "https://api.spoonacular.com/recipes/extract"


def extract_recipe_details(source_url):
    """Uses the Spoonacular extract endpoint to retrieve detailed recipe data."""
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'url': source_url
    }
    response = requests.get(EXTRACT_ENDPOINT, params=params)
    return response.json()


def fetch_recipe_by_country(country):
    # Search for recipes that match the given country.
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'query': country,
        'number': 100,
        'addRecipeInformation': True
    }
    data = requests.get(SEARCH_ENDPOINT, params=params).json()
    
    # Filter for recipes that have a sourceUrl
    valid = [r for r in data.get('results', []) if r.get('sourceUrl')]
    if not valid:
        return None

    chosen = random.choice(valid)
    details = extract_recipe_details(chosen['sourceUrl'])
    
    # Ingredients
    ingredients = []
    if "extendedIngredients" in details:
        ingredients = [ing.get("name", "Unknown") for ing in details["extendedIngredients"]]
    elif "ingredients" in details:
        ingredients = [ing.get("name", "Unknown") for ing in details["ingredients"]]
    ingredients = [i.split('-')[0].strip() for i in ingredients]
    
    # Summary filtering
    summary = details.get("summary", "")
    cut_markers = [
        "Similar recipes include",
        "Overall",
        "Taking all factors into account",
        "It is brought to you by"
    ]
    cut_index = len(summary)
    for m in cut_markers:
        idx = summary.find(m)
        if idx != -1 and idx < cut_index:
            cut_index = idx
    summary = summary[:cut_index].strip()
    # spoonacular score truncation
    sc = "spoonacular score"
    idx = summary.find(sc)
    if idx != -1:
        end = summary.find("%", idx)
        if end != -1:
            summary = summary[:end+1]

    return {
        "title": details.get("title", chosen.get("title", "No title")),
        "image": chosen.get("image", ""),
        "ingredients": ingredients,
        "summary": summary,
        "instructions": details.get("instructions", "")
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        country = request.form.get('country')
        return redirect(url_for('explore', country=country))
    return render_template('home.html')


@app.route('/explore')
def explore():
    country = request.args.get('country')
    recipe = fetch_recipe_by_country(country)
    return render_template("explore.html", recipe=recipe, country=country)


if __name__ == '__main__':
    app.run(debug=True)
