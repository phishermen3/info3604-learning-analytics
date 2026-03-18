from flask import Blueprint, render_template

about_views = Blueprint("about_views", __name__)

@about_views.route("/about")
def about():
    return render_template("about.html")