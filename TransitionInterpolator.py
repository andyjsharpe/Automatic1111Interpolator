import tkinter as tk
from tkinter import ttk

blackColor = '#171717'
navyColor = '#1f252e'
greyColor = '#2f353d'
lightColor = '#595f69'

whiteColor = '#cfcfcf'
goldColor = '#ffcc00'
checkColor = '#919191'

lineFormat = "--prompt {} --negative_prompt {}"
weightFormat = "({}):{}"  # Prompt, weight
mixPromptFormat = "{{({}:{}) | ({}:{})}}"  # Start, weight1*interp, End, weight2*(1-interp)
stepPromptFormat = "[(({}):{}) : (({}):{}) : {}]"  # Start, weight1, End, weight2, 1-interp


def validate_int_seed(i):
    if i == "":
        return True
    try:
        value = int(i)
        if -1 <= value:  # Change the range as needed
            return True
        else:
            return False
    except ValueError:
        return False


def validate_int_10k(i):
    if i == "":
        return True
    try:
        value = int(i)
        if 0 <= value <= 10000:  # Change the range as needed
            return True
        else:
            return False
    except ValueError:
        return False


def validate_float_1000(i):
    if i == "":
        return True
    try:
        value = float(i)
        if 0 <= value <= 1000:  # Change the range as needed
            return True
        else:
            return False
    except ValueError:
        return False


def validate_float_1(i):
    if i == "":
        return True
    try:
        value = float(i)
        if 0 <= value <= 1:  # Change the range as needed
            return True
        else:
            return False
    except ValueError:
        return False


def validate_end_txt(value):
    return ".txt" in value


def scurve(value, exponent):
    if value == 1:
        return 1
    x_ratio = value / (1 - value)
    if x_ratio <= 0:
        return 0
    return 1 / (1 + x_ratio ** (-exponent))


def blank_frame(parent_frame):
    return tk.Frame(parent_frame, height=2, bg=blackColor)


def label(parent_frame, text, bold):
    if bold:
        return ttk.Label(parent_frame, text=text, background=greyColor,
                         foreground=whiteColor, font="Verdana 8 bold")
    else:
        return ttk.Label(parent_frame, text=text, background=navyColor,
                         foreground=whiteColor)


