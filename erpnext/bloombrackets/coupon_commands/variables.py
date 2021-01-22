
def load_variable_meta(meta, for_doctype):
	meta.update({
		"doc": {
			"doctype": for_doctype
		},
		"today": {
			"fieldtype": "Date"
		},
		"True": {
			"fieldtype": "boolean"
		},
		"False": {
			"fieldtype": "boolean"
		}
	})