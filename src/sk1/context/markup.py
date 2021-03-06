# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wal
from generic import ActionCtxPlugin
from generic import CtxPlugin
from sk1 import _, events, modes
from sk1.pwidgets import FontChoice
from sk1.resources import icons, pdids
from uc2 import libpango
from wal import LEFT, CENTER


class TextCasePlugin(ActionCtxPlugin):
    name = 'TextCasePlugin'
    ids = [pdids.ID_UPPER_TEXT, pdids.ID_LOWER_TEXT, pdids.ID_CAPITALIZE_TEXT, ]


class ClearMarkupPlugin(ActionCtxPlugin):
    name = 'ClearMarkupPlugin'
    ids = [pdids.ID_CLEAR_MARKUP]


FONT_SIZES = range(5, 14) + range(14, 30, 2) + [32, 36, 40, 48, 56, 64, 72]


class FontMarkupPlugin(CtxPlugin):
    name = 'FontMarkupPlugin'

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)
        events.connect(events.SELECTION_CHANGED, self.update)

    def build(self):

        self.families, self.faces_dict = libpango.get_fonts()

        self.families_combo = FontChoice(self, onchange=self.on_font_change)
        self.add(self.families_combo, 0, LEFT | CENTER, 2)
        self.add((3, 3))
        self.families_combo.set_font_family('Sans')

        self.faces = self.faces_dict['Sans']
        self.faces_combo = wal.Combolist(self, items=self.faces,
            onchange=self.apply_changes)
        self.faces_combo.set_active(0)
        self.add(self.faces_combo, 0, wal.LEFT | wal.CENTER, 2)
        self.add((3, 3))

        self.size_combo = wal.FloatCombobox(self, 12,
            digits=2, items=FONT_SIZES, onchange=self.apply_changes)
        self.add(self.size_combo, 0, wal.LEFT | wal.CENTER, 2)

    def update(self, *args):
        insp = self.app.insp
        if not insp.is_mode(modes.TEXT_EDIT_MODE): return
        val = insp.is_text_selection()
        for item in (self.families_combo, self.faces_combo, self.size_combo):
            item.set_enable(val)
        ctrl = self.app.current_doc.canvas.controller
        family, face, size = ctrl.get_fontdescr()

        if not family in self.families: family = 'Sans'
        self.families_combo.set_font_family(family)

        self.faces = self.faces_dict['Sans']
        self.faces_combo.set_items(self.faces)
        if face in self.faces:
            self.faces_combo.set_active(self.faces.index(face))
        else:
            self.faces_combo.set_active(0)

        self.size_combo.set_value(size)

    def on_font_change(self, *args):
        self.faces = self.faces_dict[self.families_combo.get_font_family()]
        face = self.faces[self.faces_combo.get_active()]
        if not face in self.faces:
            self.faces_combo.set_active(0)
        self.apply_changes()

    def apply_changes(self, *args):
        insp = self.app.insp
        if not insp.is_mode(modes.TEXT_EDIT_MODE): return
        family = self.families_combo.get_font_family()
        face = self.faces[self.faces_combo.get_active()]
        size = self.size_combo.get_value()
        ctrl = self.app.current_doc.canvas.controller
        ctrl.set_fontdescr(family, face, size)


class SimpleMarkupPlugin(CtxPlugin):
    name = 'SimpleMarkupPlugin'

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)
        events.connect(events.SELECTION_CHANGED, self.update)

    def build(self):
        self.bold = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_BOLD,
            tooltip=_('Bold'), onchange=self.bold_changed)
        self.add(self.bold, 0, LEFT | CENTER, 2)

        self.italic = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_ITALIC,
            tooltip=_('Italic'), onchange=self.italic_changed)
        self.add(self.italic, 0, LEFT | CENTER, 2)

        self.underline = wal.ImageToggleButton(self,
            art_id=icons.PD_TEXT_UNDERLINE,
            tooltip=_('Underline'), onchange=self.underline_changed)
        self.add(self.underline, 0, LEFT | CENTER, 2)

        self.strike = wal.ImageToggleButton(self,
            art_id=icons.PD_TEXT_STRIKETHROUGH,
            tooltip=_('Strikethrough'), onchange=self.strike_changed)
        self.add(self.strike, 0, LEFT | CENTER, 2)

    def update(self, *args):
        insp = self.app.insp
        if not insp.is_mode(modes.TEXT_EDIT_MODE): return
        val = insp.is_text_selection()
        for item in (self.bold, self.italic, self.underline, self.strike):
            item.set_enable(val)
        ctrl = self.app.current_doc.canvas.controller
        self.bold.set_value(ctrl.is_tag('b'), True)
        self.italic.set_value(ctrl.is_tag('i'), True)
        self.underline.set_value(ctrl.is_tag('u'), True)
        self.strike.set_value(ctrl.is_tag('s'), True)

    def bold_changed(self):
        ctrl = self.app.current_doc.canvas.controller
        ctrl.set_tag('b', self.bold.get_value())

    def italic_changed(self):
        ctrl = self.app.current_doc.canvas.controller
        ctrl.set_tag('i', self.italic.get_value())

    def underline_changed(self):
        ctrl = self.app.current_doc.canvas.controller
        ctrl.set_tag('u', self.underline.get_value())

    def strike_changed(self):
        ctrl = self.app.current_doc.canvas.controller
        ctrl.set_tag('s', self.strike.get_value())


class ScriptMarkupPlugin(CtxPlugin):
    name = 'ScriptMarkupPlugin'

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)
        events.connect(events.SELECTION_CHANGED, self.update)

    def build(self):
        self.sup = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_SUPERSCRIPT,
            tooltip=_('Superscript'), onchange=self.sup_changed)
        self.add(self.sup, 0, LEFT | CENTER, 2)

        self.sub = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_SUBSCRIPT,
            tooltip=_('Subscript'), onchange=self.sub_changed)
        self.add(self.sub, 0, LEFT | CENTER, 2)

    def update(self, *args):
        insp = self.app.insp
        if not insp.is_mode(modes.TEXT_EDIT_MODE): return
        val = insp.is_text_selection()
        for item in (self.sup, self.sub):
            item.set_enable(val)
        ctrl = self.app.current_doc.canvas.controller
        self.sup.set_value(ctrl.is_tag('sup'), True)
        self.sub.set_value(ctrl.is_tag('sub'), True)

    def sup_changed(self):
        ctrl = self.app.current_doc.canvas.controller
        ctrl.set_tag('sup', self.sup.get_value())

    def sub_changed(self):
        ctrl = self.app.current_doc.canvas.controller
        ctrl.set_tag('sub', self.sub.get_value())
