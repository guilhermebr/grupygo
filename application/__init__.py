#encoding: utf-8

from flask import Flask

app = Flask(__name__)

#app = Flask('application')
app.config.from_object('application.settings')

import views
#import urls
