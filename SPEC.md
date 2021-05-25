**Note**: This document is a work in progress and is constantly evolving into a proper specification.
<!-- # 1. Introduction
Skink is a small, statically typed, interpreted programming language. It emphasizes prototype-based code.<br><br>
Skink has a large standard library which contains several packages.

# 2. Lexical Structure
This chapter specifies the lexical structure of Skink. -->

# 1 Introduction
Skink is a small, statically typed, interpreted programming language. It emphasizes prototype-based code. It is especially suited to numeric computation and scientific computing.

# 2 Lexical Structure
This chapter specifies the lexical structure of Skink.

## 2.1 Identifiers
Identifiers start with a alphabetic character or `_` followed by any number of alphabetic characters, `_` or digits `[0-9]`. 

The lowercase and uppercase representation of the same alphabetic character are considered different characters. For instance "foo", "Foo" and "fOo" will be treated as 3 distinct identifiers.


## 2.2 Keywords
## 2.3 Operators
## 2.4 Literals
## 2.5 Comments
## 2.6 Newlines and Whitespace
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