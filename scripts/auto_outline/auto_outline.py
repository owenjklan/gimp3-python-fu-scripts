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

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
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
        Gimp.message("Hello world!")
        # do what you want to do, then, in case of success, return:
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(AutoOutline.__gtype__, sys.argv)
