import tkinter as tk
from tkinter import ttk

blackColor = '#171717'
navyColor= '#1f252e'
greyColor = '#2f353d'
lightColor = '#595f69'

whiteColor = '#cfcfcf'
goldColor = '#ffcc00'
checkColor = '#919191'

lineFormat = "--prompt {} --negative_prompt {}\n"
weightFormat = "({}):{}" #Prompt, weight
mixPromptFormat = "{{({}:{}) | ({}:{})}}" #Start, weight1*interp, End, weight2*(1-interp)
stepPromptFormat = "[(({}):{}) : (({}):{}) : {}]" #Start, weight1, End, weight2, 1-interp

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

def validate_end_txt(value):
    return ".txt" in value

def scurve(value, exponent):
    if value == 1:
        return 1
    xRatio = value/(1-value)
    if xRatio <= 0:
        return 0
    return 1/(1+xRatio**(-exponent))

class TransitionEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Transition Interpolator")
        self.transitions = []
        self.blanks = []

        self.scrollFrame = tk.Frame(root)
        self.scrollFrame.columnconfigure(index=0, weight=1)
        self.scrollFrame.rowconfigure(index=0, weight=1)
        self.scrollFrame.pack(fill="both", expand=True)

        self.scrollCanvas = tk.Canvas(self.scrollFrame)
        self.scrollCanvas.grid(row=0, column=0, sticky="nsew")

        self.scrollY = ttk.Scrollbar(self.scrollFrame, orient="vertical", command=self.scrollCanvas.yview)
        self.scrollY.grid(row=0, column=1, sticky="ns")

        self.scrollX = ttk.Scrollbar(self.scrollFrame, orient="horizontal", command=self.scrollCanvas.xview)
        self.scrollX.grid(row=1, column=0, sticky="ew")

        self.scrollCanvas.configure(yscrollcommand=self.scrollY.set, xscrollcommand=self.scrollX.set, bg=navyColor)
        self.scrollCanvas.bind_all("<Configure>", self.updateScrollRegion)
        self.scrollCanvas.bind_all("<MouseWheel>", self.mouseScrollY)
        self.scrollCanvas.bind_all("<Shift - MouseWheel>", self.mouseScrollX)

        self.transition_frame = tk.Frame(self.scrollCanvas, bg="black")
        self.transition_frame.pack(side="top", fill="both")
        self.window = self.scrollCanvas.create_window((0, 0), window=self.transition_frame, anchor="nw")

        self.button_frame = tk.Frame(self.transition_frame, bg=greyColor)
        self.button_frame.grid(sticky="ew", row=0, column=0)

        span = 1

        self.transitionButtonsFrame = tk.Frame(self.button_frame, bg=greyColor)
        self.transitionButtonsFrame.grid(padx=10, row=3, column=0, sticky="W", columnspan=span)

        self.add_transition_button = tk.Button(self.transitionButtonsFrame, text="Add Interpolation", command=self.add_transition, background=navyColor, foreground=whiteColor)
        self.add_transition_button.pack(pady=10, padx=10, side="left")
        self.remove_transition_button = tk.Button(self.transitionButtonsFrame, text="Remove Interpolation", command=self.remove_transition, background=navyColor, foreground=whiteColor)
        self.remove_transition_button.pack(pady=10, padx=10, side="left")

        self.constantsFrame = tk.Frame(self.button_frame, bg=greyColor)
        self.constantsFrame.grid(padx=10, row=1, column=0, sticky="E", columnspan=span)

        self.constantsLabel = ttk.Label(self.constantsFrame, text="Constants:", background=navyColor,foreground=whiteColor)
        self.constantsLabel.pack(pady=10, padx=10, side="left")
        self.constantsEntry = ttk.Entry(self.constantsFrame, width=160, background=greyColor, foreground=blackColor)
        self.constantsEntry.pack(padx=5, side="left")

        self.negConstantsFrame = tk.Frame(self.button_frame, bg=greyColor)
        self.negConstantsFrame.grid(padx=10, row=2, column=0, sticky="E", columnspan=span)

        self.negConstantsLabel = ttk.Label(self.negConstantsFrame, text="Constant Negatives:", background=navyColor,
                                        foreground=whiteColor)
        self.negConstantsLabel.pack(pady=10, padx=10, side="left")
        self.negConstantsEntry = ttk.Entry(self.negConstantsFrame, width=160, background=greyColor, foreground=blackColor)
        self.negConstantsEntry.pack(padx=5, side="left")

        self.runFrame = tk.Frame(self.button_frame, bg=greyColor)
        self.runFrame.grid(padx=10, row=0, column=0, sticky="W", columnspan=span)

        self.framesLabel = ttk.Label(self.runFrame, text="Last Frame:", background=navyColor,
                                     foreground=whiteColor)
        self.framesLabel.pack(padx=5, side="left")

        valid1 = self.runFrame.register(validate_int_10k)
        self.frames = tk.StringVar(value="10")
        self.framesEntry = ttk.Entry(self.runFrame, width=6, background=greyColor, foreground=blackColor,
                                     textvariable=self.frames, validate="key", validatecommand=(valid1, '%P'))
        self.framesEntry.pack(padx=5, side="left")

        self.fileNameLabel = ttk.Label(self.runFrame, text="Output File Name:", background=navyColor,
                                       foreground=whiteColor)
        self.fileNameLabel.pack(pady=10, padx=10, side="left")

        validTxt = self.runFrame.register(validate_end_txt)
        self.file = tk.StringVar(value="out.txt")
        self.fileName = ttk.Entry(self.runFrame, width=16, background=greyColor, foreground=blackColor,
                                  textvariable=self.file, validate="key", validatecommand=(validTxt, '%P'))
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

        #This pre-opens up some of the UI
        #blankFrame = BlankFrame(self.transition_frame, 0)
        #self.blanks.append(blankFrame)
        #self.add_transition()

    def updateScrollRegion(self, event):
        self.scrollCanvas.update_idletasks()
        self.scrollCanvas.configure(scrollregion=self.scrollCanvas.bbox("all"))

    def mouseScrollY(self, event):
        self.scrollCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def mouseScrollX(self, event):
        self.scrollCanvas.xview_scroll(int(-1*(event.delta/120)), "units")

    def create_file(self):
        f = open(self.fileName.get(), "w+")
        self.runningLabel.config(text="Running...", foreground=goldColor)
        try:
            #For each frame
            for frame in range(int(self.frames.get()) + 1):
                prompt = []
                negPrompt = []
                #For each transition
                for transition in self.transitions:
                    if len(transition.keyframes) < 1:
                        continue
                    startKeyframe = transition.keyframes[0]
                    startDist = max(frame - int(startKeyframe.time_entry.get()), 0)
                    endKeyframe = transition.keyframes[-1]
                    endDist = max(int(endKeyframe.time_entry.get()) - frame, 0)
                    exponent = transition.exponents[0]
                    if startDist < 0:
                        newPrompt = weightFormat.format(startKeyframe.prompt_entry.get(), startKeyframe.weight_entry.get())
                        if transition.negative.get():
                            negPrompt.append(newPrompt)
                        else:
                            prompt.append(newPrompt)
                        continue
                    if endDist < 0:
                        newPrompt = weightFormat.format(endKeyframe.prompt_entry.get(), endKeyframe.weight_entry.get())
                        if transition.negative.get():
                            negPrompt.append(newPrompt)
                        else:
                            prompt.append(newPrompt)
                    # Loop through keyframes until closest one on each side is found
                    for i in range(len(transition.keyframes)):
                        keyframe = transition.keyframes[i]
                        time = int(transition.keyframes[i].time_entry.get())
                        if time < frame:
                            if max(frame - time, 0) < startDist and keyframe != transition.keyframes[-1]:
                                startKeyframe = keyframe
                                startDist = max(frame - time, 0)
                                if i < len(transition.exponents):
                                    exponent = transition.exponents[i]
                        elif time > frame:
                            if max(time - frame, 0) < endDist and keyframe != transition.keyframes[0]:
                                endKeyframe = keyframe
                                endDist = max(time - frame, 0)
                                if i < len(transition.exponents):
                                    exponent = transition.exponents[i]
                        elif time == frame:
                            if endKeyframe != keyframe and max(frame - time, 0) < startDist and keyframe != transition.keyframes[-1]:
                                startKeyframe = keyframe
                                startDist = max(frame - time, 0)
                                if i < len(transition.exponents):
                                    exponent = transition.exponents[i]
                            elif startKeyframe != keyframe and max(time - frame, 0) < endDist and keyframe != transition.keyframes[0]:
                                endKeyframe = keyframe
                                endDist = max(frame - time, 0)
                                if i < len(transition.exponents):
                                    exponent = transition.exponents[i]
                    print(str(frame) + ": " + startKeyframe.prompt_entry.get() + "-" + endKeyframe.prompt_entry.get())
                    interp = (frame - int(startKeyframe.time_entry.get())) / (int(endKeyframe.time_entry.get()) - int(startKeyframe.time_entry.get()))
                    interp = scurve(interp, float(exponent.exponent.get()))
                    if interp >= 1:
                        interp = 0.999
                    if interp <= 0:
                        interp = 0.001
                    interp = round(1-interp, 3)
                    if exponent.interpolation.get():
                        newPrompt = stepPromptFormat.format(startKeyframe.prompt_entry.get(), float(startKeyframe.weight_entry.get()), endKeyframe.prompt_entry.get(), float(endKeyframe.weight_entry.get()), interp)
                        if transition.negative.get():
                            negPrompt.append(newPrompt)
                        else:
                            prompt.append(newPrompt)
                    else:
                        newPrompt = mixPromptFormat.format(startKeyframe.prompt_entry.get(), round(float(startKeyframe.weight_entry.get())*interp, 3), endKeyframe.prompt_entry.get(), round(float(endKeyframe.weight_entry.get())*(1 - interp),3))
                        if transition.negative.get():
                            negPrompt.append(newPrompt)
                        else:
                            prompt.append(newPrompt)
                finalPromps = ', '.join(prompt + [self.constantsEntry.get()])
                finalNegPrompts = ', '.join(negPrompt + [self.negConstantsEntry.get()])
                line = lineFormat.format(finalPromps, finalNegPrompts)
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

    def add_transition(self):
        transition = Transition(self.transition_frame, len(self.transitions) + 1)
        transition.add_keyframe()
        transition.add_keyframe()
        blankFrame = BlankFrame(self.transition_frame, len(self.transitions) + 1)
        self.transitions.append(transition)
        self.blanks.append(blankFrame)

    def remove_transition(self):
        if len(self.transitions) <= 0:
            return
        transition = self.transitions[-1]
        self.transitions.remove(transition)
        transition.transition_frame.destroy()
        blankFrame = self.blanks[-1]
        self.blanks.remove(blankFrame)
        blankFrame.blank_frame.destroy()

