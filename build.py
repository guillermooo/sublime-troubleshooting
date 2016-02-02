from pybuilder.core import use_plugin
from pybuilder import task

# use_plugin("python.core")
# use_plugin("python.unittest")
# use_plugin("python.coverage")
# use_plugin("python.distutils")

@task
def greet():
    print("hello")

default_task = "greet"