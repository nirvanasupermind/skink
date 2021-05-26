# skink
[![npm version](https://badge.fury.io/js/skink.svg)](https://badge.fury.io/js/skink)<br>
(WiP)<br>
Skink is a small, statically typed, interpreted programming language that is  especially suited to numeric computation and scientific computing. It emphasizes prototype-based code.

# Specification
See [SPEC.md](SPEC.md).

# Implementation
Skink's core is implemented in Node.js. The Skink evaluator executes a typed abstract syntax tree. 

# Usage
You first need to install Node.js to use the skink implementation.

The skink package is available from the npm registry
```
$ npm install skink
```
Once you have installed the package you can run the shell from bash using
```
$ skink
```
and run a file using
```
$ skink <filename>
```

If you don't have bash, you can use the node API:
```js
var skink = require("skink");
skink("<filename>");
```


