import numpy as np
import pandas as pd
from my_globals import *
import random


def invalid_animal_to_na(animal_string):
    if not animal_string in APENHEUL_ANIMALS:
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
    if len(partial) > 1:
        sec = int(partial[0]) * 60 + int(partial[1])
    elif partial[0] != "nan":
        sec = int(partial[0]) * 60
    elif sec == "nan":
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
    # print('running calc_new_schedule()...')

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
            print(
                f"removed {original_schedule[idx_of_lowest_time_rem,:]}, as there is less than 2 minutes of observations time left"
            )
            original_schedule = np.delete(
                original_schedule, idx_of_lowest_time_rem, axis=0
            )  # delete row if time remaining is lower than 2 minutes

    new_schedule = pd.DataFrame(original_schedule, columns=COLUMN_HEADERS)

    return new_schedule


def get_indexes_for_timeslots():
    xs = []
    for animal_index in range(len(APENHEUL_ANIMALS)):
        xs.append((animal_index) * len(TIMESLOTS))

    idxs = []
    for y in range(len(TIMESLOTS)):
        shuffled_idxs_for_this_timeslot = list(map(lambda x: x + y, xs))
        # random.seed(RANDOM_SEED)
        random.shuffle(shuffled_idxs_for_this_timeslot)
        idxs.append(shuffled_idxs_for_this_timeslot)

    res = dict()
    for timeslot, idx in zip(TIMESLOTS, idxs):
        res[timeslot] = idx

    return res


def reorder(list, index_list):
    res = []
    for x in index_list:
        res.append(list[x])
    return res


try:
    schedule = pd.read_csv(f"{CSV_INITIAL_SCHEDULE_NAME}", sep=";")
except:
    schedule = pd.read_csv("initial_schedule (backup).csv", sep=";")
true_obs = pd.read_excel(f"{XLSX_TRUE_OBS_NAME}")
true_obs = true_obs.iloc[:, 2:5]
true_obs["Animal"] = true_obs["Animal"].apply(invalid_animal_to_na)
true_obs["Timeslot"] = true_obs["Timeslot"].apply(invalid_timeslot_to_na)
true_obs = true_obs.dropna()
# add index to Timeslot, s.t. "EM" becomes "1.EM" becoming equal to the elements of TIMESLOTS
true_obs["Timeslot"] = true_obs["Timeslot"].apply(add_timeslot_index)
true_obs = true_obs.astype(str)
true_obs["Animal"] = true_obs["Animal"].apply(to_upper_but_fillna)
true_obs["Timeslot"] = true_obs["Timeslot"].apply(to_upper_but_fillna)
true_obs["Time"] = true_obs["Time"].apply(min_to_sec)
true_obs["Time"] = true_obs["Time"].astype(float).astype(int)
true_obs = true_obs.dropna()

# # test_schedule = schedule
# test_schedule = np.array([["AA", "BB", 100], ["CC", "DD", 100]])
# test_schedule = np.insert(test_schedule, 0, ["XX", "XX", 500])
# test_schedule = np.insert(test_schedule, 0, ["AA", "AA", 50])
# test_schedule = test_schedule.reshape(int(test_schedule.shape[0] / 3), 3)
# test_schedule = pd.DataFrame(test_schedule, columns=COLUMN_HEADERS)
# test_schedule.iloc[:, -1] = test_schedule.iloc[:, -1].astype(int)

# # test_observations = true_obs
# test_observations = np.array(["AA", "BB", 10])
# test_observations = np.array(["CC", "DD", 5])
# for _ in range(2):
#     test_observations = np.insert(test_observations, 0, ["XX", "XX", 100])
# test_observations = np.insert(test_observations, 0, ["XX", "XX", 50])
# test_observations = test_observations.reshape(int(test_observations.shape[0] / 3), 3)
# test_observations = pd.DataFrame(
#     test_observations, columns=["Animal", "Timeslot", "Time"]
# )
# test_observations.iloc[:, -1] = test_observations.iloc[:, -1].astype(int)

new_schedule = calc_new_schedule(true_obs, schedule)

# new_schedule = new_schedule.sample(frac=1)
# new_schedule = new_schedule.sort_values(by=['ANIMAL','TIMESLOT', 'TIME REMAINING'])
# new_schedule.to_csv(f"{CSV_SCHEDULE_NAME}", sep=";", index=False)


# # %%
# def get_observation_idxs_for_one_day(indexes_for_timeslots: dict) -> list[int]:
#     observation_order_for_one_day = []
#     for timeslot in indexes_for_timeslots:
#         observations_this_timeslot_today = indexes_for_timeslots[timeslot][:NO_OBS_PER_TIMESLOT]
#         # print(coming_6observations)
#         observation_order_for_one_day += observations_this_timeslot_today
#     return observation_order_for_one_day

# # %%
# observation_order_for_one_day = get_observation_idxs_for_one_day(get_indexes_for_timeslots())

indexes = get_indexes_for_timeslots()

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
        x = new_schedule.iloc[i, :].to_numpy()

sorted_schedule = np.array(sorted_schedule)
reshaped_simpler = np.hstack(sorted_schedule)
reordering_index = reshaped_simpler.reshape(
    len(indexes) * split_length * NO_OBS_PER_TIMESLOT
)


new_schedule_list = new_schedule.to_numpy().tolist()
reordering_index_list = reordering_index.tolist()
reordering_index_list += split_residuals  # add residuals to come to 52 rows s.t. index and schedule_list are equally long
# schedule_list = schedule_list[:len(reordering_index_list)] #subtract residuals to come to 48 rows s.t. index and schedule_list are equally long

new_schedule_list = reorder(new_schedule_list, reordering_index_list)

# remove number in front of timeslot code
for row in new_schedule_list:
    row[1] = row[1].split(".")[1]

print("The first 12 as an example...")
print(pd.DataFrame(new_schedule_list, columns=COLUMN_HEADERS).head(12))

np.savetxt(f"{CSV_SCHEDULE_NAME}", new_schedule_list, delimiter=";", fmt="% s")