class BlankFrame:
    def __init__(self, parent_frame, num):
        self.parent_frame = parent_frame

        self.blank_frame = tk.Frame(parent_frame, height=4, bg=blackColor)
        self.blank_frame.grid(sticky="ew",row=num * 2 + 2, column=0)

class Transition:
    def __init__(self, parent_frame, num):
        self.parent_frame = parent_frame
        self.keyframes = []
        self.exponents = []

        self.transition_frame = tk.Frame(parent_frame, padx=8, pady=8, bg=navyColor)
        self.transition_frame.grid(sticky="w",row=num * 2 + 1, column=0)

        self.transition_buttons_frame = tk.Frame(self.transition_frame, padx=8, pady=8, bg=navyColor)
        self.transition_buttons_frame.grid(row = 0, column=0, sticky="N")

        self.transition_label = ttk.Label(self.transition_buttons_frame, text="Interpolation #" + str(num) + ": ", font="Verdana 8 bold", background=navyColor, foreground=whiteColor)
        self.transition_label.grid(row=0, column=0, padx=5)

        self.negative = tk.BooleanVar(value=False)
        self.negative_checkbox = tk.Checkbutton(self.transition_buttons_frame, text="Negative?", background=greyColor,
                                                foreground=checkColor, variable=self.negative)
        self.negative_checkbox.grid(row=1, column=0, padx=5)

        self.keyframes_frame = tk.Frame(self.transition_frame, padx=8, pady=8, bg=navyColor)
        self.keyframes_frame.grid(row = 0, column=1, sticky="N")

        self.add_keyframe_button = tk.Button(self.transition_buttons_frame, text="Add Keyframe",
                                             command=self.add_keyframe, background=navyColor, foreground=whiteColor)
        self.add_keyframe_button.grid(row=3, column=0, padx=5)
        self.remove_keyframe_button = tk.Button(self.transition_buttons_frame, text="Remove Keyframe",
                                                command=self.remove_keyframe, background=navyColor,
                                                foreground=whiteColor)
        self.remove_keyframe_button.grid(row=4, column=0, padx=5)


    def add_keyframe(self):
        keys = len(self.keyframes)
        if keys > 0:
            exponent = Exponent(self.keyframes_frame, keys)
            self.exponents.append(exponent)
        keyframe = Keyframe(self.keyframes_frame, keys+1)
        self.keyframes.append(keyframe)
    def remove_keyframe(self):
        keys = len(self.keyframes)
        if keys <= 0:
            return
        if keys > 1:
            exponent = self.exponents[-1]
            self.exponents.remove(exponent)
            exponent.exponent_frame.destroy()
        keyframe = self.keyframes[-1]
        self.keyframes.remove(keyframe)
        keyframe.keyframe_frame.destroy()

