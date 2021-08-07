# skink
**NOTICE**: this is work in progress

Skink is a small, dynamically-typed programming language with a prototype-based object model.

```java
var Point = Object.new();
Point.new = function (x, y) {
    var result = Object.new()
    result.setPrototype(Point);
    result.x = x;
    result.y = y;

    return result;
}

Point.sum = function (this) {
    return this.x + this.y;
}

var myPoint = Point.new(1, 1);
System.print(myPoint.sum()); //=> 2
```

# Use
In order to use this implementation of Skink, you must have the [python](https://www.python.org) and [pip](https://pypi.org/) installed.

