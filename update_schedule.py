import glob
import os
import numpy as np
import pandas as pd
from helpers.my_globals import *
from helpers.helper_generate_initial_schedule import *
from helpers.helper_update_schedule import *

# REMOVE PREVIOUS DAILY_SCHEDULEs
daily_schedules = "_".join(CSV_DAILY_SCHEDULE_NAME.split("_")[:2])
for filename in glob.glob(f"./{daily_schedules}*"):
    os.remove(filename)

# GENERATE INITIAL SCHEDULE
combs = generate_combinations(ANIMALS, TIMESLOTS)
schedule = pd.DataFrame(combs, columns=COLUMN_HEADERS)

# checking if DATA_DIR_NAME exist or not.
if not os.path.exists(DATA_DIR_NAME):

    # if DATA_DIR_NAME is not present then create it.
    os.makedirs(DATA_DIR_NAME)

schedule.to_csv(f"{CSV_INITIAL_SCHEDULE_NAME}", sep=";", index=False)


# UPDATE PART
try:
    schedule = pd.read_csv(f"{CSV_INITIAL_SCHEDULE_NAME}", sep=";")
except:
    schedule = pd.read_csv(f"initial_schedule_{ZOO} (backup).csv", sep=";")
schedule["TIMESLOT"] = schedule["TIMESLOT"].apply(add_timeslot_index)
true_obs = pd.read_excel(f"{XLSX_TRUE_OBS_NAME}", sheet_name=ZOO)
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

new_schedule = calc_new_schedule(true_obs, schedule)

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

np.savetxt(f"{CSV_DAILY_SCHEDULE_NAME}", new_schedule_list, delimiter=";", fmt="% s")

print("The first 12 as an example...")
print(pd.DataFrame(new_schedule_list, columns=COLUMN_HEADERS).head(12))
