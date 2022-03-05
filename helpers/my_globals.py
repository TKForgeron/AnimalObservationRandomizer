# GLOBALS

RANDOM_SEED = 32
DATA_DIR_NAME = "data"
COLUMN_HEADERS = ["ANIMAL", "TIMESLOT", "TIME REMAINING"]
TIMESLOTS = ["1.EM", "2.LM", "3.EA", "4.LA"]
NO_OBS_PER_TIMESLOT = 3

DIERENRIJK_ANIMALS = [
    "BR",
    "M8",
    "BA",
    "LU",
    "BIC",
    "BO",
    "RU",
    "PI",
    "EP",
    "JO",
    "JE",
    "RE",
    "JAP",
]
GAIAZOO_ANIMALS = [
    "HAS",
    "FR",
    "ZA",
    "JA",
    "FA2",
    "TH",
    "KAM",
    "KL",
    "KD",
    "FAM",
    "FE",
    "KA2",
    "SAL",
    "FAD",
]
APENHEUL_ANIMALS = [
    "KE",
    "FA",
    "MU",
    "NO",
    "SW",
    "SG",
    "SA",
    "HA",
    "BI",
    "KA",
    "TU",
    "AS",
    "TA",
]


def set_global_zoo():
    zoo_name = 0
    while not zoo_name in ["1", "2", "3"]:
        zoo_name = input(
            "Which zoo? (1: Apenheul (default), 2: GaiaZoo, 3: Dierenrijk) \n Use 'Enter' for default \n"
        )
        if zoo_name == "":
            zoo_name = "1"  # 4 days per week, 10 weeks
        else:
            print("Pls choose 1, 2, or 3")

    if zoo_name == "1":
        return "apenheul", APENHEUL_ANIMALS
    elif zoo_name == "2":
        return "gaiazoo", GAIAZOO_ANIMALS
    elif zoo_name == "3":
        return "dierenrijk", DIERENRIJK_ANIMALS
    else:
        print("Something went horribly wrong in set_global_zoo()")


ZOO, ANIMALS = set_global_zoo()
print("OK...", ANIMALS, "\n")


def set_global_total_obs_days():
    days = None
    while not type(days) == int:
        days = input(
            f"How many days in total will you make observations for {ZOO}? (default: 40) \n Use 'Enter' for default \n"
        )
        try:
            days = int(days)
        except:
            if days == "":
                days = 40  # 4 days per week, 10 weeks
            else:
                print("Pls give an integer ")
    return days


TOTAL_OBS_DAYS = set_global_total_obs_days()
print("OK...", TOTAL_OBS_DAYS, "\n")
ONE_OBS_TIME = 1200
TOTAL_COMBS = len(ANIMALS) * len(TIMESLOTS)
TOTAL_OBS = len(TIMESLOTS) * NO_OBS_PER_TIMESLOT * TOTAL_OBS_DAYS
TOTAL_OBS_TIME_PER_COMB = int(TOTAL_OBS / TOTAL_COMBS * ONE_OBS_TIME)

CSV_DAILY_SCHEDULE_NAME = f"daily_schedule_{ZOO}.csv"
CSV_INITIAL_SCHEDULE_NAME = f"{DATA_DIR_NAME}/initial_schedule_{ZOO}.csv"
XLSX_TRUE_OBS_NAME = "animal_observations.xlsx"
