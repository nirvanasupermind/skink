enum TokenType {
    INT,
    DOUBLE,
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    LPAREN,
    RPAREN,
    EOF_
};

struct TokenValue {
    std::int32_t i;
    double d;
};                   

class Token {
    public:
        TokenType type;
        TokenValue value;

        Token(TokenType type, TokenValue value) {
            this->type = type;
            this->value = value;
        }

        std::string str() {
            std::string result;

            switch (type) {
                case TokenType::INT:
                    result += "INT:" + std::to_string(value.i);
                    break;
                case TokenType::DOUBLE:
                    result += "DOUBLE:" + std::to_string(value.d);
                    break;
                case TokenType::PLUS:
                    result += "PLUS";
                    break;
                case TokenType::MINUS:
                    result += "MINUS";
                    break;
                case TokenType::MULTIPLY:
                    result += "MULTIPLY";
                    break;
                case TokenType::DIVIDE:
                    result += "DIVIDE";
                    break;
                case TokenType::LPAREN:
                    result += "LPAREN";
                    break;
                case TokenType::RPAREN:
                    result += "RPAREN";
                    break;
                case TokenType::EOF_:
                    result += "EOF";
                    break;
            }

            return result;
        }
};