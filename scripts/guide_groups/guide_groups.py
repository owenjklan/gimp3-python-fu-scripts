#!/usr/bin/env python3

###
# This was created with guidance from the following links:
# - https://testing.docs.gimp.org/3.0/en/gimp-using-python-plug-in-tutorial.html
#
# GIMP 3.0 Plugin that will register two functions:
# - Resize image canvas by 25% and centered
# - Resize layer boundary by 25% and centered

import sys

import gi

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GLib

MENU_PATH = "<Image>/Image/Guide Groups/"

plugin_procedures = {
    "owenjklan-add-guide-groups-edges": {
        "label": "Add edges",
        "menu_path": MENU_PATH,
        "documentation_title": "Add guides at all edges",
        "documentation_body": "Add guides at all edges"
    },
    "owenjklan-remove-guide-groups-edges": {
        "label": "Remove edges",
        "menu_path": MENU_PATH,
        "documentation_title": "Remove guides at all edges",
        "documentation_body": "Remove guides at all edges"
    },
    "owenjklan-add-guide-groups-halves": {
        "label": "Add halves",
        "menu_path": MENU_PATH,
        "documentation_title": "Add horizontal and vertical guide at 50%",
        "documentation_body": "Add horizontal and vertical guide at 50%"
    },
    "owenjklan-remove-guide-groups-halves": {
        "label": "Remove halves",
        "menu_path": MENU_PATH,
        "documentation_title": "Remove horizontal and vertical guide at 50%",
        "documentation_body": "Remove horizontal and vertical guide at 50%"
    },
    "owenjklan-add-guide-groups-thirds": {
        "label": "Add thirds",
        "menu_path": MENU_PATH,
        "documentation_title": "Add horizontal and vertical guides at 33% and 66%",
        "documentation_body": "Add horizontal and vertical guides at 33% and 66%"
    },
    "owenjklan-remove-guide-groups-thirds": {
        "label": "Remove thirds",
        "menu_path": MENU_PATH,
        "documentation_title": "Remove horizontal and vertical guides at 33% and 66%",
        "documentation_body": "Remove horizontal and vertical guides at 33% and 66%"
    },
    "owenjklan-add-guide-groups-quarters": {
        "label": "Add quarters",
        "menu_path": MENU_PATH,
        "documentation_title": "Add horizontal and vertical guides at 25%, 50% and 75%",
        "documentation_body": "Add horizontal and vertical guides at 25%, 50% and 75%"
    },
    "owenjklan-remove-guide-groups-quarters": {
        "label": "Remove quarters",
        "menu_path": MENU_PATH,
        "documentation_title": "Remove horizontal and vertical guides at 25%, 50% and 75%",
        "documentation_body": "Remove horizontal and vertical guides at 25%, 50% and 75%"
    },
    "owenjklan-list-guides": {
        "label": "List (Debug to Console)",
        "menu_path": MENU_PATH,
        "documentation_title": "Dump image guides",
        "documentation_body": "Dump image guides"
    },
}

