#include <iostream>
#include "../tokens.cpp"

int main () {
    TokenValue v = {.i=2};

    Token token(TokenType::INT, v);

    std::cout << token.str();

    return 0;
}