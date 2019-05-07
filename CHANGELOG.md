# Changelog

## [v5.3.2] (2019-05-07)

**Major Changes:**

- BatteryParser
    - Moved all InfoCollector + Shell Script gather/parser and handling to seperate module, allowing for easier management and cleaner solution.
    - Improved battery parsing information effectiviness, and providing almost instant update

- DriveGather
    - Moved all InfoCollector + Shell Script gather/parser and handling to seperate module, allowing for easier management and cleaner solution.
    - Improved CDROM gathering/parsing, additionaly software will warn user if there is any optical disk inside computer
    - Now it is possible to "Quick Format" disk drive ( Wipping out partition tables )

- GUI
    - Added Bug Report, for better issues, error handling and fixing
    
- Server
    - Changed server GET address, in favor of dropping old GET support

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

- First Commit!
