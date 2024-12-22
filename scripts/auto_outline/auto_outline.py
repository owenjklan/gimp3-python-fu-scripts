#!/usr/bin/env python3

###
# This was created with guidance from the following links:
# - https://testing.docs.gimp.org/3.0/en/gimp-using-python-plug-in-tutorial.html
#
# GIMP 3.0 Plugin that will:
#
# - Use the "Alpha to selection" on a layer
# - Grow the selection by 3 pixels
# - Apply the "Stroke selection" for 6 pixels
#
# This is to make outlining layers in thumbnails etc. far easier
# ie: Able to be bound to a shortcut / Stream Deck button.

import sys
import time

import gi

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GLib


class AutoOutline (Gimp.PlugIn):
    def do_query_procedures(self):
        return [ "owenjklan-auto-outline" ]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("RGBA")  # Require RGB and Alpha channel

        procedure.set_menu_label("Auto-outline")
        procedure.add_menu_path('<Image>/Layer/')

        procedure.set_documentation("Auto-outline plug-in",
                                    "This plug-in automatically applies a stroke outline around the contents of"
                                    " a layer. Uses 'Alpha to Selection' to perform the selection.",
                                    name)
        procedure.set_attribution("Owen Klan", "Owen Klan", "2024")

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        selected_layers = image.get_selected_layers()

        if len(selected_layers) != 1:
            Gimp.message("Auto-outline only works for a single layer.")
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

        # Push the current context
        if not Gimp.context_push():
            Gimp.message("Auto-outline failed to push context!")
            return procedure.new_return_values(Gimp.PDBStatusType.FAILED, GLib.Error())

        layer = selected_layers[0]

        # As of 22nd Dec. 2024, it appears that Gimp.Unit.pixel() is broken.
        # So, we determine the pixels to points then set the line width unit
        # to points
        LINE_WIDTH_IN_PIXELS = 6.0

        # We need to obtain the image DPI for the pixels-to-points conversion
        _, x_resolution, y_resolution = image.get_resolution()
        line_width_in_points = Gimp.pixels_to_units(LINE_WIDTH_IN_PIXELS, Gimp.Unit.point(), x_resolution)

        # Grow the selection by half the width of the stroke
        image_selection = image.get_selection()
        image_selection.grow(image, LINE_WIDTH_IN_PIXELS / 2)

        # Paint a stroke along the selection
        Gimp.context_set_line_width_unit(Gimp.Unit.point())
        Gimp.context_set_line_width(
            line_width_in_points,
        )
        Gimp.context_set_antialias(True)
        Gimp.context_set_brush_hardness(1.0)
        Gimp.context_set_stroke_method(Gimp.StrokeMethod.LINE)

        # Actually perform the stroke
        layer.edit_stroke_selection()

        # Pop the context back off the stack
        Gimp.context_pop()

        success_message = f"Applied automatic outline of {line_width_in_points} points ({LINE_WIDTH_IN_PIXELS} pixels)."
        Gimp.message(success_message)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(AutoOutline.__gtype__, sys.argv)
