import { Component } from "../component";
import { auto_size_select, get_meta } from "../utils";
import { IF_ALLOWED_FIELD_TYPES, CMD_VAR } from "../constants";

export const Variable = Component((ui, $container, { exp, autofocus, onChange }) => {
  const $select = $container.find('select');
  const $fields = $container.find('.bb-fields');
  let doctype = undefined;
  if (exp.length > 1) {
    doctype = ui.context['#VARMETA'][exp[1]].doctype;
  }

  const variableFieldSelectHandle = (position, selection, meta) => {
    // Remove all fields to the right of this one as they are invalid now.
    $fields.children().eq(position - 2).nextAll().remove();

    // Insert doctype fields if THIS field is a link to another doctype.
    if (meta.fieldtype === "Link") {
      $fields.children().eq(position - 2).after(VariableField(ui, { 
        exp, 
        position: position + 1, 
        doctype: meta.options, 
        autofocus: true, 
        onFieldChange: variableFieldSelectHandle
      }));
      ui.$wrapper.trigger('bb-init');
    }

    if ( onChange ) {
      onChange(exp, meta);
    }
  }

  const handleSelectChange = () => {
    const selection = $select.val();
    const $selected_option = $select.find(':selected');
    const doctype = $selected_option.attr('data-doctype');
    const fieldtype = $selected_option.attr('data-fieldtype');
    const fieldname = selection;
    const meta = {
      fieldtype: $selected_option.attr('data-fieldtype'),
      fieldname: selection,
      label: selection,
      options: $selected_option.attr('data-doctype')
    }
    $selected_option.data('meta', meta);

    // set variable name
    exp.splice(1);
    exp.push(fieldname)

    // Empty field selections every time the user changes var
    $fields.empty();
    if (doctype) {
      $fields.append(VariableField(ui, {
        exp, 
        position: 2, 
        doctype: meta.options,
        title: fieldname, 
        autofocus: true, 
        onFieldChange: variableFieldSelectHandle
      }));
      ui.$wrapper.trigger('bb-init');
    }

    $select.attr('title', `VAR ${$selected_option.attr('title')}`);

    auto_size_select($container, $select, $selected_option);
    if ( onChange ) {
      onChange(exp, meta);
    }

    $container.trigger('bb-script-change');
  }

  const buildVariableList = () => {
    const selected = exp.length > 1 ? exp[1] : undefined;
    const options = ui.list_vars().map((v) => {
      const meta = ui.context['#VARMETA'][v];
      return $(`<option class="${meta.doctype ? 'doctype' : ''}" data-fieldtype="${meta.fieldname || ''}" data-doctype="${meta.doctype || ''}" title="${v}" value="${v}">${v}</option>`);
    });
  
    if (!selected) {
      options.unshift($('<option hidden disabled value selected> -- </option>'));
    }

    $select.empty().append(options);
    $select.val(selected);

    if ( selected ) {
      auto_size_select($container, $select, $select.find(':selected'));
    }
  }

  const handleVariableRename = (e, oldName, newName) => {
    if ( exp[1] == oldName ) {
      exp[1] = newName
    }

    buildVariableList();
  }

  // Bind events
  $select.on('change', handleSelectChange);
  ui.$wrapper.on('bb-var-rename', handleVariableRename);

  if (autofocus) {
    $select.focus();
  }

  // insert variable options
  buildVariableList();

  // prime fields if values are set
  if (exp.length > 1) {
    let fields = exp.slice(2).map((x, i) => VariableField(ui, {
      exp, 
      position: i, 
      doctype, 
      selected: x, 
      title: x, 
      autofocus: false, 
      onFieldChange: variableFieldSelectHandle
    })).join('');
    $fields.append(fields);
    ui.$wrapper.trigger('bb-init');
  }
}, (ui, { exp }) => {
  if (exp[0] !== CMD_VAR) {
    throw new Error(`Expression is not a variable: ${exp}`);
  }

  return `
    <div class="bb-variable">
      <div class="bb-control bb-dropdown bb-var">
        <select></select>
      </div>
      <div class="bb-fields"></div>
    </div>
`;
});

export const VariableField = Component("bb-control bb-dropdown loading", 
async function (ui, $container, {
  exp, position, doctype, selected, title, autofocus, onFieldChange
}) {
  // Fetch meta info about this field
  const response = await get_meta(doctype);
  const meta = response.message;

  // build field options
  const field_option = (field) => {
    const $option = $(`<option>${field.label || field.fieldname}</option>`);
    $option.attr('title', `(${field.fieldtype == 'Link' ? `${field.options} ` : ''}${field.fieldtype}) ${field.label || field.fieldname}${field.description ? ':' + field.description : ''}`);
    $option.attr('value', field.fieldname);
    $option.data('meta', field);
    $option.prop('selected', field.fieldname == selected);
    if (field.fieldtype == 'Link') {
      $option.addClass('bb-doctype');
    }
    return $option;
  }

  const field_label_alphabetical_sort = (a, b) => {
    const left = (a.label || '').toUpperCase();
    const right = (b.label || '').toUpperCase();
    return (left < right) ? -1 : (left > right) ? 1 : 0;
  }

  const filed_allowed_types_filter = (field) => IF_ALLOWED_FIELD_TYPES.includes(field.fieldtype);

  // We only support a subset of field types. Filter out the ones we can't handle
  const options = meta.fields
    .filter(filed_allowed_types_filter)
    .sort(field_label_alphabetical_sort)
    .map(field_option);

  if (!selected) {
    options.unshift($('<option hidden disabled selected value> -- </option>'));
  }

  const $select = $(`<select></select>`);
  const $control = $container;

  const handleFieldChange = () => {
    const selection = $select.val();
    const $selected_option = $select.find(':selected');
    const meta = $selected_option.data('meta');
    // set field name
    exp.splice(position);
    exp.push(selection)

    if (onFieldChange) {
      onFieldChange(position, selection, meta);
    }

    // used to colorize dropdown for doctype values
    if ($selected_option.hasClass('bb-doctype')) {
      $select.closest('.bb-dropdown').addClass('bb-doctype');
    } else {
      $select.closest('.bb-dropdown').removeClass('bb-doctype');
    }

    $select.attr('title', $selected_option.attr('title'));
    auto_size_select($container, $select, $select.find(':selected'));
    $container.trigger('bb-script-change');
  };

  // set fields
  $select.attr('title', title);
  $select.append(options)

  // finally attach field on DOM
  $control.append($select);
  $control.removeClass('loading');

  // bindings
  $select.on('change', handleFieldChange);

  if (autofocus) {
    $select.focus();
  }
}, () => '')