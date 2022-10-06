import copy

import achievements
import json
import pickle
import os

achievement_combos = achievements.win_combo_achievements
card_names = achievements.card_names


class GameData:
    def __init__(self):
        self.current_cards = list()

        self.achievement_cards = copy.deepcopy(achievement_combos)

    def addCards(self, card_pos, card_neg):
        self.current_cards.append(card_pos)
        self.current_cards.append(card_neg)

        # Update achievement matches
        for achievement_name, cards in self.achievement_cards.items():
            for card in [card_pos, card_neg]:
                if card in cards:
                    self.achievement_cards[achievement_name].remove(card)

    def getMatchesCompletion(self, card_options):
        card_matches = {name: 0 for name in card_options}
        card_completion = {name: 0 for name in card_options}

        temp_achievement_cards = copy.deepcopy(self.achievement_cards)
        for achievement_name, cards in temp_achievement_cards.items():
            for card in card_options:
                if card in cards:
                    if card in temp_achievement_cards[achievement_name]:
                        card_matches[card] += 1
                        temp_achievement_cards[achievement_name].remove(card)
                        card_completion[card] = (len(achievement_combos[achievement_name]) - len(
                            temp_achievement_cards[achievement_name])) / len(achievement_combos[achievement_name])

        return card_matches, card_completion

    def bestChoice(self, card_options_1, card_options_2, show_calcs=False):
        choose_option_1 = None

        card_matches_op_1, card_completion_op_1 = self.getMatchesCompletion(card_options_1)
        card_matches_op_2, card_completion_op_2 = self.getMatchesCompletion(card_options_2)

        if show_calcs:
            print("Option 1:", card_matches_op_1, card_completion_op_1)
            print("Option 2:", card_matches_op_2, card_completion_op_2)

        # Get fully complete flags
        complete_in_op_1 = False
        complete_in_op_2 = False
        if 1 in card_completion_op_1.values():
            complete_in_op_1 = True
        if 1 in card_completion_op_2.values():
            complete_in_op_2 = True

        # Evaluate fully complete
        if complete_in_op_1 == complete_in_op_2:  # Tie-break
            # Using average completed
            average_op_1 = sum(card_completion_op_1.values()) / len(card_completion_op_1.values())
            average_op_2 = sum(card_completion_op_2.values()) / len(card_completion_op_2.values())
            if average_op_1 > average_op_2:
                choose_option_1 = True
            elif average_op_1 < average_op_2:
                choose_option_1 = False
            else:  # Tie-break
                # Using the highest matches
                if max(card_matches_op_1.values()) > max(card_matches_op_2.values()):
                    choose_option_1 = True
                elif max(card_matches_op_1.values()) < max(card_matches_op_2.values()):
                    choose_option_1 = False
                else:  # Tie-break
                    # Free for all :)
                    pass
        elif complete_in_op_1 is True:
            choose_option_1 = True
        elif complete_in_op_2 is True:
            choose_option_1 = False

        return choose_option_1
        # return card_matches

    def toDict(self):
        return {
            "current_cards": self.current_cards,
            "achievement_matches": self.achievement_cards,
        }

    def save(self):
        directory = "Game Saves"
        os.makedirs(directory, exist_ok=True)
        files = [f for f in os.listdir(directory) if f.endswith(".pkl")]

        game_number = 1
        file_name = f"game #{game_number}.pkl"
        while file_name in files:
            game_number += 1
            file_name = f"game #{game_number}.pkl"

        file_path = os.path.join(directory, file_name)

        with open(file_path, "wb") as f:
            pickle.dump(self, f)

        with open(file_path.replace(".pkl", ".json"), "w") as f:
            json.dump(self.toDict(), f, indent=4)


# gd = GameData()
# gd.addCards("Pillage", "Revolution")
# bc = gd.bestChoice(["Conscription", "Militia"], ["Assault", "Ruins"])
# print(bc)
# gd.save()
