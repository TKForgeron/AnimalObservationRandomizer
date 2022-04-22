import random
import numpy as np
import pandas as pd
from helpers.sterres_globals import *


def invalid_animal_to_na(animal_string):
    if not animal_string in ANIMALS:
        animal_string = np.nan
    return animal_string


def invalid_timeslot_to_na(timeslot_string):
    corrected_timeslots = [x.split(".")[1] for x in TIMESLOTS]
    if not timeslot_string in corrected_timeslots:
        timeslot_string = np.nan
    return timeslot_string

def min_to_sec(min):
    sec = min
    partial = str(min).split(".", 1)
    try:
        if len(partial) > 1:
            sec = int(partial[0]) * 60 + int(partial[1])
        elif partial[0] != "nan":
            sec = int(partial[0]) * 60
        elif sec == "nan":
            sec = None
    except:
        sec = None

    return sec


def to_upper_but_fillna(s):
    if s == "nan":  # or not s:
        s = None
    else:
        s = s.upper()
    return s


def add_timeslot_index(unindexed_timeslot):
    for i, timeslot in enumerate(TIMESLOTS):
        if unindexed_timeslot in timeslot:
            index_to_add = str(i + 1)
            indexed_timeslot = index_to_add + "." + unindexed_timeslot
            return indexed_timeslot
    return unindexed_timeslot


def calc_new_schedule(
    observations: pd.DataFrame, original_schedule: pd.DataFrame
) -> pd.DataFrame:
    # aggregate Time per Animal/Timeslot combination
    observations = (
        observations.groupby(["Animal", "Timeslot"])["Time"].sum().reset_index()
    )
    # check if there exist duplicate ANIMAL/TIMESLOT combinations, if so, aggregate their TIME REMAINING
    unique_rows_old_schedule = original_schedule[
        ["ANIMAL", "TIMESLOT"]
    ].drop_duplicates()
    if len(unique_rows_old_schedule) < len(original_schedule):
        print(
            f"Duplicate ANIMAL/TIMESLOT combinations were found in {CSV_SCHEDULE_NAME} and merged"
        )
        # df = pd.DataFrame(, columns=["ANIMAL","TIMESLOT",'TIME REMAINING'])
        original_schedule["TIME REMAINING"] = (
            original_schedule["TIME REMAINING"].astype(float).astype(int)
        )
        original_schedule = (
            original_schedule.groupby(["ANIMAL", "TIMESLOT"])["TIME REMAINING"]
            .sum()
            .reset_index()
        )

    original_schedule = original_schedule.to_numpy()
    observations = observations.to_numpy()

    for obs in observations:
        # print(old_schedule)
        idx = []
        idx.append(
            np.where(np.all(obs[:2] == original_schedule[:, :2], axis=1))
        )  # append indexes in old_schedule where obs (animal/timeslot combination) is found
        # print(idx, '\n', old_schedule)
        old_schedule_idxs = idx[0][0]
        time_remaining_list = []
        for i in old_schedule_idxs:
            time_remaining_list.append(
                original_schedule[i, 2]
            )  # time remaining is found at index 2 or -1
        idxs_of_lowest_time_rem = [
            i
            for i, j in enumerate(time_remaining_list)
            if j == min(time_remaining_list)
        ]
        idx_of_lowest_time_rem = idxs_of_lowest_time_rem[0]
        idx_of_lowest_time_rem = old_schedule_idxs[idx_of_lowest_time_rem]
        row_to_be_subtracted_from = original_schedule[
            idx_of_lowest_time_rem
        ]  # row with lowest time remaining
        new_time_remaining = row_to_be_subtracted_from[-1] - obs[-1]
        if new_time_remaining > 2 * 60:
            original_schedule[idx_of_lowest_time_rem, -1] = new_time_remaining
        elif (
            new_time_remaining == new_time_remaining
        ):  # check if new_time_remaining is nan
            # print(
            #     f"removed {original_schedule[idx_of_lowest_time_rem,:]}, as there is less than 2 minutes of observations time left"
            # )
            # original_schedule = np.delete(
            #     original_schedule, idx_of_lowest_time_rem, axis=0
            # )  # delete row if time remaining is lower than 2 minutes

            original_schedule[idx_of_lowest_time_rem, -1] = 0


    new_schedule = pd.DataFrame(original_schedule, columns=COLUMN_HEADERS)

    return new_schedule


def get_indexes_for_timeslots():
    xs = []
    for animal_index in range(len(ANIMALS)):
        xs.append((animal_index) * len(TIMESLOTS))

    idxs = []
    for y in range(len(TIMESLOTS)):
        shuffled_idxs_for_this_timeslot = list(map(lambda x: x + y, xs))
        random.shuffle(shuffled_idxs_for_this_timeslot)
        idxs.append(shuffled_idxs_for_this_timeslot)

    res = dict()
    for timeslot, idx in zip(TIMESLOTS, idxs):
        res[timeslot] = idx

    return res

def generate_reordering_indexes(schedule, indexes):
    sorted_schedule = []
    split_residuals = []
    for idx in indexes:
        idx_list = indexes[idx]
        df = pd.DataFrame(columns=COLUMN_HEADERS)
        split_length = int(len(idx_list) / NO_OBS_PER_TIMESLOT)
        split_list = [
            idx_list[i : len(idx_list) : split_length] for i in range(split_length)
        ]  # split idx list into lists s.t. there are sublists with length==NO_OBS_PER_TIMESLOT
        split_residual = [
            x[NO_OBS_PER_TIMESLOT] for x in split_list if len(x) > NO_OBS_PER_TIMESLOT
        ]  # cut off any sublist that is 'one-off' due to split_length being a fractal
        split_list = [
            x[:NO_OBS_PER_TIMESLOT] for x in split_list
        ]  # cut off any sublist that is 'one-off' due to split_length being a fractal
        sorted_schedule.append(split_list)
        split_residuals += split_residual
        # sorted_schedule += split_list
        for i in idx_list[:NO_OBS_PER_TIMESLOT]:
            x = schedule.iloc[i, :].to_numpy()

    sorted_schedule = np.array(sorted_schedule)
    reshaped_simpler = np.hstack(sorted_schedule)
    reordering_index = reshaped_simpler.reshape(
        len(indexes) * split_length * NO_OBS_PER_TIMESLOT
    )


    reordering_index_list = reordering_index.tolist()
    reordering_index_list += split_residuals  # add residuals to come to 52 rows s.t. index and schedule_list are equally long
    # schedule_list = schedule_list[:len(reordering_index_list)] #subtract residuals to come to 48 rows s.t. index and schedule_list are equally long
    return reordering_index_list


def reorder(arr, index_list):
    res = []
    for i in index_list:
        res.append(arr[i])
    return np.array(res)

