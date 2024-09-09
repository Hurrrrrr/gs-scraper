from typing import Set, List, Optional

class Appellation:
    def __init__(self, name):
        self.name = name
        self.aliases = aliases
        self.classification = classification    # AOC, DOCG, etc
        self.country = country
        self.region = region
        self.subregion = subregion
        self.styles = styles
        self.year_established = year_established

class Style(Appellation):
    def __init__(self):
        self.wine_type = wine_type  # white, red, etc.
        self.grapes_min = grapes_min    # k-v pair: chard: 85
        self.grapes_max = grapes_max
        self.num_grapes
        self.min_pa = min_pa    # potential alcohol
        self.min_rs = min_rs
        self.max_rs = max_rs
        self.harvesting = harvesting    # should this be bool or list of strings?
        self.chapitalization = chapitalization  # bool
        self.training = training    # single guyot, etc.
        self.max_yield = max_yield  # hl/ha
        self.elevage = elevage
        self.year_established = year_established    # if different than Appellation

        self.fermentation = fermentation    # traditional, charmat
        self.lees = lees    # months on lees
        self.pressure   # atmospheres of pressure

        self.rose = rose    # saignee, blending, maceration

        self.botrytis = botrytis    # bool
        self.min_aa = min_aa    # acquired alcohol

