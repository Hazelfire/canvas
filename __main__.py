# Import the Canvas class
from canvasapi import Canvas
from canvasapi.exceptions import Unauthorized, ResourceDoesNotExist
import click
import os
import sys

key = ""


def get_canvas():
    API_URL = os.environ["CANVAS_URL"]
    # Canvas API key
    API_KEY = key

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    return canvas


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
        click.echo(course.enrollment_term_id)
        click.echo(course)


@click.argument("course")
@cli.command()
def modules(course):
    canvas = get_canvas()

    try:
        canvas_modules = canvas.get_course(course).get_modules()

        for module in canvas_modules:
            click.echo("{}: {}".format(module.id, module.name))
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
                print(dir(items[0]))
                for module_item in items:
                    click.echo(
                        "{}: {} ({})".format(
                            module_item.content_id, module_item.title, module_item.type
                        )
                    )
            except ResourceDoesNotExist:
                click.echo("module does not exist")
        except ResourceDoesNotExist:
            click.echo("course does not exist")

    except Unauthorized:
        click.echo("Unauthorized to access modules")


@click.argument("module", type=int)
@click.argument("course")
@cli.command()
def page(course, module):
    canvas = get_canvas()

    try:
        try:
            canvas_module = canvas.get_course(course)
            try:
                items = canvas_module.get_module(module).get_module_items()
                for module_item in items:
                    click.echo(module_item)
            except ResourceDoesNotExist:
                click.echo("module does not exist")
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


@click.argument("fileid")
@cli.command()
def download(fileid):
    canvas = get_canvas()

    try:
        canvas_file = canvas.get_file(fileid)
        canvas_file.download(canvas_file.filename)
    except ResourceDoesNotExist:
        click.echo("File does not exist")


@click.option("--course", help="The course you want to get assignments for")
@cli.command()
def assignments(course):
    canvas = get_canvas()
    assignments = canvas.get_course(course).get_assignments()

    for assignment in assignments:
        click.echo(assignment)


@click.option("--course", help="The course you want to get assignments for")
@click.option("--assignment", help="The course you want to get assignments for")
@cli.command()
def assignment(course, assignment):
    canvas = get_canvas()
    assignment = canvas.get_course(course).get_assignment(assignment)
    click.echo("Name: {}\nDue: {}".format(assignment, assignment.due_at))


if __name__ == "__main__":
    sys.exit(cli(prog_name="canvas"))
# Canvas API URL
