import { Component } from "../component";

/**
 * AddRemoveWrapper Component prop object
 * @typedef AddRemoveProps
 * @type {object}
 * @property {array} exp The expression instance related to this component
 * @property {array} options An array of options to display on this component's dropdown
 * @property {string} title A title attribute value to attach to this component's dropdown
 * @property {boolean} open When true the dropdown will be automatically displayed
 * @property {function} onOptionSelected A callback issued when a dropdown item is selected. 
 * @property {function} onDelete A callback issued when the delete button is clicked.
 * @property {function} onInit A callback issued when this component first initializes.
 * @property {int} order The position of this component inside its parent.
 */

/**
 * @callback addRemoveWrapperCallback
 * @param {import('../../bloombrackets_widget').BloomBracketsComponent} ui The BloomBracketsComponent 
 *        app instance.
 * @param {AddRemoveProps} props A property object passed to initialize component
 * @returns {string}
 */

/**
 * Component wrapper that eases implementation of adding and removing components.
 * This component display a + button which further displays a dropdown with custom options.
 * Once this dropdown appears there will be an X button to hide the options again.
 * 
 * When an item in the dropdown is selected, this component will attempt to delete itself from
 * the DOM and in its place will insert HTML returned by the onOptionSelected callback's return value.
 * 
 * @type {addRemoveWrapperCallback}
 */
export const AddRemoveWrapper = Component("bb-addremove", (ui, $container, {
  exp, options, title, open, onOptionSelected, onDelete, onInit, fullWidth = true,
  order, hideRemoveBtn
}) => {
  const $btn_min = $container.find('> .btn-minus');
  const $btn_plus = $container.find('> .bb-actions .btn-plus');
  const $select = $container.find('> .bb-actions select');
  const $actions = $container.find('> .bb-actions');
  const $content = $container.find('> .bb-content');
  const api = {
    selectOption (data) {
      const [contentHtml, insertHtml=undefined] = onOptionSelected(data.value, data);

      if (contentHtml) {
        if ( hideRemoveBtn ) {
          $btn_min.addClass('hidden');
        } else {
          $btn_min.removeClass('hidden');
        }
      
        if ( insertHtml ) {
          const $parent = $container.parent();
          $parent.append($(insertHtml));
        }
        $content.empty().append($(contentHtml));
        $actions.hide();

        setTimeout(() => ui.$wrapper.trigger('bb-init'), 1);
        ui.$wrapper.trigger('bb-script-change');
        return;
      }
    }
  }

  if ( fullWidth ) {
    $container.width('100%');
  }

  if ( hideRemoveBtn ) {
    $btn_min.addClass('hidden');
  }

  /**
   * handles the + button click event. Makes the dropdown and X button available to the user.
   */
  const handleOpenOptions = () => {
    $select.parent().removeClass('hidden');
    $btn_plus.addClass('hidden');
    if ( !hideRemoveBtn ) {
      $btn_min.removeClass('hidden');
    }
  }

  /**
   * Resets display state of this component to only display the + button.
   */
  const handleCloseOptions = () => {
    let success = true;
    if ( onDelete ) {
      success = onDelete($container, exp);
    }

    if ( success ) {
      $select.parent().addClass('hidden');
      $btn_plus.removeClass('hidden');
      $btn_min.addClass('hidden');
    }
  }

  /**
   * handles the dropdown option change event.
   * If the onOptionSelected callback is defined and returns a value. This component will
   * attempt to remove itself and in its place will inject the returned HTML from onOptionSelected.
   */
  const handleSelectChange = () => {
    if (onOptionSelected) {
      const $selected_option = $select.find('option:selected');
      const data = $selected_option.data('option');
      api.selectOption(data);
      $select.val('');
    }
  }

  /**
   * Builds this component's dropdown options from the passed options information.
   */
  const buildOptions = () => {
    $select.find(':disabled').nextAll().remove();

    options.forEach((o) => {
      const $option = $(`<option></option>`);
      $option.data('option', o);
      $option.val(o.value);
      $option.text(o.label);
      if ( o.name ) {
        $option.attr('data-name', o.name);
      }
      if ( o.description ) {
        $option.attr('title', o.description);
      }
      if ( o.cls ) {
        $option.addClass(o.cls);
      }
      $select.append($option);
    });
  }

  // DOM event binds
  $select.on('change', handleSelectChange);
  $btn_plus.on('click', handleOpenOptions);
  $btn_min.on('click', handleCloseOptions);

  // Initialize inserts if already defined
  if ($select.val()) {
    handleSelectChange();
  }

  // open options from the start if defined.
  if (open) {
    handleOpenOptions();
  }

  // kick off option building
  buildOptions();

  // let parent component know when this component was initialized.
  if (onInit) {
    onInit(ui, $container, api);
  }

  // if ( order != undefined ) {
  //   $container.css('order', order);
  // }

}, (ui, { title }) => `
  <i class="btn btn-minus octicon octicon-x hidden"></i>
  <div class="bb-actions">
      <i class="btn btn-plus octicon octicon-plus"></i>
      <div class="bb-control hidden">
        <select title="${title}">
          <option hidden disabled selected value> -- </option>
        </select>
      </div>
    </div>
  <div class="bb-content"></div>
`);
