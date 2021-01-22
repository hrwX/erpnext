import frappe
from erpnext.bloombrackets.commands import COMMANDS
from erpnext.bloombrackets.constants import CMD_UNSUPPORTED, CMD_ARRAY
from erpnext.bloombrackets.types import *
from frappe.model.document import Document

def run_script(script, ctx):
	"""Executes a block of bloombracket expressions one line at a time.
	
	Params:
		script: list -> An expression list
		ctx: dict -> The script context. Stores variables and helper methods used during processing.
	"""
	for statement in script:
		resolve_expression(statement, ctx)

def resolve_expression(expression, ctx):
	"""Bloombracket's script kernel. All processing, validation and variable resolutions
	are processed here
	
	Params:
		expression: list -> An expression represented in a list. Where the first value in the
							list represents a command and all other values are arguments to that
							command.
		ctx: dict -> The script context. Stores variables and helper methods used during processing.

	Returns:
		A result arrived by processing the expression. This is dependent on the command passed into
		the expression.
	
	"""

	expression_type = resolve_type(expression)

	ctx.update({
		"#RUN": lambda script: run_script(script, ctx),
		"#VAR": lambda path: resolve_variable(path, ctx),
		"#VARS": ctx.get("#VARS", {})
	})

	if expression_type == TYPE_EXPRESSION:
		cmd = expression[0]
		args = [ resolve_expression(arg, ctx) for arg in expression[1:] ]

		fn = COMMANDS.get(cmd, CMD_UNSUPPORTED)
		if fn == CMD_UNSUPPORTED:
			args = cmd

		result = fn(args, ctx)
		return result
	elif expression_type == TYPE_LIST:
		args = [ resolve_expression(arg, ctx) for arg in expression[1:] ]

		return args
	else:
		return expression

def resolve_type(value):
	"""Resolves data types of passed values. Internally called to distinguish expressions from data.
	
	Params:
		value: * -> A value to test its type.

	Returns:
		The value type as understood by bloom brackets
	"""

	if type(value) == int or type(value) == float:
		return TYPE_NUMERIC
	elif type(value) == bool:
		return TYPE_BOOLEAN
	elif isinstance(value, str):
		return TYPE_STRING
	elif isinstance(value, list):
		if value[0] == CMD_ARRAY:
			return TYPE_LIST
		elif isinstance(value[0], list):
			return TYPE_BLOCK
		else:
			return TYPE_EXPRESSION

	return None

def resolve_variable(path, context):
	"""Resolves a variable stored in the script's context. In the cases where the variable is
	a dictionary you can pass more path parts to resolve further into the dictionary. Likewise,
	for doctypes, any Link fields will be resolved and further paths can drill into linked documents
	
	Params:
		path: string list -> A list of strings defining a variable path
		context: dict -> The script's context. Variables and helper methods are stored here.

	Returns:
		The resolved value of the variable or dictionary/document drilldown
	
	"""

	if isinstance(path, str):
		path = [path]

	value = context.get("#VARS")

	for key in path:
		doc = None
		field_meta = None
		if isinstance(value, Document):
			doc = value
			field_meta = value.meta.get_field(key)

		if field_meta and field_meta.fieldtype == "Link":
			value = frappe.get_doc(field_meta.options, value.get(key))
		else:
			value = value.get(key)
			value_type = resolve_type(value)

	return value