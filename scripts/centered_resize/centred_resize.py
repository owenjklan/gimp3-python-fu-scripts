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

plugin_procedures = {
    "owenjklan-image-canvas-centered-resize": {
        "label": "Centered Canvas Resize",
        "menu_path": "<Image>/Image/",
        "documentation_title": "Resize image canvas by 25%, centering original content.",
        "documentation_body": "Resize an image canvas by 25% and center the original content."
    },
    "owenjklan-layer-boundary-centered-resize": {
        "label": "Centered Boundary Resize",
        "menu_path": "<Image>/Layer/",
        "documentation_title": "Resize layer boundary by 25%, centering original content.",
        "documentation_body": "Resize a layer boundary by 25% and center the original content."
    }
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

    def owenjklan_layer_boundary_centered_resize(self, procedure, run_mode, image, drawables, config, run_data):
        # Determine new layer size and center offsets
        layers = image.get_selected_layers()
        for layer in layers:
            orig_w = layer.get_width()
            orig_h = layer.get_height()
            new_w = orig_w * 1.25
            new_h = orig_h * 1.25
            off_x = new_w / 2 - orig_w / 2
            off_y = new_h / 2 - orig_h / 2

            layer.resize(new_w, new_h, off_x, off_y)

        success_message = f"Resized boundary of {len(layers)} layers."
        Gimp.message(success_message)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def owenjklan_image_canvas_centered_resize(self, procedure, run_mode, image, drawables, config, run_data):
        # Determine new image size and center offsets
        orig_w = image.get_width()
        orig_h = image.get_height()
        new_w = orig_w * 1.25
        new_h = orig_h * 1.25
        off_x = new_w / 2 - orig_w / 2
        off_y = new_h / 2 - orig_h / 2

        image.resize(new_w, new_h, off_x, off_y)

        success_message = f"Resized image canvas to ({new_w}, {new_h}) and centered original content."
        Gimp.message(success_message)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(CenteredResize.__gtype__, sys.argv)
