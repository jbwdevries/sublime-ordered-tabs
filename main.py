from typing import Tuple

import sublime
import sublime_plugin

OT_SETTINGS = None

def sheet_key(sheet: 'Sheet') -> 'Tuple[str, str, str]':
	return view_key(sheet.view())

def view_key(view: 'View') -> 'Tuple[str, str, str]':
	file_name = view.file_name() or ''
	return (file_name.lower(), )

def sort_sheets(window: 'Window') -> None:
	"""
	Sorts the sheets of the given window
	"""
	global OT_SETTINGS

	sheet_list = window.sheets()
	sheet_list = sorted(sheet_list, key=sheet_key)

	# Sorting messes up the focus
	# So store the old focus
	active_sheet = window.active_sheet()

	# Find if there's a transient sheet
	# This is also known as 'preview on click'
	# We need to special case this
	semi_transient_sheet_list = [x for x in sheet_list if x.is_semi_transient()]
	if len(semi_transient_sheet_list) > 1:
		sys.stderr.write('Do not understand how to deal with multiple semi transient windows')
		return

	if not semi_transient_sheet_list:
		# When there are no semi-transient sheets, it's easy
		# Just set the index for each sheet
		for idx, sheet in enumerate(sheet_list):
			window.set_sheet_index(sheet, sheet.group(), idx)
	else:
		# When there are semi-transient sheets, it's tricky
		# Because setting the index on a transient sheet makes it
		# non-transient.
		# So we have to set the index for all sheets, EXCEPT
		# the transient one
		# To make this stable, we first order all the sheets
		# before the transient sheet ordered from left to right,
		# and then the sheets after the transient sheet ordered
		# from right to left. This makes the sorting stable.

		# len(semi_transient_sheet_list) == 1
		semi_transient_sheet = semi_transient_sheet_list[0]
		semi_transient_sheet_index = sheet_list.index(semi_transient_sheet)

		index_list = list(enumerate(sheet_list))

		for idx, sheet in index_list[:semi_transient_sheet_index]:
			window.set_sheet_index(sheet, sheet.group(), idx)

		for idx, sheet in reversed(index_list[semi_transient_sheet_index + 1:]):
			window.set_sheet_index(sheet, sheet.group(), idx)

	# Restore the old focus
	window.focus_sheet(active_sheet)

class OrderExistingTabsCommand(sublime_plugin.WindowCommand):
	def run(self):
		window = self.window

		if window.num_groups() > 1:
			print('OrderedTabs does not know how to deal with multiple groups')
			return

		sort_sheets(window)

class OrderedTabsEventListener(sublime_plugin.EventListener):
	def on_new(self, view: 'View') -> None:
		"""
		Called when a new file is created.

		Sort to make sure the file is on the left
		"""
		sort_sheets(view.window())

	def on_load(self, view: 'View') -> None:
		"""
		Called when the file is finished loading.

		We sort the tabs whenever a new file is loaded
		"""
		if view.sheet().is_transient():
			return

		sort_sheets(view.window())

	def on_post_save(self, view: 'View') -> None:
		"""
		Called after a view has been saved.

		The path may have changed, so we sort again
		"""
		sort_sheets(view.window())

def plugin_loaded():
	global OT_SETTINGS

	OT_SETTINGS = sublime.load_settings('OrderedTabs.sublime-settings')

def plugin_unloaded():
	pass # Nothing to do
