Quantizer
======================

backend sonification engine for ATLAS data
<br /><br />
To Run: <br />
Open GUI.pd <br />
Open ATLASMultiScalePatch.pd <br />
Make sure that GUI.pd reflects your desired settings <br />
double-click purple button on upper left corner of gui.pd twice in order to make sure that all settings are properly initialized
<br /><br />
Run python script via:  <br />
<br /><br />
python ATLAS_live_audio.py --test=1 <br />
<br />
[Above runs in a test mode in which a single event is streamed through the engine, as oppose to the mode in which many events are streamed.] <br />
<br />
Currently, you can add the following commandline arguments to adjust how the audio is streamed: <br />
<br />
--maxbeats=n [sets the number of beats in the audio per event] <br />
--seconds=n [sets the number of seconds of audio per event] <br />
--geo="" [we've only been using eta geometry, and only eta geometry is well tested, but the system is set up to stream WRT phi and absolute value of phi as well] <br />
--uniform=True/False [true by default, which runs in a mode that applies discretization of data to create beats. If off, data will be streamed in a more randomized way, based only on geometric coordinates of data] <br />


