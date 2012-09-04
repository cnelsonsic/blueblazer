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
