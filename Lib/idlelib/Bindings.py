# This file defines the menu contents and key bindings.  Note that
# there is additional configuration information in the EditorWindow
# class (and subclasses): the menus are created there based on the
# menu_specs (class) variable, and menus not created are silently
# skipped by the code here.  This makes it possible to define the
# Debug menu here, which is only present in the PythonShell window.

import sys
from configHandler import idleConf

menudefs = [
 # underscore prefixes character to underscore
 ('file', [
   ('_New window', '<<open-new-window>>'),
   ('_Open...', '<<open-window-from-file>>'),
   ('Open _module...', '<<open-module>>'),
   ('Class _browser', '<<open-class-browser>>'),
   ('_Path browser', '<<open-path-browser>>'),
   None,
   ('_Save', '<<save-window>>'),
   ('Save _As...', '<<save-window-as-file>>'),
   ('Save Co_py As...', '<<save-copy-of-window-as-file>>'),
   None,
   ('_Print window', '<<print-window>>'),
   None,
   ('_Close', '<<close-window>>'),
   ('E_xit', '<<close-all-windows>>'),
  ]),
 ('edit', [
   ('_Undo', '<<undo>>'),
   ('_Redo', '<<redo>>'),
   None,
   ('Cu_t', '<<cut>>'),
   ('_Copy', '<<copy>>'),
   ('_Paste', '<<paste>>'),
   ('Select _All', '<<select-all>>'),
   None,
   ('_Find...', '<<find>>'),
   ('Find a_gain', '<<find-again>>'),
   ('Find _selection', '<<find-selection>>'),
   ('Find in Files...', '<<find-in-files>>'),
   ('R_eplace...', '<<replace>>'),
   ('Go to _line', '<<goto-line>>'),
  ]),
('format', [
    ('_Indent region', '<<indent-region>>'),
    ('_Dedent region', '<<dedent-region>>'),
    ('Comment _out region', '<<comment-region>>'),
    ('U_ncomment region', '<<uncomment-region>>'),
    ('Tabify region', '<<tabify-region>>'),
    ('Untabify region', '<<untabify-region>>'),
    ('Toggle tabs', '<<toggle-tabs>>'),
    ('New indent width', '<<change-indentwidth>>'),
]),
 ('run',[
   ('Python shell', '<<open-python-shell>>'),
 ]),
 ('debug', [
   ('_Go to file/line', '<<goto-file-line>>'),
   ('_Stack viewer', '<<open-stack-viewer>>'),
   ('!_Debugger', '<<toggle-debugger>>'),
   ('!_Auto-open stack viewer', '<<toggle-jit-stack-viewer>>' ),
  ]),
 ('settings', [
   ('_Configure Idle...', '<<open-config-dialog>>'),
   None,
   ('Revert to _Default Settings', '<<revert-all-settings>>'),
  ]),
 ('help', [
   ('_IDLE Help...', '<<help>>'),
   ('Python _Documentation...', '<<python-docs>>'),
   ('_Advice...', '<<good-advice>>'),
   ('View IDLE _Readme...', '<<view-readme>>'),
   None,
   ('_About IDLE...', '<<about-idle>>'),
  ]),
]

default_keydefs = idleConf.GetCurrentKeySet()

del sys
