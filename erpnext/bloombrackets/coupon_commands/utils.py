import frappe

def flat_item_group_tree_list(item_group, result=None):
	if not result:
		result = [item_group]

	child_groups = frappe.get_list(
		"Item Group", 
		filters={"parent_item_group": item_group}, 
		fields=["name"]
	)
	child_groups = [child.name for child in child_groups if child not in result]
	
	if len(child_groups) > 0:
		result = result + child_groups
		for child in child_groups:
			flat_item_group_tree_list(child, result)

	return result