import { Component } from "../component";
import { resolve_type } from "../utils";

export const Expression = Component((ui, { exp, autofocus }) => {
  const exp_type = resolve_type(exp);

  switch (exp[0]) {
    case CMD_IF: return ui.insertIfThenElse({ exp, autofocus }); break;
    case CMD_UNDEFINED: return ui.insertExpressionInsert({ exp }); break;
    default:
      return '';
  }
})

export default Expression;