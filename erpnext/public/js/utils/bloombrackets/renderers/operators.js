//const { OP_LABELS } = require('./constants');
import { gen_id } from '../utils';
import { Component } from '../component';
import { ALL_OPERATORS, OP_LABELS } from "../constants";

export const ComparisonOperatorSelector = (ui, { exp, autofocus, reference_exp }) => {
  const ops = ALL_OPERATORS;
  let $containerRef = null;
  let rightApi = undefined;

  const handleRightRef = (ref) => {
    rightApi = ref;
  }

  const handleLeftChange = (exp, meta) => {
    $containerRef.find('.bb-control').trigger('bb-change', [exp, meta, 'left']);
    if ( rightApi ) {
      rightApi.updateFieldType(meta.fieldtype);
    }
  }

  const initializeOperator = () => {
    
  }

  return Component((ui, $container) => {
    const $select = $container.find('.bb-operator:first select');
    $containerRef = $container;

    $select.on('change', () => {
      if (!$select.hasClass('hidden')) {
        // update expression operator command
        exp[0] = $select.val();
        ui.$wrapper.trigger('bb-script-change');
      }
    });

    initializeOperator();
  }, (ui) => {
    const options = ops.map((op, i) => `<option ${(exp[0] == op) ? 'selected' : ''} value="${op}">${OP_LABELS[op]}</option>`).join('');

    return `
      <div class="bb-left">
        ${ ui.insertExpressionInsert({
          exp: exp[1],
          autofocus, 
          open: true, 
          onChange: handleLeftChange
        })}
      </div>
      <div class="bb-control bb-operator">
        <select>${options}</select>
      </div>
      <div class="bb-right">
        ${ ui.insertExpressionInsert({
          exp: exp[2], 
          autofocus: undefined, 
          open: true, 
          ref: handleRightRef
        })}
      </div>
      <div class="bb-group bb-between hidden">
        <div class="bb-text">AND</div>
        <div class="bb-right2"></div>
      </div>
    `;
  })(ui);
}

export default ComparisonOperatorSelector;