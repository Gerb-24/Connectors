import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QIcon
from sidewalls import compile_multiple
import json
from copy import deepcopy

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui2.ui', self)
        self.setWindowTitle("Connectors")
        self.setWindowIcon(QIcon('ui_images/appicon.ico'))
        self.setFixedSize(self.size())

        self.data = {
            # variables for standard connectors
            'standard_file':                '',
            'standard_dir':                 '',
            'standard_search_texture':      '',
            'standard_wall_texture':        '',
            'standard_floor_texture':       '',
            'standard_ceiling_texture':     '',
            'standard_corner_texture':      '',

            # variables for jump connectors
            'jump_dir':                     '',
            'jump_search_texture':          '',
            'jump_wall_texture':            '',
            'jump_floor_texture':           '',
            'jump_ceiling_texture':         '',
            'jump_corner_texture':          '',
            'jump_tele_texture':            '',

            # variables for third section
            'maps_dir':                     '',
            'new_map_name':                 '',
            'preset_file':                  '',
            'preset_dir':                   '',

            #boolean variables
            'standard_nodraw':              False,
            'jump_nodraw':                  False,
            'standard_corner':              False,
            'jump_corner':                  False,
        }

        self.le_data = {
            # line-edits for standard connectors
            'standard_search_texture':      self.standard_search_le,
            'standard_wall_texture':        self.standard_wall_le,
            'standard_floor_texture':       self.standard_floor_le,
            'standard_ceiling_texture':     self.standard_ceiling_le,
            'standard_corner_texture':      self.standard_corner_le,

            # line-edits for jump connectors
            'jump_search_texture':          self.jump_search_le,
            'jump_wall_texture':            self.jump_wall_le,
            'jump_floor_texture':           self.jump_floor_le,
            'jump_ceiling_texture':         self.jump_ceiling_le,
            'jump_corner_texture':          self.jump_corner_le,
            'jump_tele_texture':            self.jump_tele_le,

            # line-edits for third section
            'new_map_name':                  self.new_map_name_le,
        }

        self.file_le_data = {
            'standard_file':    self.standard_file_le,
            'preset_file':      self.preset_file_le,
        }

        self.file_btn_data = {
            'standard_file':    self.standard_file_btn,
            'preset_file':      self.preset_file_btn,
        }

        self.file_dir_data = {
            'standard_file':    'standard_dir',
            'preset_file':      'preset_dir',
        }

        self.dir_le_data = {
            'jump_dir':     self.jump_dir_le,
            'maps_dir':     self.maps_dir_le,
        }

        self.dir_btn_data = {
            'jump_dir':     self.jump_dir_btn,
            'maps_dir':     self.maps_dir_btn,
        }

        self.bool_cb_data = {
            'standard_nodraw':  self.standard_nodraw_cb,
            'jump_nodraw':      self.jump_nodraw_cb,
            'standard_corner':  self.standard_corner_cb,
            'jump_corner':      self.jump_corner_cb,
        }
       
        # connecting string logic
        for tex in self.le_data:
            self.le_data[ tex ].textChanged.connect( lambda _, t=tex: self.assign_text_to_var( tex=t ) )

        # connecting file logic
        for file in self.file_btn_data:
            self.file_btn_data[ file ].clicked.connect( lambda _, f=file: self.load_file( file=f ) )

        # connecting dir logic
        for dir_key in self.dir_btn_data:
            self.dir_btn_data[ dir_key ].clicked.connect( lambda _, d=dir_key: self.load_dir( dir_key=d ) )

        # connecting boolean logic
        for key in self.bool_cb_data:
            self.bool_cb_data[ key ].clicked.connect( lambda _, k=key: self.assign_bool_to_var( key=k ) )

        # connecting compile buttons
        self.standard_compile_btn.clicked.connect( self.standard_compile )
        self.jump_compile_btn.clicked.connect( self.jump_compile )
        self.create_new_project_btn.clicked.connect( self.create_new_project )
        self.add_new_jump_btn.clicked.connect( self.add_new_jump )

        # handling settings
        self.save_settings_btn.clicked.connect( self.save )
        self.load_settings()

    def assign_text_to_var( self, tex='' ):
        self.data[ tex ] = self.le_data[tex].text()

    def assign_bool_to_var( self, key='' ):
        self.data[ key ] = not self.data[ key ]

    def load_file( self, file='' ):
        dir_key = self.file_dir_data[ file ]
        filepath, _ = QFileDialog.getOpenFileName(self, "Load VMF", self.data[ dir_key ], "VMF(*.vmf)")
        self.data[ file ] = filepath  
        self.data[ dir_key ] = os.path.dirname(filepath)
        self.file_le_data[ file ].setText( os.path.basename(filepath) )

    def load_dir( self, dir_key='' ):
        dirpath = QFileDialog.getExistingDirectory(self, "Open Directory", self.data[ dir_key ])
        self.data[ dir_key ] = dirpath
        self.dir_le_data[ dir_key ].setText( os.path.basename(dirpath) )

    # compile functions
    def standard_compile( self ):
        textures = [ 
            self.data[ 'standard_search_texture' ],
            self.data[ 'standard_wall_texture' ],
            self.data[ 'standard_floor_texture' ],
            self.data[ 'standard_ceiling_texture' ],
            self.data[ 'standard_corner_texture' ],
            '',
            ]
        file_path = self.data[ 'standard_file' ]
        nodraw = self.data[ 'standard_nodraw' ]
        corner = self.data[ 'standard_corner' ]
        compile_multiple( 'standard', '', [ file_path ], textures, nodraw, corner )

    def jump_compile( self ):
        textures = [ 
            self.data[ 'jump_search_texture' ],
            self.data[ 'jump_wall_texture' ],
            self.data[ 'jump_floor_texture' ],
            self.data[ 'jump_ceiling_texture' ],
            self.data[ 'jump_corner_texture' ],
            self.data[ 'jump_tele_texture' ],
            ]
        dir_path = self.data[ 'jump_dir' ]
        nodraw = self.data[ 'jump_nodraw' ]
        corner = self.data[ 'jump_corner' ]
        files = [os.path.join( dir_path, f ) for f in os.listdir( dir_path ) if os.path.isfile(os.path.join( dir_path , f)) ]
        root = os.path.abspath(os.path.join( dir_path, os.pardir))
        
        # we dont want to include the .vmx files
        files = [ f for f in files if os.path.splitext(f)[1] == '.vmf' ]
        compile_multiple( 'jump', root, files, textures, nodraw, corner )

    # utility functions

    def create_new_project( self ):
        maps_dir = self.data[ 'maps_dir' ]
        map_name = self.data[ 'new_map_name' ]
        if maps_dir == '' or map_name == '':
            return
        jumps_path = os.path.join( maps_dir, f'{map_name}/jumps_for_{map_name}' )
        os.makedirs( jumps_path )
        self.data[ 'jump_dir' ] = jumps_path
        self.dir_le_data[ 'jump_dir' ].setText( os.path.basename( jumps_path )  )

    def add_new_jump( self ):
        preset_path = self.data[ 'preset_file' ]
        if preset_path == '':
            return
        with open( preset_path, 'r' ) as f:
            data = f.read()
        dir_path = self.data[ 'jump_dir' ]
        if dir_path == '':
            return 
        files = [os.path.join( dir_path, f ) for f in os.listdir( dir_path ) if os.path.isfile(os.path.join( dir_path , f)) ]
        files = [ f for f in files if os.path.splitext(f)[1] == '.vmf' ]
        new_jump_path = os.path.join( dir_path, f'jump_{ len( files ) + 1 }.vmf' )
        print( new_jump_path )
        with open( new_jump_path, 'w' ) as f:
            f.write( data )

    # settings functions
    def save( self ):
        save_data = self.data
        json_data = json.dumps( save_data, indent=2 )
        with open("settings.json", "w") as f:
            f.write(json_data)

    def load_settings(self):
        with open("settings.json", "r") as f:
            load_data = json.loads(f.read())
        for key in load_data:
            self.data[ key ] = load_data[ key ]
        for tex in self.le_data:
            self.le_data[ tex ].setText( self.data[ tex ] )
        for file in self.file_le_data:
            file_path = self.data[ file ]
            self.file_le_data[ file ].setText( os.path.basename( file_path ) )
        for dir_key in self.dir_le_data:
            dir_path = self.data[ dir_key ]
            self.dir_le_data[ dir_key ].setText( os.path.basename( dir_path ) )
        for key in self.bool_cb_data:
            self.bool_cb_data[ key ].setChecked( self.data[ key ] )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(open('cssfiles/stylesheet.css').read())

    window = MyApp()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print(' Closing Window ... ')
