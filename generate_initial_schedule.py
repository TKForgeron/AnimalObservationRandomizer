import random
import pandas as pd
from my_globals import *


def generate_combinations(animal_names, timeslots):

    combs = []
    for name in animal_names:
        combs += list(
            zip(
                [name] * len(timeslots * NO_OBS_PER_TIMESLOT),
                timeslots * NO_OBS_PER_TIMESLOT,
            )
        )
    combs *= NO_OBS_PER_TIMESLOT

    return combs


def sort_per_NO_OBS_PER_TIMESLOT(full_schedule: pd.DataFrame) -> pd.DataFrame:

    np_starting_schedule = full_schedule.to_numpy()
    full_schedule = full_schedule.sort_values(
        by=["TIMESLOT", "TIME REMAINING"], ascending=False
    )
    timeslot_indexes = []
    looping_condition = (
        lambda: full_schedule.loc[full_schedule["TIME REMAINING"] == 1200].shape[0]
        >= len(TIMESLOTS) * NO_OBS_PER_TIMESLOT
    )

    while looping_condition():
        for timeslot in TIMESLOTS:
            x = full_schedule.loc[full_schedule["TIMESLOT"] == timeslot]
            z = x.iloc[:NO_OBS_PER_TIMESLOT]
            zindex = z.index
            full_schedule = full_schedule.drop(index=zindex)
            zindex = zindex.to_list()
            timeslot_indexes.append(zindex)

    sorted_schedule = []
    for idxs in timeslot_indexes:
        for idx in idxs:
            sorted_schedule.append((np_starting_schedule[idx].tolist()))
    return pd.DataFrame(sorted_schedule, columns=COLUMN_HEADERS)


# GENERATE INITIAL SCHEDULE
combs = generate_combinations(APENHEUL_ANIMALS, TIMESLOTS)
random.seed(RANDOM_SEED)
random.shuffle(combs)
initial_schedule = pd.DataFrame(combs, columns=["ANIMAL", "TIMESLOT"])
initial_schedule["TIME REMAINING"] = [1200] * initial_schedule.shape[0]


schedule = sort_per_NO_OBS_PER_TIMESLOT(initial_schedule)
schedule["TIME REMAINING"] = schedule["TIME REMAINING"].astype(int)
schedule = (
    schedule.groupby(["ANIMAL", "TIMESLOT"])["TIME REMAINING"].sum().reset_index()
)

schedule.to_csv(f"{CSV_INITIAL_SCHEDULE_NAME}", sep=";", index=False)
# print(schedule)
