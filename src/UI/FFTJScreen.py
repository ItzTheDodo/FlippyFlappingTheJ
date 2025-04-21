# FlippyFlappingTheJ
# ./src/UI/FFTJScreen.py

import math
import os
from functools import cache
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox
from PIL import ImageTk, Image as PILImage

from src.UI.RegularExpressonEditor import RegexEditorUI
from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.Automata.AutomatonBuilder import AutomatonBuilder
from src.utils.Automata.DFA import DeterministicFiniteAutomaton
from src.utils.Automata.NDFA import NonDeterministicFiniteAutomaton
from src.utils.IO.AutomatonFile import AutomatonFile
from src.utils.Language.LanguageScript import LanguageScriptFile
from src.utils.LayoutEngine.ForceDirected import ForceDirectedLayout
from src.utils.LayoutEngine.TransitionRenderer import TransitionManager, RenderedTransition
from src.utils.TkUtils.DragAndDrop import DropZone, DragAndDropRoundedButton, DragManager, DragAndDropTransparentButton, \
    DDRenderable
from src.utils.TkUtils.FloatingMenu import CustomMenu
from src.utils.TkUtils.RealTimeUpdateManager import RealTimeUpdateManager, PulseColour
from src.utils.TkUtils.RoundedButton import RoundedButton
from src.utils.TkUtils.Tooltip import ToolTip
from src.utils.TkUtils.TransparentButton import TransparentButton, TBCompound


class EditorMouseMode:  # Enum to make mouse changes easier to manage
    SELECT, TRANSITION_DRAW = range(2)


