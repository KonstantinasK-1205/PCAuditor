# Changelog

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
