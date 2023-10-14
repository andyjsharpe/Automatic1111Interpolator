# Automatic1111Interpolator

This is a script intended to be used to interpolate between multiple prompts in order to creare an image sequence using Automatic 1111. This script outputs a .txt file which Automatic 1111 can read using the "Prompts from file or textbox" script to create a sequance of images.

This script is purely designed to produce sets of positve and negative prompts. In this vein the Checkpoint, Step Count, Refiner, Styles, Sampling Method, and all other diffusion settings have to be configured in the Automatic 1111 UI. This makes it so that an output can be easily reused with different Checkpoints and settings easily.

If you wish to modify the code it should be pretty self-explanitory. Tkinter is used for the UI but everything else is just normal built-in Python.

## Global Settings:
The top bar of the UI contains important settings that effect the rest of the UI:
- The "Add/Remove Interpolations" buttons add and remove interpolations
- "Last Frame" decides the point which new images will stop being made (the numer of output images will be this value + 1 to handle the zero frame).
- "Constants" is the positve prompt which is applied to each image. All normal Automatic 1111 prompt formating can be used. Note that this is not intended to be a replacement of Automatic 1111's styles feature, as that generally gives better results, but rather an ease-of-use tool to avoid having to make an interpolation with only one keyframe in order to have constant values.
- "Constant Negatives" is the same exact thing, but for negative prompts.
- "Output File Name" is the name of the file which will be outputted by the script. The file will be created in the folder containing the script.
- The "Create File" button is what you press to create the output file based on all of your inputs. Once clicked the text nest to it will say "Running...", and if it finished with no errors will say "Done!".

## Interpolations:
Each "Interpolation" represents a single chaning feature. I reccomnd using a single interpolation for similar groups of ideas (for example: use one Interpolation for the camera angle and another for the setting).
- The "Negative?" checkbox puts the outputs of the interpolation in the negative prompt box instead of the positive prompt box.
- Each Interpolation is comprised of multiple "Keyframes" and "Transitions" which define the values being interpolated, their frame locations, and how they are interpolated. Since blending keyframes whith very different prompts can give unsatasfactory results, I reccomend erring on the side of using more keyframes if I can.
- The "Add/Remove Keyframes" button adds and removes keyframes (and the transitions between them)

## Keyframes:
Each "Keyframe: represents a prompt at a set point in time. Multiple keyframes will be interpolated within a single transition based on their frame to create the output.
- The "Prompt" is the prompt at that keyframe. All normal Automatic 1111 prompt formating can be used.
- The "Weight" is a multiplier applied to the prompt.
- The "Frame" is the time at which the keyframe occurs. The ammount that this keyframe's prompt is applied to any given image depends on the ratio betwen the image's frame and the distance to the nearest keyframe on either side. Make sure that this value is in between the frames of the surrounding keyframes or unintended outputs may be produced.

## Transition:
Between every pair of keyframes there will be a transition which is used to decide how they are interpolated
- The "Exponent" decides the shape of the interpolation:
  - 1 is Linear. This usaily gives good results, but you may want to change it is the "intersting" parts of the transition are not being given enough frames in theoutput images.
  - Values greater then 1 makes an s-curve that spends more time on the ends of the interpolation, this is best used if a lot of changes occur near the ends or if the middle of the transition is "boring".
  - Values less then 1 makes an inverted s-curve that spends more time on the middle of the interpolation, this is best used if the ends do not have many changes, or if the middle is the most interesting part of the transition.
- The "Use Step Interpolation?" checkbox changes the mode of how the interpolation is done:
  - Normally prompt values are blended based on their weights and frames, then that resulting blended prompt is applied over all diffusion steps, this usially works quite well and is the default.
  - In some cases there is no satasfactory blend between two prompts, usially occuring when they are very different and of different types, in that case it may be better to use one prompt for some steps, and then use the second prompt for the rest. Checking the box will turn on this mode for the transition, though be aware that this often "skews" the timing of the transition, so the exponent may not have the same effect as before.