class FFTJUI(Tk):

    WIN_WIDTH: int = 1000
    WIN_HEIGHT: int = 700

    COLOUR_PALLET: list[str] = ["#cfcec7", "#c2bcb5", "#c0bbb2", "#a09b92"]
    BUTTON_OUTLINE_COL: str = "#aeb4ac"
    HEADER_COL: str = "#2c3643"
    TEXT_LIGHT_COL: str = "#aed3de"
    TEXT_DARK_COL: str = "#525764"

    DEFAULT_FONT: str = "Bahnschrift"

    def __init__(self, runtime):
        super().__init__()

        self._runtime = runtime

        # UI Setup
        self.title(f"Flippy Flapping The J ({self._runtime.version})")
        self.geometry("%sx%s+50+30" % (self.WIN_WIDTH, self.WIN_HEIGHT))
        self.resizable(False, False)

        self.screen = Canvas(self, width=self.WIN_WIDTH, height=self.WIN_HEIGHT, background=self.COLOUR_PALLET[0], bd=0)
        self.screen.pack(side='top', fill='both', expand=1)

        # Setup managers
        self._update_manager = RealTimeUpdateManager(self.screen)
        self._screen_drag_manager = DragManager(self, self.screen)

        self.STATE_IMAGE_FP = os.path.join(self._runtime.datafolder.image_folder, "State.png")
        self.INITIAL_STATE_IMAGE_FP = os.path.join(self._runtime.datafolder.image_folder, "InitialState.png")
        self.FINAL_STATE_IMAGE_FP = os.path.join(self._runtime.datafolder.image_folder, "FinalState.png")
        self.INITIAL_FINAL_STATE_IMAGE_FP = os.path.join(self._runtime.datafolder.image_folder, "InitialFinalState.png")
        self.SELECT_CURSOR_IMAGE_FP = os.path.join(self._runtime.datafolder.image_folder, "cursor-arrow.png")
        self.CROSS_CURSOR_IMAGE_FP = os.path.join(self._runtime.datafolder.image_folder, "cursor-cross.png")

        # tracking variables
        self._drop_zone_zoom: float = 0.0
        self._running: bool = True
        self._current_automaton: AutomatonBuilder = AutomatonBuilder()
        self._visible_state_table: dict[str: TransparentButton] = {}  # state_id: tb_tag
        self._current_cursor_type: int = EditorMouseMode.SELECT

        # load images
        self._load_images()

        # Saved assets
        self._drop_zone = DropZone(self.screen, width=730, height=480, bg=self.COLOUR_PALLET[0], highlightthickness=0)
        self._transition_manager = TransitionManager(self, self._drop_zone)

        # Render Sections
        self._file_section()
        self._edit_section()
        self._automata_edit_section()
        self._automata_build_zone()

        self._set_cursor_type(EditorMouseMode.SELECT)  # Initialise Cursor Buttons

        # load previous automaton
        self._load_open_automaton()

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tkraise()
        try:
            self.update_loop()
        except TclError:
            pass

    @property
    def drop_zone_zoom(self) -> float:
        return self._drop_zone_zoom

    @property
    def current_automata(self) -> AutomatonBuilder:
        return self._current_automaton

    @property
    def running(self) -> bool:
        return self._running

    def update_loop(self):
        while self._running:  # Main application loop
            self._update_manager.update()
            self.update()

    def close(self):
        self._running = False
        self.destroy()

    def _load_images(self):
        self._state_image_raw = PILImage.open(self.STATE_IMAGE_FP)
        self._state_image = self._state_image_raw
        self._state_image_tk = ImageTk.PhotoImage(self._state_image_raw)

        self._initial_state_image_raw = PILImage.open(self.INITIAL_STATE_IMAGE_FP)
        self._initial_state_image = self._initial_state_image_raw
        self._initial_state_image_tk = ImageTk.PhotoImage(self._initial_state_image_raw)

        self._final_state_image_raw = PILImage.open(self.FINAL_STATE_IMAGE_FP)
        self._final_state_image = self._final_state_image_raw
        self._final_state_image_tk = ImageTk.PhotoImage(self._final_state_image_raw)

        self._initial_final_state_image_raw = PILImage.open(self.INITIAL_FINAL_STATE_IMAGE_FP)
        self._initial_final_state_image = self._initial_final_state_image_raw
        self._initial_final_state_image_tk = ImageTk.PhotoImage(self._initial_final_state_image_raw)

        self._select_cursor_image = PILImage.open(self.SELECT_CURSOR_IMAGE_FP)
        self._select_cursor_image = self._select_cursor_image.resize((20, 30))
        self._select_cursor_image_tk = ImageTk.PhotoImage(self._select_cursor_image)

        self._cross_cursor_image = PILImage.open(self.CROSS_CURSOR_IMAGE_FP)
        self._cross_cursor_image = self._cross_cursor_image.resize((30, 30))
        self._cross_cursor_image_tk = ImageTk.PhotoImage(self._cross_cursor_image)

    def _load_open_automaton(self):
        automaton_fp = self._runtime.datafolder.config.getValue("current_file")
        if automaton_fp == "":
            return
        automaton_file = AutomatonFile(automaton_fp)
        automaton_alphabet = automaton_file.get_alphabet()
        automaton_states, final_states, initial_states = automaton_file.get_states()
        automaton_transitions = automaton_file.get_transitions(automaton_states)
        if automaton_file.is_deterministic():
            finite_automata = DeterministicFiniteAutomaton(automaton_states, automaton_alphabet, automaton_transitions, initial_states, final_states)
        else:
            finite_automata = NonDeterministicFiniteAutomaton(automaton_states, automaton_alphabet, automaton_transitions, initial_states, final_states)
        automaton_builder = AutomatonBuilder.get_builder_from_finite_automata(finite_automata)
        self.new_automata(automaton_builder)

    def open_file(self, e: Event, fp: str | None = None):
        pass

    def save_current_file(self, e: Event):
        pass

    def open_recent_file(self, e: Event, fp: str):
        pass

    def new(self):
        pass

    def open(self):
        pass

    def _file_section(self):
        # background
        RoundedButton.round_rectangle(self.screen, 5, 5, 250, 275, radius=10, fill=self.COLOUR_PALLET[1])

        # header
        RoundedButton.round_rectangle(self.screen, 5, 5, 250, 40, radius=10, fill=self.HEADER_COL)
        self.screen.create_text(30, 22, text="File", fill=self.TEXT_LIGHT_COL, font=(self.DEFAULT_FONT, 15, "bold"))

        # new file
        RoundedButton(self, self.screen, 25, 55, "New", self.new,
                      padding=15, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=200)

        # recent files
        self.screen.create_text(50, 120, text="Recent Files:", fill=self.TEXT_DARK_COL, font=(self.DEFAULT_FONT, 10))
        recent_files_options = self._runtime.datafolder.config.getValue("recent_files")
        self._recent_files_dropdown_var = StringVar(value="Open recent file..")
        recent_files_dropdown = Combobox(self.screen, values=recent_files_options, state="readonly",
                                         textvariable=self._recent_files_dropdown_var, width=25)
        self.screen.create_window((12, 135), window=recent_files_dropdown, anchor="nw")
        RoundedButton(self, self.screen, 195, 135, "> Open",
                      lambda e, var=self._recent_files_dropdown_var.get: self.open_recent_file(e, var),
                      padding=4, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL)

        # Open File
        RoundedButton(self, self.screen, 25, 165, "Open File..", self.open,
                      padding=4, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=200)

        # Save File
        RoundedButton(self, self.screen, 25, 207, "Save File..", self.save_current_file,
                      padding=15, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=200)

    def undo_action(self, e: Event):
        pass

    def redo_action(self, e: Event):
        pass

    def copy_action(self, e: Event):
        pass

    def delete_action(self, e: Event):
        pass

    def _edit_section(self):
        # background
        RoundedButton.round_rectangle(self.screen, 5, 290, 250, 485, radius=10, fill=self.COLOUR_PALLET[1])

        # header
        RoundedButton.round_rectangle(self.screen, 5, 290, 250, 325, radius=10, fill=self.HEADER_COL)
        self.screen.create_text(30, 307, text="Edit", fill=self.TEXT_LIGHT_COL, font=(self.DEFAULT_FONT, 15, "bold"))

        # Undo Redo Buttons
        RoundedButton(self, self.screen, 17, 340, "Undo", self.undo_action,
                      padding=15, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=100)
        RoundedButton(self, self.screen, 133, 340, "Redo", self.redo_action,
                      padding=15, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=100)

        # Copy button
        RoundedButton(self, self.screen, 25, 400, "Copy", self.copy_action,
                      padding=6, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=200)

        # Delete button
        RoundedButton(self, self.screen, 25, 440, "Delete", self.delete_action,
                      padding=6, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=200)

    def _convert_current_automata_to_dfa(self, _):
        finite_automata = self.current_automata.to_finite_automata()
        if isinstance(finite_automata, NonDeterministicFiniteAutomaton):
            finite_automata = finite_automata.to_deterministic()
        new_builder = AutomatonBuilder.get_builder_from_finite_automata(finite_automata)
        self.new_automata(new_builder)

    def _simplify_current_dfa(self, _):
        finite_automata = self.current_automata.to_finite_automata()
        if isinstance(finite_automata, NonDeterministicFiniteAutomaton):
            finite_automata = finite_automata.to_deterministic()
        new_builder = AutomatonBuilder.get_builder_from_finite_automata(finite_automata.simplify())
        self.new_automata(new_builder)

    def _is_current_automata_equivalent_to(self, e: Event):
        pass

    @staticmethod
    @cache
    def generate_offset(zoom: float):
        return (25 * ((zoom - 10) / (zoom - 11))) / 2

    def _set_state_image(self, state_id: int, state_widget: TransparentButton):
        is_final = self._current_automaton.is_final(state_id)
        is_initial = self._current_automaton.is_initial(state_id)
        if is_final and is_initial:
            state_widget.image = self._initial_final_state_image_tk
            state_widget.centre_offset = (25 * ((self._drop_zone_zoom - 10) / (self._drop_zone_zoom - 11))) / 2
        elif is_initial:
            state_widget.image = self._initial_state_image_tk
            state_widget.centre_offset = (25 * ((self._drop_zone_zoom - 10) / (self._drop_zone_zoom - 11))) / 2
        elif is_final:
            state_widget.image = self._final_state_image_tk
            state_widget.centre_offset = 0
        else:
            state_widget.image = self._state_image_tk
            state_widget.centre_offset = 0

    def _toggle_final_state(self, state_id: int, menu_obj: CustomMenu, state_widget: TransparentButton):
        menu_obj.hide_window("")
        success, err = self._current_automaton.toggle_state_final(state_id)
        if not success:
            messagebox.showerror("Final State toggle error", err)

        self._set_state_image(state_id, state_widget)
        self._transition_manager.attach_drag(state_widget)

    def _toggle_initial_state(self, state_id: int, menu_obj: CustomMenu, state_widget: TransparentButton):
        menu_obj.hide_window("")
        success, err = self._current_automaton.toggle_state_initial(state_id)
        if not success:
            messagebox.showerror("Initial State toggle error", err)

        self._set_state_image(state_id, state_widget)
        is_initial = self._current_automaton.is_initial(state_id)
        self._transition_manager.attach_drag(state_widget,
                                             centre_offset_x=self.generate_offset(self.drop_zone_zoom) if is_initial else 0)
        self._transition_manager.update_transitions_for_state(state_id, state_widget)

    def _delete_state(self, state_id: int, menu_obj: CustomMenu, state_widget: TransparentButton):
        menu_obj.hide_window("")
        state_widget.delete()
        success, err = self._current_automaton.remove_state(state_id)
        if not success:
            raise RuntimeError(err)
        del self._visible_state_table[str(state_id)]
        self._transition_manager.remove_drag(state_widget)

    def _generate_offset_for_state_render(self, state_id: int) -> (int, int):
        is_initial = self._current_automaton.is_initial(int(state_id))
        x_offset = int((75 * (self._drop_zone_zoom - 10)) / (self._drop_zone_zoom - 12)) \
            if is_initial else int((50 * (self._drop_zone_zoom - 10)) / (self._drop_zone_zoom - 12))
        y_offset = int((50 * (self._drop_zone_zoom - 10)) / (self._drop_zone_zoom - 12))
        return x_offset, y_offset

    def is_mouse_select_mode(self) -> bool:
        return self._current_cursor_type == EditorMouseMode.SELECT

    def is_mouse_transition_mode(self):
        return self._current_cursor_type == EditorMouseMode.TRANSITION_DRAW

    def _render_dropped_automata_state(self, e: Event, onto_widget: DropZone, widget_dropped: DDRenderable):
        if isinstance(widget_dropped, DragAndDropTransparentButton):
            if not self.is_mouse_select_mode():
                return
            widget_dropped.delete()
            state_id = widget_dropped.text
            del self._visible_state_table[str(state_id)]

            x_offset, y_offset = self._generate_offset_for_state_render(int(state_id))
            state_widget = DragAndDropTransparentButton(self, onto_widget, self._render_dropped_automata_state,
                                                        e.x - x_offset, e.y - y_offset, lambda _: None,
                                                        text=str(state_id), image=widget_dropped.image, padding=5,
                                                        compound=TBCompound.CENTER, text_font=(self.DEFAULT_FONT, 15),
                                                        drag_text=state_id, disabled_func=self.is_mouse_select_mode)
            self._transition_manager.replace(widget_dropped, state_widget)
            self._set_state_image(int(state_id), state_widget)
            self._transition_manager.update_transitions_for_state(int(state_id), state_widget)
        else:
            status, state_id = self._current_automaton.add_state(False, False)
            if not status:
                messagebox.showerror("State creation error.", state_id)

            x_offset, y_offset = self._generate_offset_for_state_render(int(state_id))
            state_widget = DragAndDropTransparentButton(self, onto_widget, self._render_dropped_automata_state,
                                                        e.x - 265 - x_offset, e.y - 5 - y_offset, lambda _: None,
                                                        text=str(state_id), image=self._state_image_tk, padding=5,
                                                        compound=TBCompound.CENTER, text_font=(self.DEFAULT_FONT, 15),
                                                        drag_text=state_id, disabled_func=self.is_mouse_select_mode)

        self._screen_drag_manager.attach_drag(state_widget)
        self._transition_manager.attach_drag(state_widget)
        self._visible_state_table[state_id] = state_widget
        menu = CustomMenu(self, offset=(-5, -5), rel=state_widget, spacing=5, padding=5,
                          background=self.COLOUR_PALLET[0])
        onto_widget.tag_bind(state_widget.tag, "<Button-3>", menu.show_menu)
        menu.add_widget(Button, text="Toggle Final", bd=0, bg=self.COLOUR_PALLET[2],
                        font=(self.DEFAULT_FONT, 12, "bold"), cursor="hand2", width=15,
                        command=lambda: self._toggle_final_state(int(state_id), menu, state_widget))
        menu.add_widget(Button, text="Toggle Initial", bd=0, bg=self.COLOUR_PALLET[2],
                        font=(self.DEFAULT_FONT, 12, "bold"), cursor="hand2", width=15,
                        command=lambda: self._toggle_initial_state(int(state_id), menu, state_widget))
        menu.add_widget(Button, text="Delete", bd=0, bg=self.COLOUR_PALLET[2],
                        font=(self.DEFAULT_FONT, 12, "bold"), cursor="hand2", width=15,
                        command=lambda: self._delete_state(int(state_id), menu, state_widget))

    def _generate_dfa_by_regex(self, _):
        editor_window = RegexEditorUI(self, self._runtime)
        if editor_window.regex.isspace():
            return
        if self._visible_state_table:
            is_ok = messagebox.askokcancel("Erase current automata",
                                           "Are you sure you want to replace the current automata?")
            if not is_ok:
                return
        language_script = LanguageScriptFile.load_by_string(editor_window.regex, self._runtime.datafolder)
        ndfa = language_script.language.to_non_deterministic_finite_automaton()
        dfa = ndfa.to_deterministic().simplify()
        automaton_builder = AutomatonBuilder.get_builder_from_finite_automata(dfa)
        self.new_automata(automaton_builder)

    def _create_menu_for_new_automaton(self, state_widget: TransparentButton, state_id: int):
        menu = CustomMenu(self, offset=(-5, -5), rel=state_widget, spacing=5, padding=5,
                          background=self.COLOUR_PALLET[0])
        self._drop_zone.tag_bind(state_widget.tag, "<Button-3>", menu.show_menu)
        menu.add_widget(Button, text="Toggle Final", bd=0, bg=self.COLOUR_PALLET[2],
                        font=(self.DEFAULT_FONT, 12, "bold"), cursor="hand2", width=15,
                        command=lambda: self._toggle_final_state(state_id, menu, state_widget))
        menu.add_widget(Button, text="Toggle Initial", bd=0, bg=self.COLOUR_PALLET[2],
                        font=(self.DEFAULT_FONT, 12, "bold"), cursor="hand2", width=15,
                        command=lambda: self._toggle_initial_state(state_id, menu, state_widget))
        menu.add_widget(Button, text="Delete", bd=0, bg=self.COLOUR_PALLET[2],
                        font=(self.DEFAULT_FONT, 12, "bold"), cursor="hand2", width=15,
                        command=lambda: self._delete_state(state_id, menu, state_widget))

    def new_automata(self, automaton: AutomatonBuilder):
        self.clear_automaton()
        self._current_automaton = automaton

        force_layout = ForceDirectedLayout(automaton, iterations=1000)
        force_layout.calculate_layout()
        state_positions = force_layout.positions

        # Calculate the bounding box of the initial positions
        min_x = min(pos[0] for pos in state_positions.values())
        max_x = max(pos[0] for pos in state_positions.values())
        min_y = min(pos[1] for pos in state_positions.values())
        max_y = max(pos[1] for pos in state_positions.values())

        drop_zone_width = 730
        drop_zone_height = 480
        padding = 60

        spread_factor_x = (drop_zone_width - 2 * padding) / (max_x - min_x)
        spread_factor_y = (drop_zone_height - 2 * padding) / (max_y - min_y)

        spread_factor = min(spread_factor_x, spread_factor_y)

        for state in self._current_automaton.states:
            x_offset, y_offset = self._generate_offset_for_state_render(state.id)
            positions = state_positions[state.id]
            spread_positions = ((positions[0] - min_x) * spread_factor + padding,
                                (positions[1] - min_y) * spread_factor + padding)
            state_widget = DragAndDropTransparentButton(self, self._drop_zone, self._render_dropped_automata_state,
                                                        spread_positions[0] - x_offset, spread_positions[1] - y_offset, lambda _: None,
                                                        text=state.id, image=self._state_image_tk, padding=5,
                                                        compound=TBCompound.CENTER, text_font=(self.DEFAULT_FONT, 15),
                                                        drag_text=str(state.id), disabled_func=self.is_mouse_select_mode)

            self._set_state_image(state.id, state_widget)
            self._screen_drag_manager.attach_drag(state_widget)
            self._transition_manager.attach_drag(state_widget, centre_offset_x=self.generate_offset(self.drop_zone_zoom) if state.is_initial else 0)
            self._visible_state_table[str(state.id)] = state_widget
            self._transition_manager.update_transitions_for_state(state.id, state_widget)

            self._create_menu_for_new_automaton(state_widget, int(state.id))

        for transition in self._current_automaton.transitions:
            rendered_link = RenderedTransition(self, self._drop_zone, widget_from=self._visible_state_table[str(transition.state_from.id)],
                                               widget_to=self._visible_state_table[str(transition.state_to.id)],
                                               transition=transition, radius1=50, radius2=50, manager=self._transition_manager)
            self._transition_manager.registered_rendered_transitions.append(rendered_link)
            self._transition_manager.update_transitions_for_state(transition.state_from.id, self._visible_state_table[str(transition.state_from.id)])
            self._transition_manager.update_transitions_for_state(transition.state_to.id, self._visible_state_table[str(transition.state_to.id)])

    def _set_cursor_type(self, cursor_type: int):
        self._select_button["bg"] = "grey"
        self._edit_transition_button["bg"] = "grey"
        if cursor_type == EditorMouseMode.SELECT:
            self._select_button["bg"] = self.COLOUR_PALLET[3]
            self._current_cursor_type = EditorMouseMode.SELECT
            self.config(cursor="arrow")
            self.screen.config(cursor="arrow")
        elif cursor_type == EditorMouseMode.TRANSITION_DRAW:
            self._edit_transition_button["bg"] = self.COLOUR_PALLET[3]
            self._current_cursor_type = EditorMouseMode.TRANSITION_DRAW
            self.config(cursor="plus")
            self.screen.config(cursor="plus")

    def _automata_edit_section(self):
        # background
        RoundedButton.round_rectangle(self.screen, 5, 500, 995, 695, radius=10, fill=self.COLOUR_PALLET[1])

        # header
        RoundedButton.round_rectangle(self.screen, 5, 500, 995, 535, radius=10, fill=self.HEADER_COL)
        self.screen.create_text(62, 517, text="Automaton", fill=self.TEXT_LIGHT_COL, font=(self.DEFAULT_FONT, 15, "bold"))

        # Convert to dfa button
        RoundedButton(self, self.screen, 17, 550, "Convert to DFA", self._convert_current_automata_to_dfa,
                      padding=15, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=150)

        # Simplify dfa button
        RoundedButton(self, self.screen, 17, 605, "Simplify DFA", self._simplify_current_dfa,
                      padding=15, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=150)

        # Is equivalent to button
        RoundedButton(self, self.screen, 17, 660, "Is Equivalent To..", self._simplify_current_dfa,
                      padding=5, radius=4, hover_colour="#909090", click_colour=self.HEADER_COL, width=150)

        self.screen.create_line((200, 560), (200, 675), fill=self.COLOUR_PALLET[3], width=2)

        # Generate by regex
        RoundedButton(self, self.screen, 230, 550, "Generate DFA by Regular Expression...",
                      self._generate_dfa_by_regex, padding=25, radius=4, hover_colour="#909090",
                      click_colour=self.HEADER_COL, width=250)

        # Automata State icon
        automata_state = DragAndDropRoundedButton(self, self.screen, self._render_dropped_automata_state,
                                                  750, 550, "New Automata State", lambda e: None,
                                                  padding=15, radius=4, hover_colour="#909090",
                                                  click_colour=self.HEADER_COL, width=150, drag_text="State")
        self._screen_drag_manager.attach_drag(automata_state)

        self.screen.create_line((925, 560), (925, 675), fill=self.COLOUR_PALLET[3], width=2)

        # Mouse select buttons
        self._select_button = Button(self, image=self._select_cursor_image_tk, bd=0, bg="grey",
                                     command=lambda: self._set_cursor_type(EditorMouseMode.SELECT),
                                     activebackground=self.COLOUR_PALLET[3], width=35, height=35)
        ToolTip(self._select_button, (-35, 25), text="Select", background=self.COLOUR_PALLET[3])
        self.screen.create_window(945, 550, window=self._select_button, anchor=NW, tags="select_button")

        self._edit_transition_button = Button(self, image=self._cross_cursor_image_tk, bd=0, bg="grey",
                                              command=lambda: self._set_cursor_type(EditorMouseMode.TRANSITION_DRAW),
                                              activebackground=self.COLOUR_PALLET[3], width=35, height=35)
        ToolTip(self._edit_transition_button, (-80, 25), text="Edit transitions", background=self.COLOUR_PALLET[3])
        self.screen.create_window(945, 600, window=self._edit_transition_button, anchor=NW, tags="transition_edit_button")

    def _zoom_drop_zone(self, zoom_factor: float = 0, direction: float = 0) -> bool:
        start_step = int(50 - zoom_factor * 5)
        if start_step < 1:
            duration_ns = int(RealTimeUpdateManager.seconds_to_ns(0.3))
            new_update_job = PulseColour(duration_ns, self._drop_zone, "dz_grid", "#ee847c")
            _ = self._update_manager.register_job(new_update_job)
            return False

        self._drop_zone.delete("dz_grid")

        # draw grid
        for x in range(start_step, 725, start_step):
            self._drop_zone.create_line((x, 5), (x, 475), fill=self.COLOUR_PALLET[3], tag="dz_grid")
        for y in range(start_step, 475, start_step):
            self._drop_zone.create_line((5, y), (725, y), fill=self.COLOUR_PALLET[3], tag="dz_grid")

        # redraw all states and transitions
        square_w_h = int((100 * (zoom_factor - 10)) / (zoom_factor - 12))
        rect_w = int((125 * (zoom_factor - 10)) / (zoom_factor - 12))
        image_z_factor = math.copysign(1, direction) if not direction == 0 else 0

        self._state_image = self._state_image_raw.resize((square_w_h, square_w_h))
        self._state_image_tk = ImageTk.PhotoImage(self._state_image)

        self._initial_state_image = self._initial_state_image_raw.resize((rect_w, square_w_h))
        self._initial_state_image_tk = ImageTk.PhotoImage(self._initial_state_image)

        self._final_state_image = self._final_state_image_raw.resize((square_w_h, square_w_h))
        self._final_state_image_tk = ImageTk.PhotoImage(self._final_state_image)

        self._initial_final_state_image = self._initial_final_state_image_raw.resize((rect_w, square_w_h))
        self._initial_final_state_image_tk = ImageTk.PhotoImage(self._initial_final_state_image)

        mult = 1.8 ** ((1 / 5) * -image_z_factor)
        for state_id, button_widget in self._visible_state_table.items():
            self._set_state_image(int(state_id), button_widget)
            button_widget.moveto(button_widget.x * mult, button_widget.y * mult)

            is_initial = self._current_automaton.is_initial(int(state_id))
            self._transition_manager.attach_drag(button_widget,
                                                 centre_offset_x=self.generate_offset(
                                                     self.drop_zone_zoom) if is_initial else 0)
            self._transition_manager.update_transitions_for_state(int(state_id), button_widget)

        return True

    def _dz_zoom(self, e: Event):
        direction = math.copysign(1, e.delta)
        self._drop_zone_zoom += direction
        success = self._zoom_drop_zone(self._drop_zone_zoom, direction)
        if not success:
            self._drop_zone_zoom -= direction
            return

        self._drop_zone.tag_raise("zoom_box")
        self._render_zoom_text()

    def _render_zoom_text(self):
        self._drop_zone.delete("zoom_box_text")
        text = self._drop_zone.create_text(5, 462, text=str(self._drop_zone_zoom), fill=self.TEXT_LIGHT_COL,
                                           font=(self.DEFAULT_FONT, 15, "bold"), tags=("zoom_box", "zoom_box_text"))
        text_bbox = self._drop_zone.bbox("zoom_box_text")
        text_width = text_bbox[2] - text_bbox[0]
        self._drop_zone.moveto(text, 5 + ((45 - text_width) / 2), 450)

    def _automata_build_zone(self):
        # background
        RoundedButton.round_rectangle(self._drop_zone, 5, 5, 725, 475, radius=10, fill=self.COLOUR_PALLET[1])
        self.screen.create_window(265, 5, window=self._drop_zone, anchor="nw")

        # render items on drop zone
        self._zoom_drop_zone()
        self._drop_zone.bind("<MouseWheel>", self._dz_zoom)

        # zoom information
        RoundedButton.round_rectangle(self._drop_zone, 5, 450, 50, 475, radius=10, fill="black", tag="zoom_box")
        self._render_zoom_text()

    def create_transition(self, from_state_id: int, to_state_id: int, link_by: list[str]) -> tuple[bool, AutomataLink | None]:
        success, transition_id = self._current_automaton.add_transition(from_state_id, to_state_id, link_by)
        if not success:
            messagebox.showerror("An error occurred.", transition_id)
            return False, None
        return True, self._current_automaton.get_transition(int(transition_id))

    def set_zoom(self, zoom: int):
        required_change = int(zoom - self.drop_zone_zoom)
        for _ in range(abs(required_change)):
            sign = math.copysign(1, required_change)
            success = self._zoom_drop_zone(self._drop_zone_zoom, sign)
            if not success:
                raise Exception("Error changing to zoom")

            self._drop_zone.tag_raise("zoom_box")
            self._render_zoom_text()

    def clear_automaton(self):
        self._current_automaton = AutomatonBuilder()
        for state in self._visible_state_table.values():
            state.delete()
        self._visible_state_table = {}
        self._transition_manager.clear()
        self.set_zoom(0)
