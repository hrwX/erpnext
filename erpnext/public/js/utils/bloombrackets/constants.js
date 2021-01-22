export const CMD_ARRAY = "ARRAY"
export const CMD_VAR = "VAR"
export const CMD_VAL = "VAL"
export const CMD_IF = "IF"
export const CMD_CALL = "CALL"
export const CMD_EQUALS = "=="
export const CMD_NOT_EQUALS = "!="
export const CMD_LIKE = "~"
export const CMD_NOT_LIKE = "!~"
export const CMD_GREATER_THAN = ">"
export const CMD_LESS_THAN = "<"
export const CMD_GREATER_AND_EQUAL = ">="
export const CMD_LESS_AND_EQUAL = "<="
export const CMD_BETWEEN = "BETWEEN"
export const CMD_ADD = "+"
export const CMD_SUBTRACT = "-"
export const CMD_MULTIPLY = "*"
export const CMD_DIVIDE = "/"
export const CMD_AND = "AND"
export const CMD_OR = "OR"
export const CMD_NOT = "NOT"
export const CMD_XOR = "XOR"
export const CMD_TRUE = "TRUE"
export const CMD_FALSE = "FALSE"
export const CMD_UNDEFINED = "UNDEFINED"
export const CMD_INT = "INT"
export const CMD_FLOAT = "FLOAT"
export const CMD_STRING = "STRING"
export const CMD_BOOL = "BOOL"
export const CMD_IN = "IN"
export const CMD_SET = "SET"
export const CMD_UNSUPPORTED = "UNSUPPORTED"

export const TYPE_STRING = "STRING"
export const TYPE_NUMERIC = "NUMERIC"
export const TYPE_BOOLEAN = "BOOLEAN"
export const TYPE_LIST = "LIST"
export const TYPE_BLOCK = "BLOCK"
export const TYPE_EXPRESSION = "EXPRESSION"

export const TYPES = [TYPE_STRING, TYPE_NUMERIC, TYPE_BOOLEAN, TYPE_LIST]

export const OP_LABELS = {
  [CMD_EQUALS]: "Equals",
  [CMD_NOT_EQUALS]: "Not Equals",
  [CMD_LIKE]: "Like",
  [CMD_NOT_LIKE]: "Not Like",
  [CMD_GREATER_THAN]: ">",
  [CMD_GREATER_AND_EQUAL]: ">=",
  [CMD_LESS_THAN]: "<",
  [CMD_LESS_AND_EQUAL]: "<=",
  [CMD_BETWEEN]: "Between",
}

export const STRING_OPERATORS = [CMD_EQUALS, CMD_NOT_EQUALS, CMD_LIKE, CMD_NOT_LIKE];
export const NUMBER_OPERATORS = [CMD_EQUALS, CMD_NOT_EQUALS, CMD_GREATER_THAN, CMD_GREATER_AND_EQUAL, CMD_LESS_THAN, CMD_LESS_AND_EQUAL];
export const DATE_OPERATORS = [CMD_LESS_THAN, CMD_GREATER_THAN, CMD_BETWEEN];
export const LINK_OPERATORS = [CMD_EQUALS, CMD_NOT_EQUALS, CMD_LIKE, CMD_NOT_LIKE];
export const ALL_OPERATORS = [CMD_EQUALS, CMD_NOT_EQUALS, CMD_LIKE, CMD_NOT_LIKE, CMD_GREATER_THAN, CMD_GREATER_AND_EQUAL, CMD_LESS_THAN, CMD_LESS_AND_EQUAL, CMD_BETWEEN];

export const IF_ALLOWED_FIELD_TYPES = ["Data", "Select", "Link", "Date", "Small Text", "Text", "Int", "Float", "Currency", "Table"];

export const SIDE_LEFT = 'left';
export const SIDE_RIGHT = 'right';

// NOTE: At the time of writing frappe doesn't export defaults correctly. This fixes that issue until
//       a proper fix is pushed.
export default {
  CMD_ARRAY,
  CMD_VAR,
  CMD_VAL,
  CMD_IF,
  CMD_CALL,
  CMD_EQUALS,
  CMD_NOT_EQUALS,
  CMD_LIKE,
  CMD_NOT_LIKE,
  CMD_GREATER_THAN,
  CMD_LESS_THAN,
  CMD_GREATER_AND_EQUAL,
  CMD_LESS_AND_EQUAL,
  CMD_BETWEEN,
  CMD_ADD,
  CMD_SUBTRACT,
  CMD_MULTIPLY,
  CMD_DIVIDE,
  CMD_AND,
  CMD_OR,
  CMD_NOT,
  CMD_XOR,
  CMD_TRUE,
  CMD_FALSE,
  CMD_UNDEFINED,
  CMD_INT,
  CMD_FLOAT,
  CMD_STRING,
  CMD_BOOL,
  CMD_IN,
  CMD_SET,
  CMD_UNSUPPORTED,
  
  TYPE_STRING,
  TYPE_NUMERIC,
  TYPE_BOOLEAN,
  TYPE_LIST,
  TYPE_BLOCK,
  TYPE_EXPRESSION,
  
  TYPES,
  
  OP_LABELS,
  
  STRING_OPERATORS,
  NUMBER_OPERATORS,
  DATE_OPERATORS,
  LINK_OPERATORS,
  
  IF_ALLOWED_FIELD_TYPES,

  SIDE_LEFT,
  SIDE_RIGHT
}