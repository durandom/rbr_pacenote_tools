* pacenote ids are always the same
* pacenote ids point to different sound files
* sound files should reflect their contents
* strings translate pacenote string to text in UI


1. read janne mod into model
   1. same as pacenote plugin
2. write model to format


https://vauhtimurot.blogspot.com/p/using-pacenote-plugin.html

When the pacenote language is set to English in-game, the samples go to \Audio\Speech\Numbers.
For other languages, they go to \Audio\Speech\Num[Xxx] (recommended!).


Numbers.ini - English
NumOther.ini - Other languages

> Not sure, mainly in compatibility with notes made with not Jannemod V3. Those notes with NIU prefix are duplicates of the notes, added to improve combatibility with notes made in V2 Jannemod. NIU == Not In Use.


```
# downsample
sox input.ogg output.ogg rate 11025

# add intercom
sox input.ogg output.ogg \
compand 0.2,1 6:-70,-60,-20 5 -90 0.2 \
equalizer 100 0.707 -5 highpass 300 lowpass 3000 equalizer 1000 0.707 3 \
gain 2.3 \
compand 0.2,1.0 6:-60,-1,-1 -5 -90 0.2

sox input.wav output.wav \
compand 0.2,1 6:-70,-60,-20 5 -90 0.2 \
equalizer 100 0.707 -5 highpass 300 lowpass 3000 equalizer 1000 0.707 3

sox input.wav output.wav \
highpass 300 lowpass 3000 \
compand 0.3,1 6:-70,-60,-20 5 -90 0.2 \
overdrive 10 \
equalizer 1000 0.707 3

```