class TransitionEditor:
    def __init__(self, parent_frame):
        self.root = parent_frame
        self.root.title("Transition Interpolator")
        self.transitions = []
        self.switchTransition = None

        self.scrollFrame = tk.Frame(parent_frame)
        self.scrollFrame.columnconfigure(index=0, weight=1)
        self.scrollFrame.rowconfigure(index=0, weight=1)
        self.scrollFrame.pack(fill="both", expand=True)

        self.scrollCanvas = tk.Canvas(self.scrollFrame)
        self.scrollCanvas.grid(row=0, column=0, sticky="nsew")

        self.scrollY = ttk.Scrollbar(self.scrollFrame, orient="vertical", command=self.scrollCanvas.yview)
        self.scrollY.grid(row=0, column=1, sticky="ns")

        self.scrollX = ttk.Scrollbar(self.scrollFrame, orient="horizontal", command=self.scrollCanvas.xview)
        self.scrollX.grid(row=1, column=0, sticky="we")

        self.scrollCanvas.configure(yscrollcommand=self.scrollY.set, xscrollcommand=self.scrollX.set, bg=navyColor)
        self.scrollCanvas.bind_all("<Configure>", self.update_scroll_region)
        self.scrollCanvas.bind_all("<MouseWheel>", self.mouse_scroll_y)
        self.scrollCanvas.bind_all("<Shift - MouseWheel>", self.mouse_scroll_x)

        self.transition_frame = tk.Frame(self.scrollCanvas, bg=navyColor)
        self.transition_frame.grid_rowconfigure(0, weight=1)
        self.transition_frame.grid_columnconfigure(0, weight=1)
        self.transition_frame.grid(row=0, column=0, sticky="NSEW")
        self.window = self.scrollCanvas.create_window((0, 0), window=self.transition_frame, anchor="nw")

        self.button_frame = tk.Frame(self.transition_frame, bg=greyColor)
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid(sticky="EW", row=0, column=0)

        self.transitionButtonsFrame = tk.Frame(self.button_frame, bg=greyColor)
        self.transitionButtonsFrame.grid(padx=10, row=2, column=0, sticky="WE")

        self.add_transition_button = tk.Button(self.transitionButtonsFrame, text="Add Interpolation",
                                               command=self.add_transition, background=navyColor, foreground=whiteColor)
        self.add_transition_button.pack(pady=10, padx=10, side="left")

        self.inputsFrame = tk.Frame(self.button_frame, bg=greyColor)
        self.inputsFrame.grid(row=1, column=0, sticky="W", padx=10)

        self.constantsFrame = tk.Frame(self.inputsFrame, bg=greyColor)
        self.constantsFrame.grid(row=0, column=0, sticky="E")

        self.constantsLabel = label(self.constantsFrame, "Constants:", False)
        self.constantsLabel.pack(pady=10, padx=10, side="left")
        self.constantsEntry = ttk.Entry(self.constantsFrame, width=120, background=greyColor, foreground=blackColor)
        self.constantsEntry.pack(padx=5, side="left")

        self.negConstantsFrame = tk.Frame(self.inputsFrame, bg=greyColor)
        self.negConstantsFrame.grid(row=1, column=0, sticky="E")

        self.negConstantsLabel = label(self.negConstantsFrame, "Constant Negatives:", False)
        self.negConstantsLabel.pack(pady=10, padx=10, side="left")
        self.negConstantsEntry = ttk.Entry(self.negConstantsFrame, width=120, background=greyColor,
                                           foreground=blackColor)
        self.negConstantsEntry.pack(padx=5, side="left")

        self.runFrame = tk.Frame(self.button_frame, bg=greyColor)
        self.runFrame.grid(padx=10, row=0, column=0, sticky="WE", columnspan=2)

        self.framesLabel = label(self.runFrame, "Last Frame:", False)
        self.framesLabel.pack(padx=5, side="left")

        valid1 = self.runFrame.register(validate_int_10k)
        self.frames = tk.StringVar(value="10")
        self.framesEntry = ttk.Entry(self.runFrame, width=6, background=greyColor, foreground=blackColor,
                                     textvariable=self.frames, validate="key", validatecommand=(valid1, '%P'))
        self.framesEntry.pack(padx=5, side="left")

        self.frames.trace("w", self.update_frame_labels)

        self.multiplierLabel = label(self.runFrame, "Frame Multiplier:", False)
        self.multiplierLabel.pack(padx=5, side="left")

        valid_m = self.runFrame.register(validate_int_10k)
        self.multiplier = tk.StringVar(value="1")
        self.multiplierEntry = ttk.Entry(self.runFrame, width=6, background=greyColor, foreground=blackColor,
                                         textvariable=self.multiplier, validate="key", validatecommand=(valid_m, '%P'))
        self.multiplierEntry.pack(padx=5, side="left")

        self.multiplier.trace("w", self.update_frame_labels)

        self.trueLastLabel = label(self.runFrame, "True Last Frame: 10:", False)
        self.trueLastLabel.pack(pady=10, padx=10, side="left")

        self.fileNameLabel = label(self.runFrame, "Output File Name:", False)
        self.fileNameLabel.pack(pady=10, padx=10, side="left")

        valid_txt = self.runFrame.register(validate_end_txt)
        self.file = tk.StringVar(value="out.txt")
        self.fileName = ttk.Entry(self.runFrame, width=16, background=greyColor, foreground=blackColor,
                                  textvariable=self.file, validate="key", validatecommand=(valid_txt, '%P'))
        self.fileName.pack(padx=5, side="left")

        self.run_button = tk.Button(self.runFrame, text="Create File",
                                    command=self.create_file, background=navyColor,
                                    foreground=whiteColor)
        self.run_button.pack(pady=10, padx=10, side="left")

        self.debugging = tk.BooleanVar(value=True)
        self.debugging_checkbox = tk.Checkbutton(self.runFrame, text="Debug?", background=greyColor,
                                                 foreground=checkColor, variable=self.debugging)
        self.debugging_checkbox.pack(pady=5, padx=5, side="left")

        self.runningLabel = ttk.Label(self.runFrame, text="Ready", background=navyColor,
                                      foreground="green")
        self.runningLabel.pack(pady=5, padx=5, side="left")

        self.extrasFrame = tk.Frame(self.transitionButtonsFrame, bg=navyColor)
        self.extrasFrame.pack(pady=5, padx=5, side="left")

        self.extrasLabel = label(self.extrasFrame, "Extra Interpolations:", True)
        self.extrasLabel.grid(pady=5, padx=5, row=0, column=0, sticky="W")

        self.useRefinerSwitch = tk.BooleanVar(value=False)
        self.useRefinerSwitchCheckBox = tk.Checkbutton(self.extrasFrame, text="Interpolate Refiner Switch Location?",
                                                       background=greyColor,
                                                       foreground=checkColor, variable=self.useRefinerSwitch,
                                                       command=self.switch_transition_cmd)
        self.useRefinerSwitchCheckBox.grid(pady=5, padx=5, row=0, column=1, sticky="W")

        '''
        self.useSeed = tk.BooleanVar(value=False)
        self.useSeedCheckbox = tk.Checkbutton(self.extrasFrame, text="Interpolate Seed?",
                                              background=greyColor,
                                              foreground=checkColor, variable=self.useSeed)
        self.useSeedCheckbox.grid(pady=5, padx=5, row=0, column=2, sticky="W")
        '''

        # This pre-opens up some of the UI
        self.add_transition()

    def update_frame_labels(self, *args):
        mult = 0
        try:
            mult = int(self.multiplier.get())
        except:
            pass
        m_frames = 0
        try:
            m_frames = int(self.frames.get())
        except:
            pass
        tex = "True Last Frame: {}".format(mult * m_frames)
        self.trueLastLabel.config(text=tex)
        for transition in self.transitions:
            for keyframe in transition.keyframes:
                fr = 0
                try:
                    fr = int(keyframe.time.get())
                except:
                    pass
                tex2 = "True Frame: {}".format(mult * fr)
                keyframe.trueFrameLabel.config(text=tex2)
        if self.switchTransition is not None:
            for keyframe in self.switchTransition.keyframes:
                fr = 0
                try:
                    fr = int(keyframe.time.get())
                except:
                    pass
                tex2 = "True Frame: {}".format(mult * fr)
                keyframe.trueFrameLabel.config(text=tex2)

    def update_scroll_region(self, event):
        self.scrollCanvas.update_idletasks()
        self.update_frame_labels()
        self.scrollCanvas.configure(scrollregion=self.scrollCanvas.bbox("all"))

    def mouse_scroll_y(self, event):
        self.scrollCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def mouse_scroll_x(self, event):
        self.scrollCanvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_file(self):
        f = open(self.fileName.get(), "w+")
        self.runningLabel.config(text="Running...", foreground=goldColor)
        try:
            # For each frame
            multiplier = int(self.multiplier.get())
            for frame in range(int(self.frames.get()) * multiplier + 1):
                prompt, neg_prompt = self.get_transition_prompts(frame, multiplier)

                final_prompts = ', '.join(prompt + [self.constantsEntry.get()])
                if final_prompts == "":
                    final_prompts = ', '
                final_neg_prompts = ', '.join(neg_prompt + [self.negConstantsEntry.get()])
                if final_neg_prompts == "":
                    final_neg_prompts = ', '
                line = lineFormat.format(final_prompts, final_neg_prompts)

                if self.useRefinerSwitch.get():
                    switch = self.get_refiner_switch(frame, multiplier)
                    line += " --refiner_switch_at {}".format(switch)
                line += "\n"
                print(line)
                f.write(line)
        except Exception as error:
            if self.debugging.get():
                self.runningLabel.config(text="ERROR!: {}".format(error), foreground="red")
                f.close()
                return
            else:
                raise error
        f.close()
        self.runningLabel.config(text="Done!", foreground="green")

    def get_transition_prompts(self, frame, multiplier):
        prompt = []
        neg_prompt = []
        # For each transition
        for transition in self.transitions:
            if len(transition.keyframes) < 1:
                continue
            exponent = transition.exponents[0]

            override_keyframe, interp, start_keyframe, end_keyframe = self.get_interp_value(transition, frame, multiplier)

            if override_keyframe is not None:
                new_prompt = weightFormat.format(override_keyframe.prompt_entry.get(),
                                                 override_keyframe.weight_entry.get())
                if transition.negative.get():
                    neg_prompt.append(new_prompt)
                else:
                    prompt.append(new_prompt)
                continue

            if interp >= 1:
                interp = 0.999
            if interp <= 0:
                interp = 0.001
            interp = round(1 - interp, 3)
            if exponent.interpolation.get():
                new_prompt = stepPromptFormat.format(start_keyframe.prompt_entry.get(),
                                                     float(start_keyframe.weight_entry.get()),
                                                     end_keyframe.prompt_entry.get(),
                                                     float(end_keyframe.weight_entry.get()), interp)
                if transition.negative.get():
                    neg_prompt.append(new_prompt)
                else:
                    prompt.append(new_prompt)
            else:
                new_prompt = mixPromptFormat.format(start_keyframe.prompt_entry.get(),
                                                    round(float(start_keyframe.weight_entry.get()) * interp, 3),
                                                    end_keyframe.prompt_entry.get(),
                                                    round(float(end_keyframe.weight_entry.get()) * (1 - interp),
                                                          3))
                if transition.negative.get():
                    neg_prompt.append(new_prompt)
                else:
                    prompt.append(new_prompt)
        return prompt, neg_prompt

    def get_refiner_switch(self, frame, multiplier):
        transition = self.switchTransition
        switch = None
        if len(transition.keyframes) < 1:
            return switch

        override_keyframe, interp, start_keyframe, end_keyframe = self.get_interp_value(transition, frame, multiplier)

        if override_keyframe is not None:
            try:
                return round(float(override_keyframe.switchValue.get()), 2)
            except:
                return None

        round(interp, 2)

        if interp > 1:
            interp = 1
        if interp < 0:
            interp = 0

        try:
            start_val = float(start_keyframe.switchValue.get())
        except:
            start_val = 0
        try:
            end_val = float(end_keyframe.switchValue.get())
        except:
            end_val = 0

        return round(start_val + (end_val - start_val) * interp, 2)

    def get_interp_value(self, transition, frame, multiplier):
        start_keyframe = transition.keyframes[0]
        start_dist = frame - int(start_keyframe.time_entry.get()) * multiplier
        end_keyframe = transition.keyframes[-1]
        end_dist = int(end_keyframe.time_entry.get()) * multiplier - frame
        exponent = transition.exponents[0]

        if start_dist < 0:
            return start_keyframe, None, None, None
        if end_dist < 0:
            return end_keyframe, None, None, None

        # Loop through keyframes until closest one on each side is found
        for i in range(len(transition.keyframes)):
            keyframe = transition.keyframes[i]
            time = int(transition.keyframes[i].time_entry.get()) * multiplier
            if time < frame:
                if max(frame - time, 0) < start_dist and keyframe != transition.keyframes[-1]:
                    start_keyframe = keyframe
                    start_dist = max(frame - time, 0)
                    if i < len(transition.exponents):
                        exponent = transition.exponents[i]
            elif time > frame:
                if max(time - frame, 0) < end_dist and keyframe != transition.keyframes[0]:
                    end_keyframe = keyframe
                    end_dist = max(time - frame, 0)
                    if i < len(transition.exponents):
                        exponent = transition.exponents[i]
            elif time == frame:
                if end_keyframe != keyframe and max(frame - time, 0) < start_dist and keyframe != \
                        transition.keyframes[-1]:
                    start_keyframe = keyframe
                    start_dist = max(frame - time, 0)
                    if i < len(transition.exponents):
                        exponent = transition.exponents[i]
                elif start_keyframe != keyframe and max(time - frame, 0) < end_dist and keyframe != \
                        transition.keyframes[0]:
                    end_keyframe = keyframe
                    end_dist = max(frame - time, 0)
                    if i < len(transition.exponents):
                        exponent = transition.exponents[i]
        interp = (frame - int(start_keyframe.time_entry.get()) * multiplier) / (
                int(end_keyframe.time_entry.get()) * multiplier - int(
            start_keyframe.time_entry.get()) * multiplier)
        interp = scurve(interp, float(exponent.exponent.get()))
        return None, interp, start_keyframe, end_keyframe

    def add_transition(self):
        num = 1
        if len(self.transitions) > 0:
            num = self.transitions[-1].num + 1
        if self.switchTransition is not None:
            num += 1
        transition = Transition(self.transition_frame, num, self)
        transition.add_keyframe()
        transition.add_keyframe()
        self.transitions.append(transition)

    def switch_transition_cmd(self):
        if self.useRefinerSwitch.get():
            self.add_switch_transition()
        else:
            self.remove_switch_transition()

    def add_switch_transition(self):
        if self.switchTransition is not None:
            return
        num = 1
        if len(self.transitions) > 0:
            num = self.transitions[-1].num + 1
        transition = SwitchTransition(self.transition_frame, num, self)
        transition.add_keyframe()
        transition.add_keyframe()
        self.switchTransition = transition

    def remove_switch_transition(self):
        if self.switchTransition is None:
            return
        self.switchTransition.transition_frame.destroy()
        self.switchTransition = None


