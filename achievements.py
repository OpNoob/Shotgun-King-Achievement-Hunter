import re

with open("Game Data/achievements.txt", "r") as f:
    text = f.read()

achievements_text = text.split("\n\n")

achievements = dict()
for a_text in achievements_text:
    name, description = a_text.split("\n")
    achievements[name] = description

win_combo_achievements = dict()
card_names = set()
skipped_achievements = dict()
for name, description in achievements.items():
    if "Win with " in description:
        card_description = description.replace("Win with ", "")
        if ", " in card_description and " and " in card_description:
            card_names_found = re.split(", | and ", card_description)
            win_combo_achievements[name] = card_names_found

            for card_name in card_names_found:  # Adding to cards
                card_names.add(card_name)
    # Check if was added
    if name not in win_combo_achievements:
        skipped_achievements[name] = description

ACHIEVEMENTS_COMPLETED_PATH = "Game Data/achievements_completed.txt"


def getCompleted():
    with open(ACHIEVEMENTS_COMPLETED_PATH, "r") as f:
        achievements_done_text = f.read()
        achievements_done = set(achievements_done_text.split("\n"))
        return achievements_done


def filterAchievementsDone(achievements_dict: dict, completed: list):
    for achievements_name in completed:
        if achievements_name in achievements_dict:
            del achievements_dict[achievements_name]
    return achievements_dict
