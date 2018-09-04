[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/kafonek/ipython_blocking/master)

# ipython_blocking
A Python library that offers a context manager and IPython magic to capture `execute_request` messages on the IPython [comms channels](https://jupyter-client.readthedocs.io/en/stable/messaging.html#messages-on-the-shell-router-dealer-channel) and then replay them later.  It is a way to "block" Jupyter notebook cells from running while waiting for a Widget value to change, a Widget button to be pressed, or other validation functions to happen.

# Table of Contents
 * [Install](#install)
 * [Examples](#examples)
   * [CaptureExecution example](#using-the-captureexecution-context-manager)
   * [`%block` with ValueWidget](#using-block-with-a-valuewidget)
   * [`%block` with Button](#using-block-with-a-button)
   * [`%block` with validation function](#using-block-with-a-functionmethod)
   * [`%block` timeout argument](#timeout-arguments)  
 * [What problem does this solve](#what-problem-is-this-solving)
 * [When not to use this library](#when-to-use-ipython_blocking-and-when-not-to)


# Install
`ipython_blocking` is on [PyPI](https://pypi.org/project/ipython_blocking/).
```
>>> pip install ipython_blocking
```

# Examples
See [the demo notebook](demo_notebook.ipynb) for an interactive example.

### Using the CaptureExecution context manager
The most explicit way to use `ipython_blocking` is to use the context manager directly.  In this example, cell #3 (printing the dropdown value) will not actually execute until you have chosen a new value besides the default empty string.
```python
### Cell 1
import ipywidgets as widgets
dd = widgets.Dropdown(options=['', 'foo', 'bar', 'baz'])
dd

### Cell 2
import ipython_blocking
ctx = ipython_blocking.CaptureExecution()
with ctx:
    while True:
        if dd.value:
            break
        ctx.step()
        
### Cell 3 (doesn't execute until the dropdown value changes)
print(dd.value)
```

# IPython `%block` line magic
Creating the context is verbose so `ipython_blocking` offers a line magic that will set up the context and break out of it in common situations.  It expects one of three types of objects: a `ValueWidget`, or a `ButtonWidget`, or a function/method,.  Each different type of object that can be passed to `%block` offers a slightly different trigger to stop capturing cell execution and to replay all captured cells.
 * If you pass a `ValueWidget`, the blocking will stop when the widget value changes
 * If you pass a `ButtonWidget`, the blocking will stop when the button is pressed
 * If you pass a function or method, the function will be called often (every `kernel.do_one_iteration()`) and the blocking will stop when it returns True

### Using `%block` with a `ValueWidget`
The `%block` cell execution capture context with a `ValueWidget` will stop when the value of the widget changes.
```python
### Cell 1
import ipython_blocking
ipython_blocking.load_ipython_extensions()

import ipywidgets as widgets
dd = widgets.Dropdown(options=['', 'foo', 'bar', 'baz'])
dd

### Cell 2
%block dd
        
### Cell 3 (doesn't execute until the dropdown value has changed)
print(dd.value)
```

### Using `%block` with a `Button`
The `%block` cell execution capture context with a `Button` will stop when the button has been clicked.  It's handy to make a button disabled until other validation has been met.

```python
### Cell 1
import ipython_blocking
ipython_blocking.load_ipython_extensions()

import ipywidgets as widgets
query_input = widgets.Text(description="Query string:")
button = widgets.Button(description="Submit", disabled=True)

def input_observe(ev):
    value = ev['new']
    if len(value) >= 14:
        button.disabled = False
        button.button_style = 'success'
    else:
        button.disabled = True
        button.button_style = ''

query_input.observe(input_observe, 'value')
box = widgets.VBox(children=[query_input, button])
box

### Cell 2
%block button

### Cell 3 (doesn't execute until the button is pressed)
print(query_input.value)
```

### Using `%block` with a function/method
The `%block` cell execution capture context with a function/method will stop when that function/method returns True.  Use this when you need to do complex input validation.  

```python
### Cell 1
import ipython_blocking
ipython_blocking.load_ipython_extensions()

import ipywidgets as widgets
dd1 = widgets.Dropdown(options=['', 'foo', 'bar', 'baz'])
dd2 = widgets.Dropdown(options=['', 'foo', 'bar', 'baz'])
box = widgets.VBox(children=[dd1, dd2])
box

### Cell 2
def complex_validation():
    "return False unless both dropdowns are non-empty strings and don't equal each other"
    return dd1.value and dd2.value and dd1.value != dd2.value

### Cell 3
%block complex_validation

### Cell 4 (doesn't execute until complex_validation returns True)
print(dd1.value, dd2.value)
```

### Timeout arguments
The `%block` magic accepts one optional argument `-t` / `--timeout`, which is a number of seconds until the cell execution context stops.  The default is no timeout, which means the `%block` will run forever until the criteria is met to stop capturing cell execution and replay any captured cells.


# What problem is this solving
[ipywidgets](https://ipywidgets.readthedocs.io/en/stable/) is an awesome library that let's authors create rich interactive user interfaces inside Jupyter notebooks.  One way we use widgets is for user input such as asking for a query string with `widgets.Text` or expecting them to choose an option from a `widgets.Dropdown`.  In that sense, widgets are an alternative to the built in `input` command or asking the users to edit code in an input cell.  Widgets are particularly compelling to use when engaging non-technical users.

The problem is that if notebook authors use widgets to pull in user input, then they must structure the rest of their logic/workflow as call-back functions.  Wrapping code in a function that is triggered by an `on_click` handler or similar isn't inherently bad, but there are problems that show up over and over in my experience: notebooks become harder to read, harder to debug, harder to maintain, and harder to build on.

### Toy problem 
Consider this toy example.  I want to write a notebook that pulls back some stats on something (NBA player, twitter feed, github profile) and builds a template that I'm going to give to marketing or HR or whatever.  The notebook might look like this - 
```python
### Cell 1
import requests
import ipywidgets as widgets
text = widgets.Text(description="Query:")
button = widgets.Button(description="Run")

def run(ev):
    to_query = text.value
    resp = requests.get('http://some_api/get_info/' + to_query)
    data = resp.json()
    # rest of template creation code here
    
button.on_submit(run)
box = widgets.VBox(children=[text, button])
display(box)
```
    
What happens is that the eventually a user reports that the notebook errored out with a `JSONDecodeError` or `KeyError` because they queried a term that made the API fail and not return json or return something else unexpected.  Then the author more or less copies out everything from inside the `run` function into a new notebook to run line by line in order to debug what went wrong.  Likewise when the author wants to tweak the template, they often put together a separate notebook instead of changing the code inside the `run` function and having to re-execute every step while testing. 

Yes, there are ways to mitigate the problems in this simplistic example, but I think it's fair to say that one huge benefit of notebooks is their ability to offer an exploratory and interactive experience and that once you end up wrapping your code in call-back functions then you lose much of those benefits.  `ipython_blocking` let's you use widgets for user input and avoid structuring the rest of your notebook as call-back functions.

### When to use `ipython_blocking` and when not to
`ipython_blocking` is perfect if you are capturing user input once and then want to move back to an exploratory notebook style.  If you're writing notebooks that are intended to be run by having a user do "cell -> run all" or using [dashboard mode](https://github.com/jupyter/dashboards), this is a great library for you to look at.  It will make your notebook easier to debug, easier to maintain, and easier to build on.

On the other hand, if you're expecting a user to change their input more than once and want the rest of your visualizations or other output to change, then `ipython_blocking` doesn't necessarily make sense for you to use.  There is no problem mixing and matching call-back functions and `ipython_blocking` in one notebook though.  
