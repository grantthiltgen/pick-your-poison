import flask
from flask import request, redirect, url_for
from textgenrnn import textgenrnn
from keras.backend import clear_session
import pickle
import random
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

with open('models/cocktail_recommender.pickle', 'rb') as fp:
    cocktail_recommender = pickle.load(fp)
with open('models/cocktails_for_app.pickle', 'rb') as fp:
    cocktail_recipes = pickle.load(fp)
with open('models/cocktail_names.pickle', 'rb') as fp:
    cocktail_names = pickle.load(fp)

        
# Initialize the app

app = flask.Flask(__name__)


# An example of routing:
# If they go to the page "/" (this means a GET request
# to the page http://127.0.0.1:5000/), return a simple
# page that says the site is up!


@app.route("/", methods=["POST", "GET"])
def drink_input():
    # request.args contains all the arguments passed by our form
    # comes built in with flask. It is a dictionary of the form
    # "form name (as set in template)" (key): "string in the textbox" (value)
    #cuisine1, cuisine2 = make_prediction(request.args)
    #return flask.render_template('predictor.html', cuisine1=cuisine1,
    #                             cuisine2=cuisine)
    return flask.render_template('index.html')

@app.route("/experimental-cocktails", methods=['GET', 'POST'])
def experimental_cocktails():
    return flask.render_template('experimental-cocktail.html')

@app.route("/experimental-surprise-me", methods=['GET', 'POST'])
def experimental_surprise_me():
    clear_session()
    generator = textgenrnn('./models/name_weights.hdf5')
    name = generator.generate(temperature = 1.2, return_as_list=True)
    clear_session()
    generator = textgenrnn('./models/cocktail_weights.hdf5')
    cocktail = generator.generate(temperature = 0.5, return_as_list=True)
    ing = cocktail[0].split(',')
    return flask.render_template('experimental-result.html', name = name[0],
                                 ingredients=ing)

@app.route("/experimental-pick-your-poison", methods=['GET', 'POST'])
def experimental_pick_your_poison():
    try:
        base = request.form['Alcohol']
        clear_session()
        generator = textgenrnn('./models/name_weights.hdf5')
        name = generator.generate(temperature = 1.2, return_as_list=True)
        clear_session()
        seed = random.choice(['1/2 oz ','1 oz ', '2 oz ']) + base
        generator = textgenrnn('./models/cocktail_weights.hdf5')
        cocktail = generator.generate(temperature = 0.5, prefix=seed, return_as_list=True)
        ing = cocktail[0].split(',')
        return flask.render_template('experimental-result.html', name = name[0],
                                 ingredients=ing)
    except:
        return redirect(url_for("experimental_cocktails"))  

    
@app.route("/recipe", methods=['GET', 'POST'])
def recipe():
    try:
        cocktail = request.form['Cocktail']
        cocktail_lower = cocktail.lower()
        if cocktail_lower not in cocktail_names:
            best_match = 0
            best_cocktails = []
            for name in cocktail_names:
                FuzzyMatch = fuzz.partial_ratio(name,cocktail_lower)
                if FuzzyMatch >= best_match:
                    best_cocktails.append(name)
                    best_match = FuzzyMatch
            best_match = 0
            best_cocktail = []
            for match in best_cocktails:
                FuzzyMatch = fuzz.ratio(match,cocktail_lower)
                if FuzzyMatch > best_match:
                    best_cocktail = match
                    best_match = FuzzyMatch
                cocktail_lower = best_cocktail
                cocktail = cocktail_lower.capitalize()
        ingredients = cocktail_recipes[cocktail_lower]['ingredients']
        instructions = cocktail_recipes[cocktail_lower]['instructions']
        return flask.render_template('recipe.html', name = cocktail,
                                     ingredients = ingredients,
                                     instructions = instructions)
    except:
        return redirect(url_for("drink_input"))

@app.route("/pick-your-poison", methods=['GET', 'POST'])
def pick_your_poison():
    try:
        global cocktail
        cocktail = request.form['Cocktail']
        cocktail_lower = cocktail.lower()
        if cocktail_lower not in cocktail_names:
            best_match = 0
            best_cocktails = []
            for name in cocktail_names:
                FuzzyMatch = fuzz.partial_ratio(name,cocktail_lower)
                if FuzzyMatch >= best_match:
                    best_cocktails.append(name)
                    best_match = FuzzyMatch
            best_match = 0
            best_cocktail = []
            for match in best_cocktails:
                FuzzyMatch = fuzz.ratio(match,cocktail_lower)
                if FuzzyMatch > best_match:
                    best_cocktail = match
                    best_match = FuzzyMatch
            cocktail_lower = best_cocktail
            cocktail = cocktail_lower.capitalize()
        cocktail_close = random.choice(cocktail_recommender[cocktail_lower])
        cocktail_close_lower = cocktail_close.lower()
        ingredients = cocktail_recipes[cocktail_close_lower]['ingredients']
        instructions = cocktail_recipes[cocktail_close_lower]['instructions']
        return flask.render_template('recommend.html', name = cocktail_close,
                                     ingredients = ingredients,
                                     instructions = instructions,
                                     original_cocktail = cocktail)
    except:
        return redirect(url_for("drink_input"))


@app.route("/pick-your-poison-again", methods=['GET', 'POST'])
def pick_your_poison_again():
    cocktail_lower = cocktail.lower()
    cocktail_close = random.choice(cocktail_recommender[cocktail_lower])
    cocktail_close_lower = cocktail_close.lower()
    ingredients = cocktail_recipes[cocktail_close_lower]['ingredients']
    instructions = cocktail_recipes[cocktail_close_lower]['instructions']
    return flask.render_template('recommend.html', name = cocktail_close,
                                 ingredients = ingredients,
                                 instructions = instructions,
                                 original_cocktail = cocktail)

    
@app.route("/surprise-me",methods = ['GET', 'POST'])
def surprise_me():
    cocktail_random = random.choice(cocktail_names)
    ingredients = cocktail_recipes[cocktail_random]['ingredients']
    instructions = cocktail_recipes[cocktail_random]['instructions']
    return flask.render_template('surprise.html',
                                 name = cocktail_random.capitalize(),
                                 ingredients = ingredients,
                                 instructions = instructions)

# Start the server, continuously listen to requests.
# We'll have a running web app!

# For local development:
if __name__ == '__main__':
    app.run()

# For public web serving:
# app.run(host='0.0.0.0')