class Transition:
    def __init__(self, parent_frame, num, transition_editor):
        self.num = num
        self.parent_frame = parent_frame
        self.transitionEditor = transition_editor
        self.keyframes = []
        self.exponents = []

        self.transition_frame = tk.Frame(parent_frame, padx=0, pady=0, bg=navyColor)
        self.transition_frame.grid(sticky="w", row=num * 2 + 1, column=0)

        self.blank = blank_frame(self.transition_frame)
        self.blank.grid(row=0, column=0, sticky="EW", columnspan=3)

        self.transition_buttons_frame = tk.Frame(self.transition_frame, padx=8, pady=8, bg=navyColor)
        self.transition_buttons_frame.grid(row=1, column=0, sticky="N")

        self.remove_transition_button = tk.Button(self.transition_buttons_frame, text="X",
                                                  command=self.remove_transition, background=navyColor,
                                                  foreground=whiteColor)
        self.remove_transition_button.grid(row=0, column=0, padx=0, rowspan=3, sticky="WE")

        self.transition_label = label(self.transition_buttons_frame, "Interpolation #" + str(num) + ": ", True)
        self.transition_label.grid(row=0, column=1, padx=5, pady=5)

        self.negative = tk.BooleanVar(value=False)
        self.negative_checkbox = tk.Checkbutton(self.transition_buttons_frame, text="Negative?", background=greyColor,
                                                foreground=checkColor, variable=self.negative)
        self.negative_checkbox.grid(row=1, column=1, padx=5, pady=5)

        self.keyframes_frame = tk.Frame(self.transition_frame, padx=8, pady=8, bg=navyColor)
        self.keyframes_frame.grid(row=1, column=2, sticky="N")

        self.add_keyframe_button = tk.Button(self.transition_buttons_frame, text="Add Keyframe",
                                             command=self.add_keyframe, background=navyColor, foreground=whiteColor)
        self.add_keyframe_button.grid(row=2, column=1, padx=5, pady=5)

        self.blank2 = blank_frame(self.transition_frame)
        self.blank2.grid(row=4, column=0, sticky="EW", columnspan=3)

    def add_keyframe(self):
        keys = len(self.keyframes)
        if keys > 0:
            exponent = Exponent(self.keyframes_frame, keys)
            self.exponents.append(exponent)
        keyframe = Keyframe(self.keyframes_frame, keys + 1, self.transitionEditor, self)
        self.keyframes.append(keyframe)

    def remove_transition(self):
        self.transitionEditor.transitions.remove(self)
        self.transition_frame.destroy()


