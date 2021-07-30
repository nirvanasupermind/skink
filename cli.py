#!/usr/bin/env python
# Skink source code
# Usage permitted under terms of MIT License
import sys
import shell
import skink

argv = sys.argv
if len(argv) == 1:
    shell.run_shell()
else:
    fn = argv[1]
    result, error = skink.run(fn)
    if error: print(error.as_string())