class Keyframe:
    def __init__(self, parent_frame, num):
        self.parent_frame = parent_frame

        self.keyframe_frame = tk.Frame(parent_frame, padx=4, pady=4, bg=greyColor)
        self.keyframe_frame.pack(fill="x")

        self.keyframe_label = ttk.Label(self.keyframe_frame, text="Keyframe #" + str(num) + ": ", font="Verdana 8 bold", background=navyColor, foreground=whiteColor)
        self.keyframe_label.pack(side="left", padx=5)

        self.prompt_label = ttk.Label(self.keyframe_frame, text="Prompt:", background=navyColor, foreground=whiteColor)
        self.prompt_label.pack(side="left", padx=5)
        self.prompt_entry = ttk.Entry(self.keyframe_frame, width=120, background=navyColor, foreground=blackColor)
        self.prompt_entry.pack(side="left", padx=5)

        self.weight = tk.StringVar(value="1")
        valid1 = self.keyframe_frame.register(validate_float_1000)
        self.weight_label = ttk.Label(self.keyframe_frame, text="Weight:", background=navyColor, foreground=whiteColor)
        self.weight_label.pack(side="left", padx=5)
        self.weight_entry = ttk.Entry(self.keyframe_frame, width=5, background=navyColor, foreground=blackColor, validate="key", validatecommand=(valid1, '%P'), textvariable=self.weight)
        self.weight_entry.pack(side="left", padx=5)

        self.time = tk.StringVar(value=str(num - 1))
        valid2 = self.keyframe_frame.register(validate_float_1000)
        self.time_label = ttk.Label(self.keyframe_frame, text="Frame:", background=navyColor, foreground=whiteColor)
        self.time_label.pack(side="left", padx=5)
        self.time_entry = ttk.Entry(self.keyframe_frame, width=5, background=navyColor, foreground=blackColor, validate="key", validatecommand=(valid2, '%P'),textvariable=self.time)
        self.time_entry.pack(side="left", padx=5)

