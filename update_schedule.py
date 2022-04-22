import glob
import os
import numpy as np
import pandas as pd
from helpers.sterres_globals import *
from helpers.helper_generate_initial_schedule import *
from helpers.helper_update_schedule import *

# REMOVE PREVIOUS DAILY_SCHEDULEs
daily_schedules = "_".join(CSV_DAILY_SCHEDULE_NAME.split("_")[:2])
for filename in glob.glob(f"./{daily_schedules}*"):
    os.remove(filename)

# GENERATE INITIAL SCHEDULE
combs = generate_combinations(ANIMALS, TIMESLOTS)
schedule = pd.DataFrame(combs, columns=COLUMN_HEADERS)

# # checking if DATA_DIR_NAME exist or not.
# if not os.path.exists(DATA_DIR_NAME):

#     # if DATA_DIR_NAME is not present then create it.
#     os.makedirs(DATA_DIR_NAME)

# try:
#     schedule.to_csv(f"{CSV_INITIAL_SCHEDULE_NAME}", sep=";", index=False)
# except Exception as e:
#     print(f'Writing to {CSV_INITIAL_SCHEDULE_NAME} not succeeded due to: ')
#     print(e)


# UPDATE PART

# import
# try:
#     schedule = pd.read_csv(f"{CSV_INITIAL_SCHEDULE_NAME}", sep=";")
# except:
#     schedule = pd.read_csv(f"initial_schedule_{ZOO} (backup).csv", sep=";")

# clean
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
true_obs = true_obs.dropna()
true_obs["Time"] = true_obs["Time"].astype(float).astype(int)
true_obs = true_obs.dropna()

# manipulate
new_schedule = calc_new_schedule(true_obs, schedule)
indexes = get_indexes_for_timeslots()
reordering_index_list = generate_reordering_indexes(new_schedule, indexes)
new_schedule = new_schedule.to_numpy()
new_schedule = reorder(new_schedule, reordering_index_list)

# clean
# remove number in front of timeslot code
for row in new_schedule:
    row[1] = row[1].split(".")[1]

# repair
# remove entries where TIME REMAINING == 0
idx_to_delete = []
for x,i in zip(new_schedule,range(0,new_schedule.shape[0])):
    if x[2] < 2 * 60:
        idx_to_delete.append(i)
new_schedule = np.delete(new_schedule, idx_to_delete, 0)

# export
np.savetxt(f"{CSV_DAILY_SCHEDULE_NAME}", new_schedule, delimiter=";", fmt="% s")

# demonstrate
print("The first 12 as an example...")
print(pd.DataFrame(new_schedule, columns=COLUMN_HEADERS).head(12))
