**Note**: This document is a work in progress and is constantly evolving into a proper specification.
<!-- # 1. Introduction
Skink is a small, statically typed, interpreted programming language. It emphasizes prototype-based code.<br><br>
Skink has a large standard library which contains several packages.

# 2. Lexical Structure
This chapter specifies the lexical structure of Skink. -->

# 1 Introduction
Skink is a small, statically typed, interpreted programming language that is  especially suited to numeric computation and scientific computing. It emphasizes prototype-based code.

# 2 Lexical Structure
This chapter specifies the lexical structure of Skink.

Skink programs are written using the Unicode character set.

## 2.1 Identifiers
Identifiers consist of an ASCII letter or an ASCII underscore (`_`), optionally followed by a string of letters, digits, and underscores.


The lowercase and uppercase representation of the same alphabetic character are considered different characters. For instance "foo", "Foo" and "fOo" will be treated as 3 distinct identifiers.


## 2.2 Keywords
The following words are reserved words by the language and cannot be used as identifiers:

```
as const do else export for if import namespace return while
```

## 2.3 Operators
The following tokens are the Skink operators, formed from ASCII characters:
```
! != % & && &= * + += - -= / /= < <= = == > >= >> 
```


## 2.4 Literals
A literal is the source code representation of a value of a type. Literals include integer literals, floating-point literals, string literals, object literals, and tuple literals.

### 2.4.1 Integer Literals
An integer literal consists of one or more ASCII digits from `0` to `9` optionally suffixed with a letter `L` or `l`, representing a positive integer. 

Examples of integer literals:
```
10 1729 9223372036854775807L
```

### 2.4.2 Floating-Point Literals
A floating-point literal has three parts: an integral part (represented by an [integer literal](#241-integer-literals)), a decimal point (represented by an ASCII period character), and an optional fractional part (represented by an integer literal).

Examples of floating point literals:
```
0. 10.5 60.0
```

### 2.4.3 String Literals
A string literal consists of zero or more characters enclosed in double quotes. Each character may be represented by an escape sequence. The supported escape sequences are:
* `\n` for the ASCII LF character, also known as "newline"
* `\r` for the ASCII CR character, also known as "return"
* `\t` for the ASCII HT character, also known as "tab"
* `\"` for the ASCII quote character (`"`)


Examples of string literals:
```
"foo" "bar" "baz" "\n"
```

## 2.4.4 Object Literals
## 2.4.5 Tuple Literals

## 2.5 Comments
Comments consist of zero or more characters surrounded by the characters `/*` and `*/`. They are ignored by the interpreter.

Comments cannot nest. 

Examples of comments:
```
/* comment 1 * / /* comment 2 * /
/* 
    multiline comment
*/ 
```

## 2.6 Line Breaks and Whitespace
A line break consists of one or more line break characters, where a line break character is defined as one of the following:
* the ASCII LF character, also known as "newline"
* the ASCII CR character, also known as "return"
* the ASCII semicolon character (`;`)
Line breaks are used to divide code into lines.

Whitespace consists of one or more whitespace characters, where a whitespace character is defined as one of the following:
* the ASCII SP character, also known as "space"
* the ASCII HT character, also known as "tab"

Whitespace is ignored by the interpreter, with the exception of [literals](#24-literals).

## 2.7 Other Tokens

# 3 Types and Values
## 3.1 Objects and Prototypes
## 3.2 object
## 3.3 void
## 3.3 bool
## 3.4 tuple
## 3.5 number
## 3.6 int
## 3.7 long
## 3.8 double
## 3.9 string
## 3.10 func
## 3.11 ns
## 3.12 Conversions and Promotions

# 4 Execution Context
## 4.1 Variables
## 4.2 Scope Management

# 5 Statements
## 5.1 Closures
## 5.2 if Statements
## 5.3 while Loops
## 5.4 for Loops
## 5.5 return Statements

# 6 Expressions
## 6.1 Operators
## 6.2 Assignment

# 7 Standard Functions
## 7.1 Global Functions
## 7.2 Member Functions

# 8 Modules
## 8.1 Creating Modules
## 8.2 Importing Modules

# 9 Standard Modules