class SwitchTransition:
    def __init__(self, parent_frame, num, transition_editor):
        self.parent_frame = parent_frame
        self.transitionEditor = transition_editor
        self.keyframes = []
        self.exponents = []

        self.transition_frame = tk.Frame(parent_frame, padx=0, pady=0, bg=navyColor)
        self.transition_frame.grid(sticky="w", row=num * 2 + 1, column=0)

        self.blank = blank_frame(self.transition_frame)
        self.blank.grid(row=0, column=0, sticky="EW", columnspan=3)

        self.transition_buttons_frame = tk.Frame(self.transition_frame, padx=8, pady=8, bg=navyColor)
        self.transition_buttons_frame.grid(row=1, column=0, sticky="N")

        self.transition_label = label(self.transition_buttons_frame, "Refiner Switch Interpolation: ", True)
        self.transition_label.grid(row=0, column=0, padx=5, pady=5)

        self.keyframes_frame = tk.Frame(self.transition_frame, padx=8, pady=8, bg=navyColor)
        self.keyframes_frame.grid(row=1, column=1, sticky="N")

        self.add_keyframe_button = tk.Button(self.transition_buttons_frame, text="Add Keyframe",
                                             command=self.add_keyframe, background=navyColor, foreground=whiteColor)
        self.add_keyframe_button.grid(row=3, column=0, padx=5, pady=5)

        self.blank = blank_frame(self.transition_frame)
        self.blank.grid(row=2, column=0, sticky="EW", columnspan=3)

    def add_keyframe(self):
        keys = len(self.keyframes)
        if keys > 0:
            exponent = NoStepExponent(self.keyframes_frame, keys)
            self.exponents.append(exponent)
        keyframe = SwitchKeyframe(self.keyframes_frame, keys + 1, self.transitionEditor, self)
        self.keyframes.append(keyframe)


