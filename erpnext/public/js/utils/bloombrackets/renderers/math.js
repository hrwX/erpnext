import { Component } from "../component";
import { auto_size_select } from "../utils";
import { 
  CMD_ADD,
  CMD_SUBTRACT, 
  CMD_MULTIPLY, 
  CMD_DIVIDE, 
  CMD_UNDEFINED, 
  SIDE_LEFT, 
  SIDE_RIGHT 
} from "../constants";

export const MathExp = Component((ui, $container, {
  exp, onChange
}) => {
  const $left = $container.find('> .bb-left');
  const $right = $container.find('> .bb-right');
  const $op = $container.find('> .bb-control > .bb-math-op');
  const refs = {
    [SIDE_LEFT]: undefined,
    [SIDE_RIGHT]: undefined
  }
  const refHandlers = {
    [SIDE_LEFT]: (ref) => refs[SIDE_LEFT] = ref,
    [SIDE_RIGHT]: (ref) => refs[SIDE_RIGHT] = ref
  }

  const handleMathOpChange = () => {
    exp[0] = $op.val();
    auto_size_select($container, $op, $op.find(':selected'));
    ui.$wrapper.trigger('bb-script-change');
  }

  const handleValueChange = (side, $parent, side_exp) => {
    if ( onChange ) {
      onChange(exp);
    }
  }

  const insertExpressionComponent = ($parent, exp, side) => {
    $parent.empty().append(
      ui.insertExpressionInsert({
        exp,
        autofocus: undefined, 
        open: true, 
        onChange: () => handleValueChange(side, $parent, exp),
        ref: refHandlers[side]
      })
    );
    ui.$wrapper.trigger('bb-init');
  }

  $op.on('change', handleMathOpChange);

  const insertLeftComponent = () => insertExpressionComponent($left, exp[1], SIDE_LEFT);
  const insertRightComponent = () => insertExpressionComponent($right, exp[2], SIDE_RIGHT);

  insertLeftComponent();
  insertRightComponent();

  if ( exp[0] !== CMD_UNDEFINED ) {
    $op.val(exp[0]);
  }

}, (ui, exp) => `
  <div class="bb-text">(</div>
  <div class="bb-left"></div>
  <div class="bb-control">
    <select class="bb-math-op">
      <option value selected hidden disabled> -- </option>
      <option value="${CMD_ADD}">+</option>
      <option value="${CMD_SUBTRACT}">-</option>
      <option value="${CMD_MULTIPLY}">*</option>
      <option value="${CMD_DIVIDE}">/</option>
    </select>
  </div>
  <div class="bb-right"></div>
  <div class="bb-text">)</div>
`)