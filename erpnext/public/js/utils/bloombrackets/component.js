import { gen_id } from "./utils"

/**
 * Simple jquery based component wrapper. Helps to quickly build component based ui.
 * @param {BloomBracketsComponent} ui The Bloombrackest instance
 * @param {function} init A callback function triggered when the component is inserted on dom.
 * @param {function} renderer A callback function expecting html string to insert into dom.
 * @returns A component wrapped in a function. Calling this function will return html for the component.
 */
export function Component(...compArgs) {
  let init = undefined;
  let render = undefined;
  let cls = undefined;
  let first = undefined;
  let last = undefined;
  if (compArgs.length > 2) {
    [cls, init, render] = compArgs;
  } else if (compArgs.length > 1) {
    [first, last] = compArgs;
    if ( typeof first == 'string' ) {
      cls = first;
      render = last;
    } else {
      init = first;
      render = last;
    }
  } else {
    [render] = compArgs;
  }

  return (ui, props) => {
    const id = `bb-component-${gen_id()}`;
    let onInit = init;
    let onRender = render;

    if (ui == undefined) {
      throw new ReferenceError("ui reference is undefined...");
    }

    if (onInit) {
      // Wait for widget to be ready before init
      ui.$wrapper.one('bb-init', () => {
        // Sanity check, only run init once for this component
        if ( onInit ) {
          const $comp = ui.$wrapper.find(`#${id}`);
          onInit(ui, $comp, props, cls);
          onInit = undefined;
        }
      });
    }

    return `
      <div id="${id}" class="bb-component${ cls ? ` ${cls}` : ''}">
        ${onRender(ui, props, cls)}
      </div>
    `
  }
}