class Keyframe:
    def __init__(self, parent_frame, num, transition_editor, transition):
        self.num = num
        self.parent_frame = parent_frame
        self.transition = transition
        self.transitionEditor = transition_editor

        self.keyframe_frame = tk.Frame(parent_frame, padx=4, pady=4, bg=greyColor)
        self.keyframe_frame.pack(fill="x")

        self.keyframe_label = label(self.keyframe_frame, "Keyframe #" + str(num) + ": ", True)
        self.keyframe_label.pack(side="left", padx=5)

        self.prompt_label = label(self.keyframe_frame, "Prompt", False)
        self.prompt_label.pack(side="left", padx=5)
        self.prompt_entry = ttk.Entry(self.keyframe_frame, width=100, background=navyColor, foreground=blackColor)
        self.prompt_entry.pack(side="left", padx=5)

        self.weight = tk.StringVar(value="1")
        valid1 = self.keyframe_frame.register(validate_float_1000)
        self.weight_label = label(self.keyframe_frame, "Weight", False)
        self.weight_label.pack(side="left", padx=5)
        self.weight_entry = ttk.Entry(self.keyframe_frame, width=5, background=navyColor, foreground=blackColor,
                                      validate="key", validatecommand=(valid1, '%P'), textvariable=self.weight)
        self.weight_entry.pack(side="left", padx=5)

        self.time = tk.StringVar(value=str(num - 1))
        valid2 = self.keyframe_frame.register(validate_float_1000)
        self.time_label = label(self.keyframe_frame, "Frame", False)
        self.time_label.pack(side="left", padx=5)
        self.time_entry = ttk.Entry(self.keyframe_frame, width=5, background=navyColor, foreground=blackColor,
                                    validate="key", validatecommand=(valid2, '%P'), textvariable=self.time)
        self.time_entry.pack(side="left", padx=5)

        self.time.trace("w", self.transitionEditor.update_frame_labels)

        result = 0
        try:
            result = int(transition_editor.multiplier.get())
        except:
            pass
        self.trueFrameLabel = label(self.keyframe_frame, "True Frame: {}".format(str((num - 1) * result)), False)
        self.trueFrameLabel.pack(padx=10, side="left")

        self.remove_keyframe_button = tk.Button(self.keyframe_frame, text="X",
                                                command=self.remove_keyframe, background=navyColor,
                                                foreground=whiteColor)
        self.remove_keyframe_button.pack(padx=5, side="left")

    def remove_keyframe(self):
        # removing should remove this keyframe and the exponent after if it exists
        index = self.transition.keyframes.index(self)
        length = len(self.transition.keyframes)
        if index < length - 1:
            exponent = self.transition.exponents[index]
            self.transition.exponents.remove(exponent)
            exponent.exponent_frame.destroy()
        elif index == length - 1 and length > 1:
            exponent = self.transition.exponents[index - 1]
            self.transition.exponents.remove(exponent)
            exponent.exponent_frame.destroy()
        self.transition.keyframes.remove(self)
        self.keyframe_frame.destroy()


