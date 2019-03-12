# Import the Canvas class
from canvasapi import Canvas
import click
import os
import sys

key = ""


def get_canvas():
    API_URL = os.environ["CANVAS_URL"]
    # Canvas API key
    API_KEY = os.environ["CANVAS_OAUTH"]

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    return canvas


@click.option('--profile', help="Profile you want to go with", default="main")
@click.group()
def cli(profile):
    if profile == "teacher":
        key = os.environ["CANVAS_TEACHER_OAUTH"]
    else:
        key = os.environ["CANVAS_OAUTH"]


@cli.command()
def courses():
    canvas = get_canvas()

    courses = canvas.get_courses()

    for course in courses:
        click.echo(course)


@click.option('--course', help="Course you want to get files for")
@cli.command()
def files(course):
    canvas = get_canvas()

    files = canvas.get_course(course).get_files()

    for canv_file in files:
        print(canv_file)


if __name__ == "__main__":
    sys.exit(cli())
# Canvas API URL
