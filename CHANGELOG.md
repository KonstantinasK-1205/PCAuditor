# Changelog

## [v5.3.2] (2019-05-07)

**Major Changes:**
- Moved all InfoCollector + Shell Script gather/parser and handling to seperate module, allowing for easier management and cleaner solution | *BatteryParser*
- Improved battery parsing information effectiviness, and providing almost instant update | *BatteryParser*
- Moved all InfoCollector + Shell Script gather/parser and handling to seperate module, allowing for easier management and cleaner solution | *DriveGather*
- Improved CDROM gathering/parsing, additionaly software will warn user if there is any optical disk inside computer | *DriveGather*
- Now it is possible to "Quick Format" disk drive ( Wipping out partition tables ) | *DriveGather*
- Added Bug Report, for better issues, error handling and fixing | *GUI*
- Changed server GET address, in favor of dropping old GET support | *Server*

**Minor Changes - Cleanup:**
- A lot of code cleanup
- Added support for Ultrabook batteries (CMB) | *BatteryParser*
- Added information backup source, if main source gathering fails | *BatteryParser*
- Added new field, Form Factor which is required field if computer is Desktop | *InfoCollector & GUI*
- Added possibility to disable keyboard test through command line | *InfoCollector*
- Reworked GPU Sensors parsing, making it more crash-free | *InfoCollector*
- Suppressed sensors error messages, when computer has GPU which can automatically disable itself | *InfoCollector*
- Changed extended box functions, to make it cleaner and more readable | *NBSummary*
- Changed dropbox creation, to make it cleaner and more readable | *NBSummary*
- Changed overheating texts | *NBStress*
- Improved Observation tab creation, by eliminating lot of unnecessary loops | *NBObservations*
- Optimised keyboard event, by reducing keypress IF  | *Events*

**Closed issues & Fixed bugs:**
- Fixed bug, when stress tab would freeze if CPU didn't have max temperature pre-set
- Fixed bug where GPU Temperature would update twice as fast as CPU. [\#6](https://github.com/KonstantinasK-1205/PCAuditor/issues/6)
- Fixed bug where BatteryParser would crash while trying to read or edit the file it can't load. [\#4](https://github.com/KonstantinasK-1205/PCAuditor/issues/4)

## [v5.3.1] (2019-03-21)

**Minor Changes - Cleanup:**
- InfoCollector
    - Added new Manufacturer & GPU replacement
    - Cleanup of GPU Temp function, removing hopefully unnecessary loop(?)
    - Changed maximum and critical temperature logic for GPU, for giving more room of heating, instead of almost immediately thermal shutdown.

**Fixed bugs:**
- Eliminated (hopefully) bug, where if GPU turns off it temperature becomes N/A (in JSON whole line just disappears), and it makes temperature function to crash.

## [v5.3] (2019-03-20)

**Major Changes:**
- Rewritten CPU & GPU temperature parsing, moved from heavy use of regex to JSON + Few lines of regex (Primary for AMD processors)
- CPU & GPU, maximum and critical temperature isn't hardcoded, but parsed from their own declared value.

**Minor Changes - Cleanup:**
- InfoCollector
    - Added new statement to condition for 'System Type', because some manufacturers declared type as 'Loptop' instead of 'Laptop'
    - Cleanup few variables (InfoCollector)
    - Updated version number

- GUI
    - If testing computer type is desktop, it will skip screen and camera entry box test (Validation if they are not empty)

- NBTest
    - Removed extra new line from keyboard test, to allow software take smaller window size than previous.

- NBStress
    - Created new variable holding temperature CPU & GPU dict, and giving it, instead of repeating long line every time i need to use it. In theory should also improve performance a bit.

**Closed issues & Fixed bugs:**
- Fixed bug where RAM gathering would break earlier than expected. [\#3](https://github.com/KonstantinasK-1205/PCAuditor/issues/3)
- Fixed bug where it would only output one GPU temperature if two same manufacturer GPU is present [\#1](https://github.com/KonstantinasK-1205/PCAuditor/issues/1)

**Closed issues:**
- When testing desktop computer, it will automatically fill screen and camera information  [\#2](https://github.com/KonstantinasK-1205/PCAuditor/issues/2)

## [v5.2] (2019-03-15)

- First Commit! (Github)

**Major Changes:**
- Added advanced debug output, showing how much time it took to execute a command.
- Added output function, for easier debug log reading.
- Added better support for application, so it doesn't require heavy modification when jumping between PXE and developer version.
- Added physical rack/box - spinbox'es, allowing users to specify in which box/rack goes recorded system.

- Rewritten - Order Page visuals, making it more nicer to eye
- Rewritten CPU extracting part, moving from LSHW to LSCPU gathering, giving more accurate information.
- Rewritten code, for making it object orientated, no more GUI.py with 2400+ lines of code!
- Rewritten code readability for PEP-8 full support.

- Reduced required memory amount, from ~30MB to ~20MB, by removing unused variables.
- Reduced loading time for application between 70% up to 150%:
    - Now lshw loads at linux startup, in parallel with GUI.
    - Optimized information extraction functions
    - Rewritten bigger half of regex'es, reducing their steps

- Eliminated most of crash scenarios, letting user fix problem by itself if isn't fatal error.
- Eliminated unnecessary communications with server, in beginning of program.

**Minor Changes:**
- Improved display master output parsing by 80-100%
- Improved regex patterns for fewer steps, reducing general time it needs to parse text
- Improved {disk/optical} drive loading/parsing time, by reducing unnecessary loops, and adding more breakpoints.

- Rewritten camera regex, allowing it to be executed up to 200% faster
- Rewritten GPU parsing, gaining time improvement, reducing memory software uses and allowing for easier handling.


## [v5.1]

**Major Changes:**
- Added more CDROM options, letting you know serial and model of optical drive, and if it was found, automatically set Optical Device as Present.
- Added batch choice, so user can select from which batch computer was got.
- Added more crash-catch exceptions on Audio Test Page, specifically Microphone.
- Added nice feature, allowing computer select its current category if it was logged before.

- Complete rewrite of InfoCollector class.
- Finally fully decrypted InfoHolder class, as it didn't give any real benefit of using it.

**Minor Changes:**
- Few optimized functions inside GUI.py
- Bugfixes

## [v5.0]

**Major Changes:**
- Added CDROM options, allowing to select if CDROM is present or not.
- Added batch choice, so user can select from which batch computer was got.

- Rewritten GUI fully.
- Rewritten Observations for easier handling and creation on startup, also it now parses OBS codes from server.

**Minor Changes:**
- Bugfixes
