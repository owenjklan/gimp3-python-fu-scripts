#!/usr/bin/env python3

###
# This was created with guidance from the following links:
# - https://testing.docs.gimp.org/3.0/en/gimp-using-python-plug-in-tutorial.html
#
# GIMP 3.0 Plugin that will provide two new convenience functions:
#
# - Add a new layer, the same size as the image, filled with black at the
#   very bottom of the layer stack
# - The same as the previous command, except this time the layer will be placed
#   at the top of the layer stack and will have a default opacity of 0.75
#

import sys

import gi

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GLib
# gi.require_version('Gegl', '3.0')
from gi.repository import Gegl


class QuickBlack(Gimp.PlugIn):
    def do_query_procedures(self):
        return [ "owenjklan-quick-black-top", "owenjklan-quick-black-bottom" ]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):
        match name:
            case "owenjklan-quick-black-top":
                cmd_function = self.quick_black_top
                menu_label = "Quick Black Layer - Top"
            case "owenjklan-quick-black-bottom":
                cmd_function = self.quick_black_bottom
                menu_label = "Quick Black Layer - Bottom"
            case _:
                return

        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            cmd_function, None)

        procedure.set_image_types("RGBA")  # Require RGB and Alpha channel

        procedure.set_menu_label(menu_label)
        procedure.add_menu_path('<Image>/Layer/')

        procedure.set_documentation(menu_label,
                                    "Create a new black layer at the top or bottom of the layer stack.",
                                    name)
        procedure.set_attribution("Owen Klan", "Owen Klan", "2024")

        return procedure

    def create_new_layer(self, image, opacity: float = 100.0):
        x_res = image.get_width()
        y_res = image.get_height()

        # Look-up the gimp-layer-new procedure
        pdb = Gimp.get_pdb()
        new_layer_proc = pdb.lookup_procedure("gimp-layer-new")

        proc_config = new_layer_proc.create_config()
        config_values = [
            ('image', image),
            ('width', x_res),
            ('height', y_res),
            ('type', Gimp.ImageType.RGBA_IMAGE),
            ('name', "Quick Black"),
            ('opacity', opacity),
            ('mode', Gimp.LayerMode.NORMAL),
        ]
        for attr_name, attr_value in config_values:
            proc_config.set_property(attr_name, attr_value)

        # Now invoke the procedure
        results = new_layer_proc.run(proc_config)

        # Success?
        success = results.index(0)
        if success:
            return results.index(1)
        else:
            return None

    def quick_black_top(self, procedure, run_mode, image, drawables, config, run_data):
        # Push the current context
        if not Gimp.context_push():
            Gimp.message("Quick Black failed to push context!")
            return procedure.new_return_values(Gimp.PDBStatusType.FAILED, GLib.Error())

        black_color = Gegl.Color()
        black_color.set_rgba(0, 0, 0, 1.0)
        Gimp.context_set_foreground(black_color)

        new_layer = self.create_new_layer(image, opacity=80.0)

        if new_layer is None:
            fail_message = "Failed to create a new layer!"
            Gimp.message(fail_message)
            return procedure.new_return_values(Gimp.PDBStatusType.FAILED, GLib.Error())

        new_layer.fill(Gimp.FillType.FOREGROUND)
        image.insert_layer(new_layer, None, 0)

        # Pop the context back off the stack
        Gimp.context_pop()

        success_message = f"New Black layer added to top of stack."
        Gimp.message(success_message)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def quick_black_bottom(self, procedure, run_mode, image, drawables, config, run_data):
        # Push the current context
        if not Gimp.context_push():
            Gimp.message("Quick Black failed to push context!")
            return procedure.new_return_values(Gimp.PDBStatusType.FAILED, GLib.Error())

        black_color = Gegl.Color()
        black_color.set_rgba(0, 0, 0, 1.0)
        Gimp.context_set_foreground(black_color)

        # 0 is the 'top' layer. The bottom will be the
        # count of layers already in the image
        layer_bottom_pos = len(image.get_layers())

        new_layer = self.create_new_layer(image)

        if new_layer is None:
            fail_message = "Failed to create a new layer!"
            Gimp.message(fail_message)
            return procedure.new_return_values(Gimp.PDBStatusType.FAILED, GLib.Error())

        new_layer.fill(Gimp.FillType.FOREGROUND)
        image.insert_layer(new_layer, None, layer_bottom_pos)

        # Pop the context back off the stack
        Gimp.context_pop()

        success_message = f"New Black layer added to top of stack."
        Gimp.message(success_message)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(QuickBlack.__gtype__, sys.argv)
