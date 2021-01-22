import { Component } from "../component";
import { auto_size_select } from "../utils";

export const IfThenElse = Component("bb-if bb-line", (ui, { exp, autofocus }) => `
  <div class="bb-line-group">
    <div class="bb-text">IF</div>
    <div class="bb-conditions">
      ${ ui.insertComparisonOperatorSelector({ exp: exp[1], autofocus, reference_exp: exp })}
    </div>
    <div class="bb-text">THEN</div>
  </div>
  <div class="bb-then bb-line-empty">${ ui.insertBlock({ block: exp[2], fullWidth: true })}</div>
  <div class="bb-text">ELSE</div>
  <div class="bb-else bb-line-empty">${ ui.insertBlock({ block: exp[3], fullWidth: true })}</div>
`);

export default IfThenElse;