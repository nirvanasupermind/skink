**Note**: This document is a work in progress and is constantly evolving into a proper specification.
<!-- # 1. Introduction
Skink is a small, statically typed, interpreted programming language. It emphasizes prototype-based code.<br><br>
Skink has a large standard library which contains several packages.

# 2. Lexical Structure
This chapter specifies the lexical structure of Skink. -->

# 1 Introduction
Skink is a lightweight, statically typed, interpreted programming language that is  especially suited to numeric computation and scientific computing. It emphasizes prototype-based code.

# 2 Lexical Structure
This section specifies the lexical structure of Skink.

Skink programs are written using the Unicode character set.

## 2.1 Identifiers
Identifiers in Skink can be any string of Latin letters, digits, and underscores, not beginning with a digit.

Skink is a case-sensitive language, so `foo` and `Foo` are counted as two distinct identifiers.

## 2.2 Reserved Words
The following words are reserved words by the language and cannot be used as identifiers:

```
as const do else export for if import namespace return while
```

## 2.3 Operators
The following tokens are the Skink operators, formed from ASCII characters:
```
! != % & && &= * + += - -= / /= < <= = == > >= >> 
```

## 2.4 String Literals
String literals consist of zero or more characters enclosed in double quotes. String literals also use the following C-like escape sequences:
* `\n` for the LF character, also known as "newline"
* `\r` for the CR character, also known as "return"
* `\t` for the HT character, also known as "tab"

Examples of valid string literals:
```
"foo"
"bar"
"baz"
"\n"
```

## 2.5 Numerical Constants
*Numerical constants* may be written with an optional decimal part and an optional `L` or `l`. 

Examples of valid numerical literals:
```
0
2
5.5
600L
1111.
```

## 2.6 Comments
Skink *comments* start with the characters `/*` and end with the characters `*/` (as in C), and can span multiple lines. They cannot nest, or appear inside strings.

Comments are ignored by the interpreter.

Examples of valid comments:
```
/* comment 1 */
/* comment 2 */
/*
  multiline comment
*/
```

## 2.7 Whitespace and Line Breaks
A *line break* consists of one or more line break characters, where a line break character is defined as one of the following:
* The LF character, also known as "newline"
* The CR character, also known as "return"
* A semicolon character (`;`)

Line breaks are used to divide Skink code into lines.

*Whitespace* consists of one or more whitespace characters, where a whitespace character is defined as one of the following:
* The SP character, also known as "space"
* The HT character, also known as "tab"

Whitespace is almost always ignored by the interpreter, with the exception of literals.

## 2.8 Other Tokens
Other used tokens are:
```
( ) { } [ ]	. , : 
```

# 3 Types and Values
## 3.1 Objects and Prototypes
Every value in Skink (including primitive values such as numbers and booleans) is an *object*. An object is an ordered collection of key-value pairs called *slots*. All keys must be of the type [`string`](#39-string), while values can be any valid expression. If a non-string key is used in an object, it will 
automatically be converted to a `string` using the `toString()` special function. Objects are defined using the [object statements](#56-object-statements).

Each slot in an object has an associated type, determined by finding the [prototype](#313-prototypes) of the slot's value. If the type is changed using [property assignment](#312-property-assignment), a runtime error is thrown.

All objects in Skink are first-class values. This means that all objects can be stored in variables, passed as arguments to other functions, and returned as results.

### 3.1.1 Property Accessor
Properties of an object are accessed by name, using either the dot notation
```
object.key
```
or the bracket notation
```
object[key]
```

If a property of an object cannot be found, [VOID](#33-void) will be returned.

### 3.1.2 Property Assignment
Properties of an object can be set using either the dot notation
```
object.key = value
```
or the bracket notation
```
object[key] = value
```

 
### 3.1.3 Prototypes
An object can be the *prototype* of other objects. This copies the slots defined in the parent object into the child objects. If an object is used as a prototype of other objects, it is known as *type*. 

The prototype of an object can be accessed and mutated at runtime using the built-in `proto` property.

A Skink implementation offers several predefined types, such as integers, floats, strings, booleans, and tuples.

## 3.2 object
Type `object` is the default prototype for all objects. See the [Objects and Prototypes](#31-objects-and-prototypes) section for more information about objects.

## 3.3 void
The type `void` represents the null, empty, or non-existent reference. The type `void` has exactly one value, called `VOID`.

## 3.3 bool
The type `bool` represents a logical entity and consists of exactly two unique values. One is called `true` and the other is called `false`.

```java
bool a = true;
```

## 3.4 tuple
The type `tuple` represents a fixed-size collection of heterogeneous values. They can be defined using the [tuple statements](#tuple-statements).

```java
tuple a = ("a", "b", "c", "d");
print(a[-1]); /* d */		
```

A tuple object of length `n` will have `2 * n` slots, whose keys correspond to the integers between `-n` and `n+1`, and whose values correspond to the tuple elements.

Manipulating tuples is done through a set of [standard functions](#6-standard-functions).

## 3.5 number
Type `number` represents an integer or floating-point number. It has the subtypes [`int`][#36-int], [`long`][#37-long], and [`double`][#38-double].

## 3.6 int
Type `int` represents a 32-bit signed integer.
```java
int a = 123;
int b = 12;
```

## 3.7 long
Type `long` represents a 64-bit signed integer.
```java
long a = 123L;
long b = 75L;
```

## 3.8 double
Type `double` represents a 64-bit IEEE 754 floating-point number.
```java
double a = 1.0;
double b = 0.234;
```

## 3.9 string
Type `string` represents an immutable sequence of characters.

```java
string a = "I'm a wonderful string\n"
```

There are several [standard functions](#6-standard-functions) for examining individual characters, for extracting substrings, for creating a copy of a string with all characters translated to uppercase or to lowercase, and so on.

## 3.10 func
Type `func` represents functions.

A function declares executable code that can be called, passing a fixed number of values as arguments. 


### 3.10.1 Function Calls
A call expression is used to invoke a function.

The syntax for function calls is:
```java
functionName(parameter1, parameter2,...)
```

### 3.10.2 Function Definitions
The syntax for function defintions is:
```java
returnType functionName(parameter1, parameter2,...) {
  /* function body */
}
```


## 3.11 ns
## 3.12 Conversions and Promotions

# 4 Execution Context
## 4.1 Variables and Constants
### 4.1.1 Pre-Defined Variables
## 4.2 Scope Management

# 5 Expressions
## 5.1 Closures
## 5.2 if Statements
## 5.3 while Loops
## 5.4 for Loops
## 5.5 return Statements
## 5.6 Object Statements
## 5.7 Tuple Statements

## 5.8 Operators
## 5.9 Assignment

# 6 Standard Functions
## 6.1 Global Functions

# 7 Modules
## 7.1 Creating Modules
## 7.2 Importing Modules

# 8 Standard Modules