class SwitchKeyframe:
    def __init__(self, parent_frame, num, transition_editor, transition):
        self.parent_frame = parent_frame
        self.transition = transition
        self.transitionEditor = transition_editor

        self.keyframe_frame = tk.Frame(parent_frame, padx=4, pady=4, bg=greyColor)
        self.keyframe_frame.pack(fill="x")

        self.keyframe_label = label(self.keyframe_frame, "Keyframe #" + str(num) + ": ", True)
        self.keyframe_label.pack(side="left", padx=5)

        self.switchValue = tk.StringVar(value="0.5")
        valid1 = self.keyframe_frame.register(validate_float_1)
        self.switch_label = label(self.keyframe_frame, "Switch At: ", False)
        self.switch_label.pack(side="left", padx=5)
        self.switch_entry = ttk.Entry(self.keyframe_frame, width=5, background=navyColor, foreground=blackColor,
                                      validate="key", validatecommand=(valid1, '%P'), textvariable=self.switchValue)
        self.switch_entry.pack(side="left", padx=5)

        self.time = tk.StringVar(value=str(num - 1))
        valid2 = self.keyframe_frame.register(validate_float_1000)
        self.time_label = label(self.keyframe_frame, "Frame:", False)
        self.time_label.pack(side="left", padx=5)
        self.time_entry = ttk.Entry(self.keyframe_frame, width=5, background=navyColor, foreground=blackColor,
                                    validate="key", validatecommand=(valid2, '%P'), textvariable=self.time)
        self.time_entry.pack(side="left", padx=5)

        self.time.trace("w", self.transitionEditor.update_frame_labels)

        result = 0
        try:
            result = int(transition_editor.multiplier.get())
        except:
            pass
        self.trueFrameLabel = label(self.keyframe_frame, "True Frame: {}".format(str((num - 1) * result)), False)
        self.trueFrameLabel.pack(padx=10, side="left")

        self.remove_keyframe_button = tk.Button(self.keyframe_frame, text="X",
                                                command=self.remove_keyframe, background=navyColor,
                                                foreground=whiteColor)
        self.remove_keyframe_button.pack(padx=5, side="left")

    def remove_keyframe(self):
        # removing should remove this keyframe and the exponent after if it exists
        index = self.transition.keyframes.index(self)
        length = len(self.transition.keyframes)
        if index < length - 1:
            exponent = self.transition.exponents[index]
            self.transition.exponents.remove(exponent)
            exponent.exponent_frame.destroy()
        elif index == length - 1 and length > 1:
            exponent = self.transition.exponents[index - 1]
            self.transition.exponents.remove(exponent)
            exponent.exponent_frame.destroy()
        self.transition.keyframes.remove(self)
        self.keyframe_frame.destroy()


