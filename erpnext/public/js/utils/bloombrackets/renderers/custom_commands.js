import { Component } from "../component";
import { CMD_UNDEFINED } from "../constants";

export const CustomCommand = Component((ui, $container, { 
  exp, fullWidth 
}) => {
  const $argsContainer = $container.find('> .bb-args');
  const cmd = exp[1];
  const cmd_meta = ui.context["#META"][cmd];

  if ( fullWidth ) {
    $container.addClass('bb-line');
  }

  if ( cmd_meta && cmd_meta.description ) {
    $container.find('> .bb-line').attr('title', cmd_meta.description);
  }

  const buildArguments = () => {
    $argsContainer.empty();
    for(let i = 0; i < cmd_meta.args.length; i++ ) {
      const arg = cmd_meta.args[i];
      if ( exp[2 + i] == undefined ) {
        exp.push([CMD_UNDEFINED]);
      }

      const html = ui.insertExpressionInsert({
        exp: exp[2 + i], 
        autofocus: i == 0, 
        open: true,
        exp_meta: arg
      });
      $argsContainer.append(html);
    }

    ui.$wrapper.trigger('bb-init');
    ui.$wrapper.trigger('bb-script-change');
  }

  buildArguments();
}, (ui, { exp }) => `
  <div class="bb-text">${exp[1]} (</div>
  <div class="bb-args"></div>
  <div class="bb-text">)</div>
`);

export default CustomCommand;