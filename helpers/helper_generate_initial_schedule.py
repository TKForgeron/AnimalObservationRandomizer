from helpers.sterres_globals import *


def generate_combinations(animal_names, timeslots):

    combs = []
    for name in animal_names:
        combs += [
            (name, timeslot.split(".")[1], TOTAL_OBS_TIME_PER_COMB)
            for timeslot in timeslots
        ]

    return combs
