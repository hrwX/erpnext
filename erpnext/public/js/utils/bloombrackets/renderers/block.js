import { Component } from "../component";

export const Block = Component('bb-block', (ui, $container, { cls }) => {
  if ( cls ) {
    $container.addClass(cls);
  }
  $container.removeClass('bb-component');
}, (ui, { block }) => {
  const html = block.map((exp, i) => ui.insertCommandInsert({ 
    block,
    exp,
    order: i,
    has_data: true,
    no_extra_command_insert: true,
    hideRemoveBtn: false,
    fullWidth: true
  })).join('');

  return `
    ${html}
    ${ ui.insertCommandInsert({ block, order: block.length, fullWidth: true })}
  `
});

export default Block;