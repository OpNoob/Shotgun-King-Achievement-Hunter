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
for name, description in achievements.items():
    if "Win with " in description:
        card_description = description.replace("Win with ", "")
        if ", " in card_description and " and " in card_description:
            card_names_found = re.split(", | and ", card_description)
            win_combo_achievements[name] = card_names_found
            for card_name in card_names_found:
                card_names.add(card_name)


with open("Game Data/achievements_completed.txt", "r") as f:
    achievements_done_text = f.read()
    achievements_done = set(achievements_done_text.split("\n"))

for name in achievements_done:
    if name in win_combo_achievements:
        del win_combo_achievements[name]
