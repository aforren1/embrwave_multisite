
The most recent Windows executable will be zipped up under:

https://ci.appveyor.com/project/aforren1/embrwave-multisite/build/artifacts

The source can be found at:

https://github.com/aforren1/embrwave_multisite

A few notes:
 - Make sure to put the Embr Wave in pairing mode (hold the button until green) before hitting
   the "Connect" button in the GUI, or else the connection won't happen and subsequent attempts
   will fail (as of Oct 16, 2019).
 - When writing new translations, note that HTML is allowed, e.g. `<br>` will insert a line break.
 - When writing new translations, prefer double quotes (`"`) in the TOML files. Some of the formatting (e.g. newlines) doesn't seem to work with single quotes. 
 - Assuming Python 3.7 (later versions should also work fine)
 - Targeting Windows 10, but other operating systems should work with minimal changes
