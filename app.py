from flask import Flask, render_template, request, redirect, url_for
import requests
import random
from flask_babel import Babel
app = Flask(__name__)

SPOONACULAR_API_KEY = 'b73d3e10b4ca474891e5fdc952e1ee4d'  # Replace with your key
SEARCH_ENDPOINT = "https://api.spoonacular.com/recipes/complexSearch"
EXTRACT_ENDPOINT = "https://api.spoonacular.com/recipes/extract"



def extract_recipe_details(source_url):
    """Uses the Spoonacular extract endpoint to retrieve detailed recipe data."""
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'url': source_url
    }
    response = requests.get(EXTRACT_ENDPOINT, params=params)
    data = response.json()
    return data


def fetch_recipe_by_country(country):
    # Search for recipes that match the given country.
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'query': country,
        'number': 100,  # Retrieve up to 100 recipes for filtering.
        'addRecipeInformation': True
    }
    response = requests.get(SEARCH_ENDPOINT, params=params)
    data = response.json()
    
    # Filter for recipes that have a sourceUrl (to allow extraction).
    valid_recipes = []
    for recipe_data in data.get('results', []):
        source_url = recipe_data.get('sourceUrl')
        if source_url and source_url.strip() != '':
            valid_recipes.append(recipe_data)
    
    if valid_recipes:
        chosen_recipe = random.choice(valid_recipes)
        source_url = chosen_recipe.get('sourceUrl')
        detailed_data = extract_recipe_details(source_url)
        
        # Extract ingredients from the detailed data.
        ingredients_list = []
        if "extendedIngredients" in detailed_data:
            ingredients_list = [ing.get("name", "Unknown") for ing in detailed_data["extendedIngredients"]]
        elif "ingredients" in detailed_data:
            ingredients_list = [ing.get("name", "Unknown") for ing in detailed_data["ingredients"]]
        
        # Process the summary:
        summary = detailed_data.get("summary", "")
        # Remove any "Similar recipes include" text.
        if "Similar recipes" in summary:
            summary = summary.split("Similar recipes include")[0]
        # Truncate summary after the spoonacular score text.
        if "spoonacular" in summary:
            start = summary.find("spoonacular")
            end = summary.find("%", start)
            if end != -1:
                summary = summary[:end+1]
    
        recipe_return = {
            "title": detailed_data.get("title", chosen_recipe.get("title", "No title")),
            "ingredients": ingredients_list,
            "summary": summary,
            "instructions": detailed_data.get("instructions", "")
        }
        
        
        recipe_return["ingredients"] = ingredients_list
        
        return recipe_return
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        country = request.form.get('country')
        return redirect(url_for('explore', country=country))
    return render_template('index.html')

@app.route('/explore')
def explore():
    country = request.args.get('country')
    recipe = fetch_recipe_by_country(country)
    return render_template("explore.html", recipe=recipe, country=country)

if __name__ == '__main__':
    app.run(debug=True)
