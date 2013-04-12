#encoding: utf-8

from flask import render_template, flash, url_for, redirect
from flask.views import View
from application import app


@app.route('/')
def index():
    template_name = "index.html"
    context = {}
    static = 'static/'
    return render_template(template_name, context=context, STATIC_URL=static)