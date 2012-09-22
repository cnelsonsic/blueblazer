#!/usr/bin/env python
'''A module to generate a random mixed drink from a given set of ingredients.
Expects an 'ingredients.yaml' file.

It should be in the following format:
    ---
    ingredients:
        - name: Vodka
          abv: 40%
        - name: Sour Apple Pucker schnapps
          proof: 30

'''

from collections import defaultdict
import os
import random
import yaml
import xdg.BaseDirectory

def combine(ingredients):
    ''' A function to combine two measures of drink.

    If we add equal parts vodka and soda, we get a drink with 20% ABV.
    >>> combine(((10, .40), (10, .0)))
    (20, 0.2)

    If we add four parts vodka, and two parts soda, we get 26.7%ABV.
    >>> combine(((40, .40), (20, .0)))
    (60, 0.267)

    You can do multiple things too (Vodka, Mixer, and lemon juice):
    >>> combine(((20, .4), (20, .2), (20, 0)))
    (60, 0.2)

    Or really complex drinks (IBA Bloody Mary):
    >>> combine(((45, .4), (90, 0), (15, 0), (9, 0)))
    (159, 0.113)
    '''
    final_amount, final_percentage = 0, 0

    for ingredient in ingredients:
        amount = ingredient[0]
        percentage = ingredient[1]

        # Multiply the percentage by the amount of liquid.
        final = final_amount * final_percentage
        second = amount * percentage

        # Add them
        combined = final + second

        # Then divide by the amount of liquid.
        final_amount += amount
        if final_amount < 0:
            continue
        combined /= final_amount
        final_percentage = round(combined, 3)
    return (final_amount, final_percentage)

def read_ingredients(filename=None, contents=None):
    '''Read the user's ingredients file and return an ingredients list.
    >>> sample_contents = \'\'\'
    ... ---
    ... ingredients:
    ...     - name: Vodka
    ...       abv: 40%
    ...     - name: Sour Apple Pucker schnapps
    ...       proof: 30
    ...     - name: Captain Jack's Spiced Rum
    ...       proof: 0.4
    ... \'\'\'
    >>> read_ingredients(contents=sample_contents)
    [{'name': 'Vodka', 'abv': 0.4}, {'name': 'Sour Apple Pucker schnapps', 'abv': 0.15}, {'name': "Captain Jack's Spiced Rum", 'abv': 0.2}]
    '''
    if not contents:
        if filename is None:
            filename = os.path.join(xdg.BaseDirectory.xdg_data_home,
                                    'blueblazer',
                                    'ingredients.yaml')
        try:
            with open(filename, 'r') as f:
                contents = f.read()
        except IOError:
            os.makedirs(os.path.dirname(filename))
            with open(filename, "w") as f:
                sample_ingredients = '\n'.join(("---",
                    "ingredients:",
                    "    - name: Vodka",
                    "    abv: 40%",
                    "    - name: Water",
                    "    proof: 0",))
                f.write(sample_ingredients)
            raise Exception("Could not read your ingredients file. "
                            "Created a blank one at {0}".format(filename))

    ingredients = yaml.load(contents).get('ingredients', [])
    for ingredient in ingredients:
        # Convert proofs to ABV.
        try:
            ingredient['abv'] = str(ingredient.pop('proof')/2.0)
        except (KeyError, AttributeError):
            # Didn't have a proof.
            pass

        # Clean up percentages
        abv = float(ingredient['abv'].strip().strip("%"))
        if abv > .99:
            # Scale stuff like "40" down to "0.4", and leave "0.4" alone.
            abv *= 0.01
        ingredient['abv'] = abv

    return ingredients

def random_ratio(rounding=1, starting_seed=None):
    '''Gets a random 3-part ratio that should give us a decent cocktail.
    starting_seed is an optional parameter, which you can use to get the same
    ratio every time.
    I use it in these examples to get the same output every time.

    >>> random_ratio(starting_seed=121412)
    [0.7, 0.2, 0.1]

    >>> random_ratio(rounding=4, starting_seed=121412)
    [0.6698, 0.2037, 0.1265]
    '''

    if starting_seed:
        random.seed(starting_seed)

    total = 0
    while round(total, rounding) != 1.0:
        first = round(random.random(), rounding)
        second = round(random.uniform(first, 1.0), rounding)
        third = round(1.0-second-first, rounding)
        if third < 0:
            continue
        total = sum((first, second, third))
    return sorted((first, second, third), reverse=True)

