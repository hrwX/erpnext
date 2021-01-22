import { Component } from "../component";
import { CMD_IF, CMD_SET, CMD_EQUALS, CMD_UNDEFINED, CMD_CALL, CMD_STRING } from "../constants";
import { AddRemoveWrapper } from "./add_remove";

export const CommandInsert = (ui, {
  block,
  exp,
  open,
  no_void_cmds = false,
  insert_directly = false,
  no_extra_command_insert = false,
  onRef,
  fullWidth = true,
  order,
  has_data = false,
  hideRemoveBtn
}) => {

  /**
   * Handles delete button click on the contained expression
   * @param {*} $container The dom container
   * @param {*} exp The expression to delete
   */
  const handleDelete = ($container) => {
    const exp_idx = block.indexOf(exp);
    if ( exp_idx > -1 ) {
      block.splice(exp_idx, 1);
      $container.remove();
      ui.$wrapper.trigger('bb-script-change');
      return true;
    } else {
      console.warn("Could not delete line: ", exp);
    }

    return false;
  }

  /**
   * Handles command selection change
   * @param {*} cmd The command selected
   * @param {*} opt Selection data
   */
  const handleOptionSelected = (cmd, opt) => {
    let html = undefined;
    let insertHtml = undefined;

    switch (cmd) {
      case CMD_IF:
        if (!has_data) {
          exp = [
            CMD_IF,
            [CMD_EQUALS,
              [CMD_UNDEFINED],
              [CMD_UNDEFINED]
            ],
            [],
            []
          ];
          block.push(exp);
        }
        html = ui.insertIfThenElse({
          exp,
          autofocus: true,
          onRef,
          fullWidth: !insert_directly ? fullWidth : false
        });
        if (no_extra_command_insert == false) {
          insertHtml = ui.insertCommandInsert({ block, open, fullWidth, order: block.length })
        }
        break;
      case CMD_SET:
        if (!has_data) {
          exp = [CMD_SET, CMD_UNDEFINED, [CMD_UNDEFINED]];
          block.push(exp);
        }
        html = ui.insertVarSet({
          exp,
          autofocus: true,
          onRef,
          fullWidth: !insert_directly ? fullWidth : false,
        });
        if (no_extra_command_insert == false) {
          insertHtml = ui.insertCommandInsert({ block, open, fullWidth, order: block.length })
        }
        break;
      case CMD_CALL:
        if (!has_data) {
          if ( !Array.isArray(exp) ) {
            exp = [];
          }

          exp.splice(0);
          exp.push(CMD_CALL, opt.name);
          for (let arg of opt.meta.args) {
            exp.push([CMD_UNDEFINED]);
          }

          if ( !block.find(x => x == exp) ) {
            block.push(exp);
          }        
        } else if ( exp[0] === CMD_UNDEFINED ) {
          exp.splice(0);
          exp.push(CMD_CALL, opt.name);
          for (let arg of opt.meta.args) {
            exp.push([CMD_UNDEFINED]);
          }
        }

        html = ui.insertCustomCommand({
          exp,
          onRef,
          fullWidth: !insert_directly ? fullWidth : false
        });
        if (no_extra_command_insert == false) {
          insertHtml = ui.insertCommandInsert({
            block, open,
            fullWidth: !insert_directly ? fullWidth : false,
            order: block.length
          });
        }
        break;
      default:
        break;
    }

    return [html, insertHtml]
  }

  const options = []

  if (!no_void_cmds) {
    options.push(
      { value: CMD_IF, label: "IF" },
      { value: CMD_SET, label: "SET" }
    );
  }

  for (const custom_cmd of Object.keys(ui.context['#META'])) {
    const custom_cmd_meta = ui.context['#META'][custom_cmd];
    if (no_void_cmds == true && custom_cmd_meta.returns == undefined) {
      continue;
    }

    options.push({
      value: CMD_CALL,
      label: custom_cmd,
      name: custom_cmd,
      title: custom_cmd_meta.description,
      meta: custom_cmd_meta
    });
  }

  return AddRemoveWrapper(ui, {
    block,
    options,
    title: "Select Command",
    open,
    onOptionSelected: handleOptionSelected,
    onDelete: handleDelete,
    fullWidth,
    order,
    hideRemoveBtn,
    onInit: (ui, $container, api) => {
      if (has_data && Array.isArray(exp) && typeof exp[0] === "string") {
        let opt = options.find((o) => o.value == exp[0]);
        if (opt) {
          api.selectOption(opt);
        }
      }
    }
  });
}

export default CommandInsert;