# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - iLab HKU
"""

import os
from flask_migrate import Migrate
from flask_minify  import minify
from sys import exit

from apps.config import config_dict
from apps import create_app, db
 
# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('FLASK_ENV        = ' + os.getenv('FLASK_ENV') )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )
    app.logger.info('UPLOAD_FOLDER    = ' + app_config.UPLOAD_FOLDER )
    app.logger.info('UPLOAD_FOLDER    = ' + app_config.OUTPUT_FOLDER_DIFF )
    app.logger.info('FABRIC_FOLDER    = ' + app_config.FABRIC_FOLDER )
if __name__ == "__main__":
    app.run()
