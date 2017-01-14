# DESCRIPTION: A script that contains the small, miscellaneous functions and
# classes that are used everywhere.

# 50726f6772616d6d696e6720697320627265616b696e67206f66206f6e652062696720696d706f
# 737369626c65207461736b20696e746f207365766572616c207665727920736d616c6c20706f73
# 7369626c65207461736b732e

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~MAIN~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from lib.exceptions import *
from copy import deepcopy


 ####### #     # #     #  #####  ####### ### ####### #     #  #####
 #       #     # ##    # #     #    #     #  #     # ##    # #     #
 #       #     # # #   # #          #     #  #     # # #   # #
 #####   #     # #  #  # #          #     #  #     # #  #  #  #####
 #       #     # #   # # #          #     #  #     # #   # #       #
 #       #     # #    ## #     #    #     #  #     # #    ## #     #
 #        #####  #     #  #####     #    ### ####### #     #  #####


def xor(x, y):
    """An XOR gate for two arguments"""
    if ((x and y) or (not x and not y)):
        return False
    else:
        return True

def xnor(x, y):
    """An XNOR gate for two arguments."""
    return (not xor(x, y))

def onlyone(iterable):
    """Returns true if only one of the items in iterable is true."""
    count = 0
    for ii in iterable:
        if count > 1:
            return False
        elif ii:
            count += 1
            continue
    return True

def convert(indexorcoordinateorvector,
            tocoordinate=False, toindex=False, tovector=False):
    """Makes the input into a coordinate, vector or index, regardless of form.

    This monolithic function basically forces either an index or a
    coordinate into the specified form. This is the translator required to
    calculate possible moves using vector attacks. See docs for more
    information into the algoithims used and why this method is required."""
    # TODO: Flesh out this docsting.
    # Sanity checks.
    assert any([tocoordinate, toindex, tovector]), \
        "Specify the output using the optional arguments."
    assert onlyone([tocoordinate, toindex, tovector]), \
        "The output is only a coordinate, vector or an index, not multiple."

    # Define functions
    def isindex(x):
        return isinstance(x, int)
    def iscoordinate(x):
        return (isinstance(x, (tuple, list)) and len(x) == 2)
    def isvector(x):
        return isinstance(x, Vector)

    # Convert to desired form:
    x = indexorcoordinateorvector  # Shorthand notation.
    if tocoordinate:  # Convert to coordinate.
        if isindex(x):
            return (x/8, x % 8)
        elif isvector(x):
            return x.tupleform()
        elif iscoordinate(x):
            return x
    elif toindex:  # Convert to index.
        if isindex(x):
            return x
        elif isvector(x):
            x = x.tupleform()
            return x[0]*8 + x[1]
        elif iscoordinate(x):
            return x[0]*8 + x[1]
    elif tovector:  # Convert to vector.
        if isindex(x):
            return Vector(x/8, x % 8)
        elif iscoordinate(x):
            return Vector(*x)
        elif isvector(x):
            return x
    else:
        raise TypeError("Passed item is none of the allowed options.")
    # If x isn't a vector, index or coordinate:
    raise TypeError("The item to be converted isn't a valid type.")
    return None

def convertlist(lst, **kwargs):
    """Same call as convert but for a list. Basically, a shortcut call."""
    return map(lambda x: convert(x, **kwargs), lst)

def readablelistof(lst):
    """Prints the list as expected, instead of a jumble of instances.

    This is to be called when dealing with pieces or vectors."""
    string = ''
    for item in lst:
        string += str(item) + ', '
    return '[' + string[:-2] + ']'


 ####### #     #  #####  ####### ######  ####### ### ####### #     #  #####
 #        #   #  #     # #       #     #    #     #  #     # ##    # #     #
 #         # #   #       #       #     #    #     #  #     # # #   # #
 #####      #    #       #####   ######     #     #  #     # #  #  #  #####
 #         # #   #       #       #          #     #  #     # #   # #       #
 #        #   #  #     # #       #          #     #  #     # #    ## #     #
 ####### #     #  #####  ####### #          #    ### ####### #     #  #####


class IllegalMoveError(IndexError):
    """Called if the move is illegal for any reason."""

    def __init__(self):
        IndexError.__init__(self, "The move supplied is not valid.")

class ColourError(TypeError):
    """Raised if the colour specified isn't either white or black."""

    def __init__(self, errormsg=None):
        if errormsg == None:
            errormsg = "The colours of the players are either white or black."
        TypeError.__init__(self, errormsg)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.:.~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
