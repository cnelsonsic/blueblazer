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

import os
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
            raise Exception("Could not read your ingredients file. "
                            "Please create one at {0}".format(filename))

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
    import random

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