class CenteredResize (Gimp.PlugIn):
    def do_query_procedures(self):
        return [ func_name for func_name in plugin_procedures.keys() ]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):
        procedure_details = plugin_procedures[name]
        procedure_func = self.__getattribute__(name.replace("-", "_"))

        procedure = Gimp.ImageProcedure.new(
            self, name, Gimp.PDBProcType.PLUGIN,
            procedure_func, None
        )

        procedure.set_image_types("*")

        procedure.set_menu_label(procedure_details["label"])
        procedure.add_menu_path(procedure_details["menu_path"])

        procedure.set_documentation(
            procedure_details["documentation_title"],
            procedure_details["documentation_body"],
            name
        )
        procedure.set_attribution("Owen Klan", "Owen Klan", "2024")

        return procedure

    def add_guides_at_percentages(self, image, positions):
        image_width = image.get_width()
        image_height = image.get_height()

        for percent_pos in positions:
            h_guide = image_height * (percent_pos / 100.0)
            v_guide = image_width * (percent_pos / 100.0)

            image.add_hguide(h_guide)
            image.add_vguide(v_guide)

    def owenjklan_list_guides(self, procedure, run_mode, image, drawables, config, run_data):
        orientation_chars = {
            Gimp.OrientationType.HORIZONTAL: "H",
            Gimp.OrientationType.VERTICAL: "V",
            Gimp.OrientationType.UNKNOWN: "U",
        }

        h_guides = []
        v_guides = []

        guide_id = image.find_next_guide(0)
        while guide_id != 0:
            orientation = image.get_guide_orientation(guide_id)
            position = image.get_guide_position(guide_id)
            if orientation == Gimp.OrientationType.HORIZONTAL:
                h_guides.append((guide_id, position))
            elif orientation == Gimp.OrientationType.VERTICAL:
                v_guides.append((guide_id, position))

            guide_id = image.find_next_guide(guide_id)
        print("Existing Guide dump")
        print("Vertical Guides:")
        for guide_id, position in sorted(v_guides, key=lambda x: x[1]):
            print(f"ID: {guide_id:>2} @ {position:>4}px")

        print("Horizontal Guides:")
        for guide_id, position in sorted(h_guides, key=lambda x: x[1]):
            print(f"ID: {guide_id:>2} @ {position:>4}px")

        print()
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def remove_guides_at_percentages(self, image, positions):
        image_width = image.get_width()
        image_height = image.get_height()
        pixel_h_positions = set([image_height * (pos / 100.0) for pos in positions])
        pixel_w_positions = set([image_width * (pos / 100.0) for pos in positions])

        guide_id = image.find_next_guide(0)  # Find the first guide

        while guide_id != 0:
            # Check the guide orientation
            orientation = image.get_guide_orientation(guide_id)
            position = image.get_guide_position(guide_id)
            if orientation == Gimp.OrientationType.HORIZONTAL:
                if position in pixel_h_positions:
                    # Get the next guide before we delete the current one
                    next_guide_id = image.find_next_guide(guide_id)
                    image.delete_guide(guide_id)
                    print(f"(id: {guide_id}) H-Guide removed from {position} px")
                    guide_id = next_guide_id
                    pixel_h_positions.remove(position)
            elif orientation == Gimp.OrientationType.VERTICAL:
                if position in pixel_w_positions:
                    # Get the next guide before we delete the current one
                    next_guide_id = image.find_next_guide(guide_id)
                    image.delete_guide(guide_id)
                    print(f"(id: {guide_id}) V-Guide removed from {position} px")
                    guide_id = next_guide_id
                    pixel_w_positions.remove(position)
            else:
                guide_id = image.find_next_guide(guide_id)
                print(f"Guide with UNKNOWN Orientation (id: {guide_id})")

    def owenjklan_add_guide_groups_edges(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [0, 100]
        self.add_guides_at_percentages(image, positions)
        success_message = f"Added guides around edges"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_remove_guide_groups_edges(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [0, 100]
        self.remove_guides_at_percentages(image, positions)
        success_message = f"Removed guides around edges"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_add_guide_groups_halves(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [50]
        self.add_guides_at_percentages(image, positions)
        success_message = f"Added guides at halves"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_remove_guide_groups_halves(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [50]
        self.remove_guides_at_percentages(image, positions)
        success_message = f"Removed guides at halves"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_add_guide_groups_thirds(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [33, 66]
        self.add_guides_at_percentages(image, positions)
        success_message = f"Added guides at thirds"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_remove_guide_groups_thirds(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [33, 66]
        self.remove_guides_at_percentages(image, positions)
        success_message = f"Removed guides at thirds"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_add_guide_groups_quarters(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [25, 50, 75]
        self.add_guides_at_percentages(image, positions)
        success_message = f"Added guides at quarters"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_remove_guide_groups_quarters(self, procedure, run_mode, image, drawables, config, run_data):
        positions = [25, 50, 75]
        self.remove_guides_at_percentages(image, positions)
        success_message = f"Removed guides at quarters"
        Gimp.message(success_message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(CenteredResize.__gtype__, sys.argv)