class Exponent:
    def __init__(self, parent_frame, num):
        self.parent_frame = parent_frame

        self.exponent_frame = tk.Frame(parent_frame, padx=2, pady=2, bg=navyColor)
        self.exponent_frame.pack(fill="x")

        self.exponent_label = ttk.Label(self.exponent_frame, text="\tTransition #" + str(num) + ": ", font="Verdana 8 bold", background=navyColor, foreground=whiteColor)
        self.exponent_label.pack(side="left", padx=5)

        valid1 = self.exponent_frame.register(validate_float_1000)
        self.exponent_label = ttk.Label(self.exponent_frame, text="Exponent:", background=navyColor, foreground=whiteColor)
        self.exponent_label.pack(side="left", padx=5)
        self.exponent = tk.StringVar(value="1")
        self.exponent_entry = ttk.Entry(self.exponent_frame, width=6, background=greyColor, foreground=blackColor, validate="key", validatecommand=(valid1, '%P'), textvariable=self.exponent)
        self.exponent_entry.pack(side="left", padx=5)

        self.interpolation = tk.BooleanVar(value=False)
        self.interpolation_checkbox = tk.Checkbutton(self.exponent_frame, text="Use Step Interpolation?", background=greyColor, foreground=checkColor, variable=self.interpolation)
        self.interpolation_checkbox.pack(side="left", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    widthOffset = 120
    heightOffset = 120
    root.geometry("{}x{}+{}+{}".format(screen_width - 2*widthOffset, screen_height - 80 - 2*heightOffset, widthOffset-10, heightOffset))
    #root.state('zoomed')
    app = TransitionEditor(root)
    root.mainloop()