# Some set amounts.
COCKTAIL = 70
HIGHBALL = 150
OLD_FASHIONED = 40

def random_drink(amount=COCKTAIL, ingredients=None, seed=None):
    '''Generate a random drink of a given amount.

    Presuming the ingredients listing looks something like this:
    >>> ingredients = [{'name': 'Rum', 'abv': 0.4},
    ...                {'name': 'Sunny D', 'abv': 0}]

    We'll get a delicious cocktail with 14mL of Sunny D, and 56mL of Rum. Yum yum.
    >>> random_drink(ingredients=ingredients, seed=12345) # The seed is for testing only.
    {'Sunny D': 14.0, 'Rum': 56.0}
    '''
    ratio = random_ratio(starting_seed=seed)

    if not ingredients:
        # Ingredients were not passed in, so load from the file.
        ingredients = read_ingredients()

    if seed:
        # Passed in a seed, use it for consistent results.
        random.seed(seed)

    # Fill out our drink's ingredients.
    drink_ingredients = defaultdict(int)
    for i in ratio:
        thisdrink = random.choice(ingredients).get('name', "Water")
        drink_ingredients[thisdrink] += i*amount

    return dict(drink_ingredients)

def format_recipe(drink, ingredients=None, seed=None):
    '''Formats a given recipe according to the information in the ingredients.
    It guesses how to prepare a given drink based on the ingredients involved.

    It can take a list of dicts of ingredients and their ABV percentages.
    >>> ingredients = [{'name': 'Rum', 'abv':  .4}, {'name': 'Cola', 'abv': 0}]

    For example, straight spirits might be shaken or stirred, depending on the
    phases of the moon.
    >>> format_recipe(drink={'Rum': 70}, ingredients=ingredients, seed=1234)
    70mL (2.37oz) Rum.
    Total of 70mL (2.37oz) @ 40% ABV
    Pour ingredients into shaker with ice.
    Shake well.
    Strain into cocktail glass filled with ice.

    Note the seed, which is not normally passed when ran normally.
    >>> format_recipe(drink={'Rum': 40, 'Cola': 30}, ingredients=ingredients, seed=12345)
    30mL (1.01oz) Cola.
    40mL (1.35oz) Rum.
    Total of 70mL (2.37oz) @ 23% ABV
    Pour ingredients into cocktail glass and stir.
    '''
    if seed:
        random.seed(seed)

    if not ingredients:
        ingredients = read_ingredients()

    for ingrname, amount in drink.iteritems():
        print "{0}mL ({1:0.2f}oz) {2}.".format(amount, amount/29.5735, ingrname)

    # Get the combined amount and abv.
    amt_abv = []
    for ingrname, amount in drink.iteritems():
        for ingr in ingredients:
            if ingr['name'] == ingrname:
                abv = ingr['abv']
                amt_abv.append((amount, abv))
                break # Found the one, don't need to look further
    total_amount, total_abv = combine(amt_abv)
    print "Total of {0}mL ({1:0.2f}oz) @ {2:.0f}% ABV".format(total_amount, total_amount/29.5735, total_abv*100)

    # Fall through and set the appropriate glass type.
    total_amount = sum(drink.values())
    glass = "bucket"
    if total_amount <= 150:
        glass = "highball"
    if total_amount <= 70:
        glass = "cocktail"
    if total_amount <= 40:
        glass = "old fashioned"

    # Shaken or stirred?
    mix_method = random.choice(('stir', 'shake'))
    if mix_method == 'stir':
        print "Pour ingredients into {glass} glass{ice} and stir{briskly}.".format(briskly=random.choice(("", " briskly", " gently")), glass=glass, ice=random.choice((" with ice", "")))
    elif mix_method == 'shake':
        print "Pour ingredients into shaker{ice}.".format(ice=random.choice(("", " with ice", " with ice", " with ice")))
        print "Shake {method}.".format(method=random.choice(("well", "briskly", "until painfully cold", "gently")))
        print "Strain into {glass} glass{ice}.".format(glass=glass, ice=random.choice(("", " filled with ice")))

# TODO: Function to evolve drinks based on given ingredients.
# TODO: Add support to the yaml for "shakeable: no" to prevent shaking soda.

if __name__ == "__main__":
    format_recipe(random_drink())
