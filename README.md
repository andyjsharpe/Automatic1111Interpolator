# Automatic 1111 Interpolator

This is a script which interpolates between multiple prompts to create an image sequence using Automatic 1111. This script outputs a .txt file which Automatic 1111 can read using the "Prompts from file or textbox" script to create a sequence of images.

<img src=Example/frame0.png width="14%"><img src=Example/frame1.png width="14%"><img src=Example/frame2.png width="14%"><img src=Example/frame3.png width="14%"><img src=Example/frame4.png width="14%"><img src=Example/frame5.png width="14%"><img src=Example/frame6.png width="14%">

This script produces sets of positive and negative prompts, but nothing else. Because of this you must configure the Checkpoint, Step Count, Refiner, Styles, Sampling Method, and all other diffusion settings in the Automatic 1111 UI. This makes it so that you can reuse the output with different Checkpoints and settings easily.

An example of a output text file is here: [Example Output](Example/ExampleOutput.txt)

If you wish to modify the code, it should be self-explanatory. Tkinter is the only library used.

I am not sure how much I plan to improve on this script, so feel free to fork this repo and make any modifications you want. If you have any feature requests or problems feel free to put them in the issues tab, though I cannot guarantee I will be able to get to them.

## Tips:
- Manually setting a seed makes the transitions seem more natural, though it may also make images seem too similar from a composition perspective.
- Try to limit the terms in a single keyframe as blending will become unstable, if you are getting to six terms it is time to split parts of them off into a separate interpolation.
- Super high weights often give strange results, if you are struggling to add a feature it is often more productive to either search for what is blocking it than to increase its weight.
- In some blends there may be a "jump" at some point in the transition rather than having a smooth transformation between the values. For example, if you blend the colors red and blue the image often does not contain purple, as they are not similar enough. An effective way to fix this is to add in intermediary keyframe with the middle value. Building off that example, adding a keyframe in the middle with the term "purple" is likely to give better results.
- A similar issue may appear on the frame which a keyframe occurs. This happens when the keyframe before and after that initial keyframe are quite different. You can either add more keyframes using the previous method, increase the weights of the middle keyframe, or add values to the prompt which are blends of values from the surrounding keyframes using the format {value1|value2}.
- If you are not getting satisfactory results try using a different checkpoint or diffusion settings, as you can reuse the .txt file this script creates.
- Since the image created relies on the training data relating to that specific prompt, blends which do not often exist may have issues. For example, the sky is normally blue, so transitioning between a blue and green sky will only give green values when close to the green sky keyframe and will often give strange results when it does occur. You can solve this issue by using the weighting system, but sometimes a blend is simply not possible.
- In a similar vein, since the script combines interpolations to make a single prompt, other terms can affect blending. For example, if you are blending between a baseball and volleyball, but the constant prompt is “at the beach” the volleyball is much more likely to show up in the output images as volleyballs are at the beach more often than baseballs. Again, you may be able to solve this issue using weights, but it is often easier to just use terms which lack interaction to avoid this issue altogether.

## UI Description and Guide:
While the UI may be self-explanatory for those who have used software with keyframes before, for others it may be a bit confusing at first. Each of the major sections of the UI and their interactable elements are as follows:

<img src=Example/ExampleInputs.png>

### Global Settings:
The top bar of the UI contains important settings that effect the rest of the UI:
- The "Add/Remove Interpolations" buttons add and remove interpolations
- "Last Frame" decides the frame number at which to stop (the number of output images will be this value + 1 to include the zero frame).
- "Constants" is the positive prompt which diffusion applies to each image. You can use all normal Automatic 1111 prompt formatting. Note that you should not use this as a replacement of Automatic 1111's styles feature, as that has more flexibility, but rather an ease-of-use tool to avoid having to make an interpolation with only one keyframe to have constant values.
- "Constant Negatives" is the same exact thing, but for negative prompts.
- "Output File Name" is the name of the file which the script will create. The script will create the file in its parent folder.
- The "Create File" button is what you press to create the output file based on all your inputs. Once clicked the text next to it will say "Running...", and if it finished with no errors will say "Done!".
- The "Debug?" checkbox makes it so any errors which arise during execution do not cause the program to fault (which would require a restart). Instead, the script shows the error next to the “Create File” button on screen. I highly recommend keeping this turned on unless you wish to make modifications to the code itself.

### Interpolations:
Each "Interpolation" represents a single changing feature. I recommend using a single interpolation for similar groups of ideas (for example: use one Interpolation for the camera angle and another for the setting).
- The "Negative?" checkbox puts the outputs of the interpolation in the negative prompt box instead of the positive prompt box.
- Each Interpolation is comprised of multiple "Keyframes" and "Transitions" which define the values the script is interpolating between and how it interpolates them. Since blending keyframes with different prompts can give unsatisfactory results, I recommend erring on the side of using more keyframes if you can.
- The "Add/Remove Keyframes" button adds and removes keyframes (and the transitions between them)

### Keyframes:
Each "Keyframe: represents a prompt at a set point in time. The script interpolates multiple keyframes within a single transition based on their frame to create the output.
- The "Prompt" is the prompt at that keyframe. You can use all normal Automatic 1111 prompt formatting.
- The "Weight" is a multiplier applied to the prompt.
- The "Frame" is the time at which the keyframe occurs. The script chooses which prompts to blend and how much based on the distance of the current image’s frame to this value. This must be in-between the frames of the surrounding keyframes, or the script will produce strange outputs.

### Transition:
Between every pair of keyframes there will be a transition which the script uses to decide how it interpolates their prompts:
- The "Exponent" decides the shape of the interpolation:
  - 1 is Linear. This usually gives reliable results, but you may want to change it if the "interesting" parts of the transition do not appear in the output images.
  - Values greater than 1 makes an s-curve that spends more time on the ends of the interpolation. You should use this if changes occur near the ends or if the middle of the transition is "boring".
  - Values less than 1 makes an inverted s-curve that spends more time on the middle of the interpolation. You should use this if the ends do not have changes, or if the middle is the most interesting part of the transition.
  - More specifically, the equation used to remap the interpolation value is: $$\frac{1}{1+\left(\frac{x}{1-x}\right)^{-\text{exponent}}}$$
- The "Use Step Interpolation?" checkbox changes the method which the script used to interpolate the prompts:
  - Normally the script blends prompt values based on their weights and frame values, then Automatic 1111 used the resulting blended prompt for all diffusion steps, this usually works quite well and is the default.
  - Sometimes there is no satisfactory blend between two prompts, usually occurring when they are different and of distinct types, in that case it may be better to use one prompt for the first few steps, and then use the second prompt for the rest. Checking the box will turn on this mode for the transition, though be aware that this often "skews" the timing of the transition, so the exponent may not have the same effect as before.
