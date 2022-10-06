from PIL import Image
import PySimpleGUI as sg
import PIL.Image
import io
import base64
import queue
import threading
import time

from search_cards import *


# GUI
def resize_image(image_path, resize=None):  # image_path: "C:User/Image/img.jpg"
    if isinstance(image_path, str):
        img = PIL.Image.open(image_path)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(image_path)))
        except Exception as e:
            data_bytes_io = io.BytesIO(image_path)
            img = PIL.Image.open(data_bytes_io)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height / cur_height, new_width / cur_width)
        img = img.resize((int(cur_width * scale), int(cur_height * scale)), PIL.Image.Resampling.LANCZOS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    # with open("test.png", "wb") as f:
    #     img.save(f, format="PNG")
    del img
    return bio.getvalue()


def main():
    # Functions
    def getLength(string_name):
        if string_name is None:
            return len("None")
        else:
            return len(string_name)

    max_string_length = len(max(list(files.keys()), key=getLength))

    # Global variable
    ALWAYS_RUN = False  # Always get screen input flag
    RUN_ACTIVE_ONLY = False  # Runs extraction of window active only flag
    CURRENT_DATA = (
        [None for i in range(10)], [None for i in range(10)], [None for i in range(2)], [None for i in range(2)])

    # Keys
    IMAGE_TOP_1_K = "-image top 1-"
    IMAGE_TOP_2_K = "-image top 2-"
    IMAGE_BOTTOM_1_K = "-image bottom 1-"
    IMAGE_BOTTOM_2_K = "-image bottom 2-"
    TEXT_TOP_1_K = "-text top 1-"
    TEXT_TOP_2_K = "-text top 2-"
    TEXT_BOTTOM_1_K = "-text bottom 1-"
    TEXT_BOTTOM_2_K = "-text bottom 2-"
    IMAGE_CHOICE_TOP_K = "-image choice top-"
    IMAGE_CHOICE_BOTTOM_K = "-image choice bottom-"
    IMAGE_BUFFS_K = "-image buff ?-"
    # TEXT_BUFFS_K = "-text buff ?-"
    IMAGE_NERFS_K = "-image nerfs ?-"
    # TEXT_NERFS_K = "-text nerfs ?-"
    RES_TYPE_K = "-res type-"
    CLEAR_K = "-clear-"
    RESET_K = "-reset-"
    ALWAYS_RUN_K = "-always run-"
    RUN_ACTIVE_ONLY_K = "-run active only-"

    # GUI options
    TEXT_SIZE = (max_string_length, 1)
    IMAGE_SIZE = (58, 42)
    MARK_GOOD_BAD_IMAGE_SIZE = (40, 40)

    # Calculate all data images
    files_image_data = {n: resize_image(p, resize=IMAGE_SIZE) for n, p in files.items()}
    files_image_data_choice = {n: resize_image(p, resize=(116, 84)) for n, p in files.items()}

    # Loading images
    BLANK_IMAGE_DATA = resize_image(files[None], resize=IMAGE_SIZE)
    CHECK_IMAGE_DATA = resize_image("Game Data/GUI/check.png", resize=MARK_GOOD_BAD_IMAGE_SIZE)
    CROSS_IMAGE_DATA = resize_image("Game Data/GUI/cross.png", resize=MARK_GOOD_BAD_IMAGE_SIZE)
    WAITING_IMAGE_DATA = resize_image("Game Data/GUI/waiting.png", resize=MARK_GOOD_BAD_IMAGE_SIZE)

    # Paths
    ICON_PATH = "Game Data/GUI/icon.ico"

    # Functions
    def getKeyFromIndex(generic_key: str, index: int, default_replace='?'):
        return generic_key.replace(default_replace, str(index))

    def getImageList(image_key_names, default_image_data=BLANK_IMAGE_DATA):
        """
        Get list of cards in pysimplgui elements

        :param image_key_names: Must include '?' to include index
        :return: List of elements (for the cards)
        """

        # assert '?' in text_key_name
        assert '?' in image_key_names

        elem_list = list()
        for index in range(10):
            # key_text = getKeyFromIndex(text_key_name, index)
            key_image = getKeyFromIndex(image_key_names, index)

            current_elem = sg.Frame("", [[sg.Button(image_data=BLANK_IMAGE_DATA, key=key_image, tooltip="None")]],
                                    border_width=0,
                                    title_location=sg.TITLE_LOCATION_TOP)
            elem_list.append(current_elem)
        return elem_list

    def updateImages(generic_image_key, card_names: list):
        for index, card in enumerate(card_names):
            key_image = getKeyFromIndex(generic_image_key, index)

            image_data = files_image_data[card]
            window[key_image].update(image_data=image_data)
            window[key_image].TooltipObject.text = str(card)

    def updateChoiceImages(options_1, options_2):
        window[IMAGE_TOP_1_K].update(image_data=files_image_data[options_1[0]])
        window[IMAGE_TOP_2_K].update(image_data=files_image_data[options_1[1]])
        window[IMAGE_BOTTOM_1_K].update(image_data=files_image_data[options_2[0]])
        window[IMAGE_BOTTOM_2_K].update(image_data=files_image_data[options_2[1]])
        # Option tooltips
        window[IMAGE_TOP_1_K].TooltipObject.text = str(options_1[0])
        window[IMAGE_TOP_2_K].TooltipObject.text = str(options_1[1])
        window[IMAGE_BOTTOM_1_K].TooltipObject.text = str(options_2[0])
        window[IMAGE_BOTTOM_2_K].TooltipObject.text = str(options_2[1])
        # Option Texts
        window[TEXT_TOP_1_K].update(str(options_1[0]))
        window[TEXT_TOP_2_K].update(str(options_1[1]))
        window[TEXT_BOTTOM_1_K].update(str(options_2[0]))
        window[TEXT_BOTTOM_2_K].update(str(options_2[1]))

    def updateMarkImages(choose_op_1):
        if choose_op_1 is True:
            window[IMAGE_CHOICE_TOP_K].update(data=CHECK_IMAGE_DATA)
            window[IMAGE_CHOICE_BOTTOM_K].update(data=CROSS_IMAGE_DATA)
        elif choose_op_1 is False:
            window[IMAGE_CHOICE_TOP_K].update(data=CROSS_IMAGE_DATA)
            window[IMAGE_CHOICE_BOTTOM_K].update(data=CHECK_IMAGE_DATA)
        else:
            window[IMAGE_CHOICE_TOP_K].update(data=CHECK_IMAGE_DATA)
            window[IMAGE_CHOICE_BOTTOM_K].update(data=CHECK_IMAGE_DATA)

    def clear():
        updateChoiceImages([None, None], [None, None])
        updateImages(IMAGE_BUFFS_K, [None for i in range(10)])
        updateImages(IMAGE_NERFS_K, [None for i in range(10)])
        window[IMAGE_CHOICE_TOP_K].update(data=WAITING_IMAGE_DATA)
        window[IMAGE_CHOICE_BOTTOM_K].update(data=WAITING_IMAGE_DATA)
        # Resetting CURRENT_DATA
        for section in CURRENT_DATA:
            for i in range(len(section)):
                section[i] = None

    def chooseCardsEvent(evnt, current_data):
        print(event)
        # Getting current card from tooltip (assumes it is always there)
        if not hasattr(window[evnt], 'TooltipObject'):
            return False
        if not hasattr(window[evnt].TooltipObject, 'text'):
            return False

        current_card = window[evnt].TooltipObject.text
        if current_card == "None":
            current_card = None

        choice = None
        buff = None
        top = None

        if evnt == IMAGE_TOP_1_K:
            choice = True
            buff = True
            top = True
        elif evnt == IMAGE_TOP_2_K:
            choice = True
            buff = False
            top = True
        elif evnt == IMAGE_BOTTOM_1_K:
            choice = True
            buff = True
            top = False
        elif evnt == IMAGE_BOTTOM_2_K:
            choice = True
            buff = False
            top = False
        elif "buff" in evnt:
            choice = False
            buff = True
        elif "nerf" in evnt:
            choice = False
            buff = False

        if choice is None and buff is None:
            return False
        else:
            if buff:
                title = "Positive (Buff) Card chooser"
                cards = cards_pos
            else:
                title = "Negative (Nerf) Card chooser"
                cards = cards_neg
            if choice:
                pass
            else:
                cards = [None] + cards

            card = chooseCards(title, cards, current_card)

            # Loading the last data found/modified
            card_found_buffs, card_found_nerfs, options_1, options_2 = current_data

            if choice:
                if buff:
                    if top is True:
                        options_1[0] = card
                    elif top is False:
                        options_2[0] = card
                else:
                    if top is True:
                        options_1[1] = card
                    elif top is False:
                        options_2[1] = card
            else:
                # Get partitions
                if buff:
                    partitions = IMAGE_BUFFS_K.partition("?")
                else:
                    partitions = IMAGE_NERFS_K.partition("?")
                index_str = event.replace(partitions[0], "").replace(partitions[2], "")
                index = int(index_str)
                if buff:
                    card_found_buffs[index] = card
                else:
                    card_found_nerfs[index] = card

            calculate(card_found_buffs, card_found_nerfs, options_1, options_2)
            return True

    def chooseCards(title, cards, current_card, num_cols=5, image_size=(116, 84)):
        list_buttons = list()
        for card in cards:
            if card == current_card:
                border_color = "green"
            else:
                border_color = sg.DEFAULT_BUTTON_COLOR
            button_element = sg.Button(image_data=files_image_data_choice[card], key=str(card), tooltip=str(card),
                                       border_width=5,
                                       button_color=border_color)
            list_buttons.append(button_element)

        num_rows = round(len(list_buttons) / num_cols)
        split_buttons = [list_buttons[i * num_cols:(i + 1) * num_cols] for i in range(num_rows)]
        column_layout = sg.Column(split_buttons, scrollable=True, vertical_scroll_only=True)

        window_chooser = sg.Window(title, [[column_layout]], icon=ICON_PATH)  # , size=(500, 150)

        while True:  # Event Loop
            ev, vals = window_chooser.Read()
            if ev in (None, 'Exit'):
                chosen_card = current_card
                break
            else:
                chosen_card = ev
                break

        if chosen_card == "None":
            chosen_card = None

        window_chooser.Close()
        return chosen_card

    def calculate(card_found_buffs, card_found_nerfs, options_1, options_2):
        game.current_cards = card_found_buffs + card_found_nerfs
        choose_option_1 = game.bestChoice(options_1, options_2)

        # Update options
        updateChoiceImages(options_1, options_2)

        # Update choices
        updateMarkImages(choose_option_1)

        # Update owned cards
        updateImages(IMAGE_BUFFS_K, card_found_buffs)
        updateImages(IMAGE_NERFS_K, card_found_nerfs)

    def getCurrentData():
        resolution_type = values[RES_TYPE_K]
        if resolution_type == "Default":
            resolution_type = None

        window.disable()

        data_queue = queue.Queue()
        thread_current = threading.Thread(target=extractCards, args=(False, resolution_type, data_queue))
        thread_current.start()

        # Animate until thread finishes
        while thread_current.is_alive():
            sg.popup_animated(image_source=sg.DEFAULT_BASE64_LOADING_GIF, grab_anywhere=False,
                              time_between_frames=50, keep_on_top=True)
        sg.popup_animated(None)

        thread_current.join()

        data = data_queue.get_nowait()

        # Update CURRENT_DATA correctly
        for i in range(len(data)):
            for j in range(len(data[i])):
                CURRENT_DATA[i][j] = data[i][j]

        calculate(*CURRENT_DATA)

        window.enable()

    layout = [
        [
            sg.vtop([
                sg.Column([
                    [
                        sg.Push(),
                        sg.Button("Run", size=(20, 3)),
                        sg.Push(),
                    ],
                    [
                        sg.Push(),
                        sg.Frame("Options", [
                            [
                                sg.Frame("Choice 1 (Top)", [
                                    [
                                        sg.Frame("", [
                                            [sg.Button(image_data=BLANK_IMAGE_DATA, key=IMAGE_TOP_1_K, tooltip="None"),
                                             sg.Text("None", size=TEXT_SIZE, key=TEXT_TOP_1_K)],
                                            [sg.Button(image_data=BLANK_IMAGE_DATA, key=IMAGE_TOP_2_K, tooltip="None"),
                                             sg.Text("None", size=TEXT_SIZE, key=TEXT_TOP_2_K)],
                                            # [sg.Button(image_data=BLANK_IMAGE_DATA, tooltip="None"),
                                            #  sg.Text("None")],
                                        ], border_width=0),
                                        sg.Image(data=WAITING_IMAGE_DATA, key=IMAGE_CHOICE_TOP_K)
                                    ]

                                ]),
                            ],
                            [
                                sg.Frame("Choice 2 (Bottom)", [
                                    [
                                        sg.Frame("", [
                                            [sg.Button(image_data=BLANK_IMAGE_DATA, key=IMAGE_BOTTOM_1_K,
                                                       tooltip="None"),
                                             sg.Text("None", size=TEXT_SIZE, key=TEXT_BOTTOM_1_K)],
                                            [sg.Button(image_data=BLANK_IMAGE_DATA, key=IMAGE_BOTTOM_2_K,
                                                       tooltip="None"),
                                             sg.Text("None", size=TEXT_SIZE, key=TEXT_BOTTOM_2_K)],
                                        ], border_width=0),
                                        sg.Image(data=WAITING_IMAGE_DATA, key=IMAGE_CHOICE_BOTTOM_K)
                                    ]

                                ]),
                            ],
                        ]),
                        sg.Push(),
                    ],

                    [
                        sg.Frame("Cards Owned", [
                            [sg.Frame("Buffs (Left)", [
                                getImageList(IMAGE_BUFFS_K),
                            ])],
                            [sg.Frame("Nerfs (Right)", [
                                getImageList(IMAGE_NERFS_K),
                            ])],
                        ]),
                    ],
                ]),
                sg.Column([
                    [
                        sg.Button("Clear (Reset)", expand_x=True, key=CLEAR_K),
                    ],
                    [
                        sg.Button("Hard Reset (closes and reopens window)", expand_x=True, key=RESET_K),
                    ],
                    [
                        sg.Text("Resolution type"),
                        sg.Combo(["1080p", "Default"], default_value="Default", key=RES_TYPE_K, readonly=True),
                    ],
                    [
                        sg.Checkbox("Continuous Running", False, key=ALWAYS_RUN_K, expand_x=True, change_submits=True, tooltip="Note that this will need constant vision of window"),
                    ],
                    [
                        sg.Checkbox("Run When Window Active Only", False, key=RUN_ACTIVE_ONLY_K, expand_x=True, change_submits=True, tooltip="Note this will disable any data extraction from game while window is not visible"),
                    ],
                ]), ])
        ],
        # [sg.Button('Exit')],
    ]

    window = sg.Window('Shotgun king achievement assistant', layout, icon=ICON_PATH).finalize()  # , size=(500, 150)

    always_run_last_time = time.time()
    ccw = CheckChoiceWindow()

    reset = False
    while True:  # Event Loop
        event, values = window.Read(timeout=2000)
        # print(event, values)
        if event in (None, "Exit"):
            break

        elif event == "__TIMEOUT__":
            pass

        elif event == "Run":
            getCurrentData()

        elif event == ALWAYS_RUN_K:
            # waitChoiceWindow()
            if values[event]:
                ALWAYS_RUN = True
            else:
                ALWAYS_RUN = False

        elif event == RUN_ACTIVE_ONLY_K:
            if values[event]:
                RUN_ACTIVE_ONLY = True
            else:
                RUN_ACTIVE_ONLY = False

        elif event == CLEAR_K:
            clear()
        elif event == RESET_K:
            reset = True
            break
        # Positive cards (Buffs) - Choice
        elif chooseCardsEvent(event, CURRENT_DATA):
            pass

        if time.time() - always_run_last_time > 5:
            if not (RUN_ACTIVE_ONLY and GetWindowText(GetForegroundWindow()) != window_text):
                if ALWAYS_RUN and ccw.checkChoiceWindow():
                    getCurrentData()
                always_run_last_time = time.time()

        print(CURRENT_DATA)

    window.Close()

    if reset:
        return True
    else:
        return False


while main():
    pass
