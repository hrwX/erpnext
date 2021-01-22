import {
  CMD_ARRAY,
  TYPE_NUMERIC,
  TYPE_BOOLEAN,
  TYPE_STRING,
  TYPE_LIST,
  TYPE_BLOCK,
  TYPE_EXPRESSION
} from "./constants";

/**
 * Resizes select element to fit its selection option label.
 * @param {*} $parent The select parent where to insert temporary select.
 * @param {*} $select The select element to resize.
 * @param {*} $option The option to use to resize select element.
 */
export function auto_size_select($parent, $select, $option) {
  const $clone = $select.clone();
  $clone.empty();
  $clone.append($option.clone());
  $clone.css({
    display: 'none',
    maxWidth: 'unset',
    width: 'unset'
  });
  $parent.append($clone);
  $select.css({
    width: `${$clone.width()}px`,
    maxWidth: 'unset'
  });
  $clone.remove();
}

let id_count = 0;
export function gen_id() {
  return ++id_count;
}

const meta_cache = new Map();
export async function get_meta(doctype) {
  if (meta_cache.has(doctype)) {
    return await meta_cache.get(doctype)
  }

  const meta = frappe.call({
    method: "erpnext.bloombrackets.utils.get_meta",
    args: {
      doctype
    },
    freeze: true
  });

  meta_cache.set(doctype, meta);

  return await meta;
}

export function resolve_type(value) {
  if (isNaN(value)) {
    return TYPE_NUMERIC;
  } else if (typeof value == "boolean") {
    return TYPE_BOOLEAN
  } else if (typeof value == "string" || value instanceof String) {
    return TYPE_STRING
  } else if (Array.isArray(value)) {
    if (value[0] == CMD_ARRAY) {
      return TYPE_LIST
    } else if (Array.isArray(value[0]) == "array") {
      return TYPE_BLOCK
    } else {
      return TYPE_EXPRESSION
    }
  }

  return null;
}

export default {};