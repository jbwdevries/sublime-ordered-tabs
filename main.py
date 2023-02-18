from typing import Tuple

import sublime
import sublime_plugin

OT_SETTINGS = None

def sheet_key(sheet: 'Sheet') -> 'Tuple[str, str, str]':
	return view_key(sheet.view())

def view_key(view: 'View') -> 'Tuple[str, str, str]':
	return (view.file_name().lower() or '', )

def sort_sheets(window: 'Window') -> None:
	"""
	Sorts the sheets of the given window
	"""
	global OT_SETTINGS

	break_preview_on_click = OT_SETTINGS.get('break_preview_on_click', False)

	sheet_list = window.sheets()
	sheet_list = sorted(sheet_list, key=sheet_key)

	# Sorting messes up the focus
	# So store the old focus
	active_sheet = window.active_sheet()

	for idx, sheet in enumerate(sheet_list):
		if not break_preview_on_click and (sheet.is_transient() or sheet.is_semi_transient()):
			# Do not set the index of a transient sheet; this will
			# cause the sheet to stop being transient
			# Since we set the index of all other sheets,
			# the transient sheet should end up at the right place anyhow.
			continue

		window.set_sheet_index(sheet, sheet.group(), idx)

	# Restore the old focus
	window.focus_sheet(active_sheet)

def sort_views(window: 'Window') -> None:
	"""
	Sorts the views of the given window
	"""
	view_list = window.views(include_transient=True)
	view_list = sorted(view_list, key=view_key)

	# Sorting messes up the focus
	# So store the old focus
	active_view = window.active_view()

	for idx, view in enumerate(view_list):
		window.set_view_index(view, 0, idx)

	# Restore the old focus
	window.focus_view(active_view)

class OrderExistingTabsCommand(sublime_plugin.WindowCommand):
	def run(self):
		window = self.window

		if window.num_groups() > 1:
			print('OrderedTabs does not know how to deal with multiple groups')
			return

		sort_sheets(window)

class OrderedTabsEventListener(sublime_plugin.EventListener):
	def on_load(self, view: 'View') -> None:
		sort_sheets(view.window())

	# def on_post_save(self, view: 'View') -> None:
	# 	# After a view is saved, the path may have changed
	# 	sort_sheets(view.window())

def plugin_loaded():
	global OT_SETTINGS

	OT_SETTINGS = sublime.load_settings('OrderedTabs.sublime-settings')

def plugin_unloaded():
	pass # Nothing to do
