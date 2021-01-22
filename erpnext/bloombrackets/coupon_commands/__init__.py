import frappe

def build_context(ctx, for_doctype, skip_meta):
	build_coupon_commands(ctx, for_doctype)
	build_coupon_vars(ctx, for_doctype)
	if not skip_meta:
		build_coupon_meta(ctx, for_doctype)
		build_coupon_var_meta(ctx, for_doctype)

def build_coupon_commands(ctx, for_doctype):
	ctx.update({ "#CALLS": ctx.get("#CALLS", {}) })
	call_hooks("coupon_brackets_extend_commands", commands=ctx["#CALLS"], for_doctype=for_doctype)

def build_coupon_vars(ctx, for_doctype):
	ctx.update({ "#VARS": ctx.get("#VARS", {}) })
	ctx.get("#VARS").update({
		"True": True,
		"False": False
	})
	call_hooks("coupon_brackets_extend_vars", script_vars=ctx["#VARS"], for_doctype=for_doctype)

def build_coupon_meta(ctx, for_doctype):
	ctx.update({ "#META": ctx.get("#META", {}) })
	call_hooks("coupon_brackets_extend_meta", meta=ctx["#META"], for_doctype=for_doctype)

def build_coupon_var_meta(ctx, for_doctype):
	ctx.update({ "#VARMETA": ctx.get("#VARMETA", {}) })
	call_hooks("coupon_brackets_extend_vars_meta", meta=ctx["#VARMETA"], for_doctype=for_doctype)

def call_hooks(hook, *args, **kwargs):
	hooks = frappe.get_hooks(hook) or []
	for method in hooks:
		frappe.call(method, *args, **kwargs)