class Exponent:
    def __init__(self, parent_frame, num):
        self.parent_frame = parent_frame

        self.exponent_frame = tk.Frame(parent_frame, padx=2, pady=2, bg=navyColor)
        self.exponent_frame.pack(fill="x")

        self.exponent_label = label(self.exponent_frame, "\tTransition #" + str(num) + ": ", True)
        self.exponent_label.pack(side="left", padx=5)

        valid1 = self.exponent_frame.register(validate_float_1000)
        self.exponent_label = label(self.exponent_frame, "Exponent:", False)
        self.exponent_label.pack(side="left", padx=5)
        self.exponent = tk.StringVar(value="1")
        self.exponent_entry = ttk.Entry(self.exponent_frame, width=6, background=greyColor, foreground=blackColor,
                                        validate="key", validatecommand=(valid1, '%P'), textvariable=self.exponent)
        self.exponent_entry.pack(side="left", padx=5)

        self.interpolation = tk.BooleanVar(value=False)
        self.interpolation_checkbox = tk.Checkbutton(self.exponent_frame, text="Use Step Interpolation?",
                                                     background=greyColor, foreground=checkColor,
                                                     variable=self.interpolation)
        self.interpolation_checkbox.pack(side="left", padx=5)


class NoStepExponent:
    def __init__(self, parent_frame, num):
        self.parent_frame = parent_frame

        self.exponent_frame = tk.Frame(parent_frame, padx=2, pady=2, bg=navyColor)
        self.exponent_frame.pack(fill="x")

        self.exponent_label = label(self.exponent_frame, "\tTransition #" + str(num) + ": ", True)
        self.exponent_label.pack(side="left", padx=5)

        valid1 = self.exponent_frame.register(validate_float_1000)
        self.exponent_label = label(self.exponent_frame, "Exponent:", False)
        self.exponent_label.pack(side="left", padx=5)
        self.exponent = tk.StringVar(value="1")
        self.exponent_entry = ttk.Entry(self.exponent_frame, width=6, background=greyColor, foreground=blackColor,
                                        validate="key", validatecommand=(valid1, '%P'), textvariable=self.exponent)
        self.exponent_entry.pack(side="left", padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    widthOffset = 120
    heightOffset = 120
    root.geometry(
        "{}x{}+{}+{}".format(screen_width - 2 * widthOffset, screen_height - 80 - 2 * heightOffset, widthOffset - 10,
                             heightOffset))
    # root.state('zoomed')
    app = TransitionEditor(root)
    root.mainloop()
