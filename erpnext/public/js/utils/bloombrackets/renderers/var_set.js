import { Component } from "../component";
import { CMD_UNDEFINED } from "../constants";

export const VarSet = (ui, { exp, autofocus, fullWidth }) => {
  let varName = exp[1];
  let $containerRef = null;

  if ( exp[2] === undefined ) {
    exp.push([CMD_UNDEFINED]);
  }

  const handleRightChange = (e, value) => {
    // exp[2] = value;

    // if ( varName != CMD_UNDEFINED ) {
    //   ui.$wrapper.trigger('bb-var-set', [varName, exp[2]]);
    // }
    // ui.$wrapper.trigger('bb-script-change');
  }
  
  return Component("bb-line", (ui, $container) => {
    $containerRef = $container;
    const $varName = $container.find('.var-name');
    const $varValue = $container.find('.var-value');

    $varName.on('change', () => {
      let oldVarName = varName;
      varName = exp[1] = ($varName.val() || '').replace(' ', '');
      $varName.val(varName);

      // Remove old variable name
      if ( oldVarName != CMD_UNDEFINED ) {
        delete ui.context['#VARMETA'][oldVarName];
      }

      ui.context['#VARMETA'][varName] = exp[1];
      if ( oldVarName != CMD_UNDEFINED && oldVarName != varName ) {
        ui.$wrapper.trigger('bb-var-rename', [oldVarName, varName]);
      }

      if ( varName && varName != CMD_UNDEFINED ) {
        $varName.closest('.bb-control').removeClass('bb-error');
      } else {
        $varName.closest('.bb-control').addClass('bb-error');
      }
      ui.$wrapper.trigger('bb-script-change');
    });

    if ( exp[1] !== CMD_UNDEFINED ) {
      $varName.val(exp[1]);
    } else if ( autofocus ) {
      $varName.closest('.bb-control').addClass('bb-error');
      $varName.focus();
    }
  }, (ui) => `
    <div class="bb-text">SET</div>
    <div class="bb-control">
      <input type="text" class="var-name" />
    </div>
    <div class="bb-text">=</div>
    ${ ui.insertExpressionInsert({
      exp: exp[2],
      autofocus: undefined, 
      open: true, 
      onChange: handleRightChange,
    })}
  `)(ui);
}