#define WHITESPACE " \n\t"
#define DIGITS "0123456789"
// #define stringify( name ) # "name

#include <string>
#include <vector>
#include <fstream>
#include <iostream>

namespace skink {
    enum TokenType {
        NUMBER,
        PLUS,
        MINUS,
        MULTIPLY,
        DIVIDE,
        SEMICOLON,
        EOF_  
    };

    class Token {
        public:
            TokenType type;
            std::string value;

            Token(TokenType type) {
                this->type = type;
            }
            
            Token(TokenType type, std::string value) {
                this->type = type;
                this->value = value;
            }

            //for debugging
            operator std::string() const {
                return "token";
            }
    };

    class Lexer {
        public:
            static std::vector<Token> lex(std::string file, std::string text) {
                std::vector<Token> tokens;

                for(int i = 0; i < text.length();) {
                    std::string c(1, text[i]);
                    if(c.find_first_of(WHITESPACE) != std::string::npos) {
                        i++;
                    } else if(c.find_first_of(DIGITS) != std::string::npos) {
                        int decimal_point_count = 0;
                        std::string number_str = c;
                        i++;

                        while(i < text.length()) {
                            if (text[i] == '.')
                                if (++decimal_point_count > 1)
                                    break;
                            
                            number_str += text[i];
                            i++;
                        }
                            
                        tokens.push_back(Token(TokenType::NUMBER, number_str));
                    } else if(c == "+") {
                        i++;
                        tokens.push_back(Token(TokenType::PLUS));
                    } else if(c == "-") {
                        i++;
                        tokens.push_back(Token(TokenType::MINUS));
                    } else if(c == "*") {
                        i++;
                        tokens.push_back(Token(TokenType::MULTIPLY));
                    } else if(c == "/") {
                        i++;
                        tokens.push_back(Token(TokenType::DIVIDE));
                    }
                }
            }
    };

    void run(std::string path) {
        std::ifstream file(path);
        std::string text;
        std::string str;

        while (std::getline(file, str)) {
            text = text + str + "\n";
        }

        std::vector<Token> tokens = Lexer::lex(path, text);

        for(int i = 0; i < tokens.size(); i++) {
            std::cout << static_cast<std::string>(tokens.at(i));
        }
    }
}