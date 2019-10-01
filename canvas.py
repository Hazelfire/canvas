# Import the Canvas class
from canvasapi import Canvas
from canvasapi.exceptions import Unauthorized, ResourceDoesNotExist
import click
import os
import re
import sys
import datetime

from dateutil.parser import parse
key = ""


def get_canvas():
    API_URL = os.environ["CANVAS_URL"]
    # Canvas API key
    API_KEY = key

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    return canvas

def get_module_id(module_item):
    if hasattr(module_item, "page_url"):
        return module_item.page_url
    if hasattr(module_item, "content_id"):
        return module_item.content_id
    return module_item.id


@click.option("--profile", help="Profile you want to go with", default="main")
@click.group()
def cli(profile):
    global key
    if profile == "teacher":
        key = os.environ["CANVAS_TEACHER_OAUTH"]
    else:
        key = os.environ["CANVAS_OAUTH"]


@cli.command()
def courses():
    canvas = get_canvas()

    courses = canvas.get_courses()

    for course in courses:
        click.echo("{}: {}".format(course.id, course.name))


@click.argument("course")
@cli.command()
def modules(course):
    canvas = get_canvas()

    try:
        canvas_modules = canvas.get_course(course).get_modules()

        for module in canvas_modules:
            click.echo("{}: {}".format(module.id, module.name))
            for module_item in module.get_module_items():
                click.echo(
                    "    {}: {} ({})".format(
                        get_module_id(module_item), module_item.title, module_item.type
                    )
                )
    except Unauthorized:
        click.echo("Unauthorized to access modules")


@click.argument("course")
@cli.command()
def enrollments(course):
    canvas = get_canvas()

    try:
        canvas_enrollments = canvas.get_course(course).get_enrollments()

        for enrollment in canvas_enrollments:
            click.echo("{}".format(enrollment))
    except Unauthorized:
        click.echo("Unauthorized to access modules")


@click.argument("module", type=int)
@click.argument("course")
@cli.command()
def module_items(course, module):
    canvas = get_canvas()

    try:
        try:
            canvas_module = canvas.get_course(course)
            try:
                items = canvas_module.get_module(module).get_module_items()
                for module_item in items:
                    click.echo(
                        "{}: {} ({})".format(
                            get_module_id(module_item), module_item.title, module_item.type
                        )
                    )
            except ResourceDoesNotExist:
                click.echo("module does not exist")
        except ResourceDoesNotExist:
            click.echo("course does not exist")

    except Unauthorized:
        click.echo("Unauthorized to access modules")


@click.argument("page")
@click.argument("course")
@cli.command()
def page(course, page):
    canvas = get_canvas()

    try:
        try:
            canvas_course = canvas.get_course(course)
            try:
                page = canvas_course.get_page(page)
                click.echo(page.title)
                click.echo(page.body)
            except ResourceDoesNotExist:
                click.echo("page does not exist")
        except ResourceDoesNotExist:
            click.echo("course does not exist")

    except Unauthorized:
        click.echo("Unauthorized to access modules")


@click.argument("course")
@cli.command(help="lists all the files for a course")
def files(course):
    canvas = get_canvas()

    try:
        files = canvas.get_course(course).get_files()

        for canv_file in files:
            click.echo("{}: {}".format(canv_file.id, canv_file))
    except Unauthorized:
        click.echo("Unauthorized to access file list")

def download_module_item(canvas, course, item, directory):
    """ Downloads a page or file """
    if item.type == "File":
        canvas_file = canvas.get_file(item.content_id)
        item_file = directory + "/" + canvas_file.filename
        canvas_file.download(item_file)
    elif item.type == "Page":
        canvas_page = course.get_page(item.page_url)
        body = "<html><head>{}</head><body>{}</body></html>".format(
            canvas_page.title,
            canvas_page.body
        )
        with open(directory + "/" + item.page_url + ".html", "w") as f:
            f.write(body)
        matches = re.finditer("/files/([0-9]+)/download", body)
        for match in matches:
            canvas_file_id = match.group(1)
            print("Downloading: " + canvas_file_id)
            try:
                canvas_file = canvas.get_file(canvas_file_id)
                canvas_file.download(directory + "/" + canvas_file.filename)
            except Unauthorized:
                print("Failed, unauthorized")
            except ResourceDoesNotExist:
                print("Failed, does not exist")

@click.argument("fileid")
@click.option("-r", "--recursive", is_flag=True)
@cli.command()
def download(fileid, recursive):
    canvas = get_canvas()
    if recursive:
        canvas_course = canvas.get_course(fileid)
        canvas_modules = canvas_course.get_modules()
        for module in canvas_modules:
            module_folder = module.name
            if not os.path.exists(module_folder):
                os.makedirs(module_folder)
            items = module.get_module_items()
            for item in items:
                download_module_item(canvas, canvas_course, item, module_folder)
    else:
        try:
            canvas_file = canvas.get_file(fileid)
            canvas_file.download(canvas_file.filename)
        except ResourceDoesNotExist:
            click.echo("File does not exist")
        


@click.argument("course", required=False)
@cli.command()
def assignments(course):
    canvas = get_canvas()
    if not course:
        courses = canvas.get_courses()
    else:
        courses = [canvas.get_course()]

    for course in courses:
        assignments = course.get_assignments()
        click.echo("\n"+str(course.id) + ": " + course.name)

        for assignment in assignments:
            if assignment.due_at and parse(assignment.due_at) > datetime.datetime.now(datetime.timezone.utc):
                click.echo("{}: {}".format(assignment.id, assignment.name))


@click.argument("assignment")
@click.argument("course")
@cli.command()
def assignment(course, assignment):
    canvas = get_canvas()
    assignment = canvas.get_course(course).get_assignment(assignment)
    click.echo("Name: {}\nDue: {}".format(assignment, assignment.due_at))
    click.echo(assignment.description)


if __name__ == "__main__":
    sys.exit(cli(prog_name="canvas"))
