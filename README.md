# ipython_blocking
A Python library that offers a context manager and IPython magic to capture `execute_request` messages on the IPython [comms channels](https://jupyter-client.readthedocs.io/en/stable/messaging.html#messages-on-the-shell-router-dealer-channel) and then replay them later.  It is a way to "block" Jupyter notebook cells from running while waiting for a Widget value to change, a Widget button to be pressed, or other validation functions to happen.


# What problem is this solving
In our corporate work environment, we have several thousand Jupyter notebook users.  A small fraction are notebook authors, while the majority of users are running notebooks that other people have written.  Non-authors fall along a spectrum of "code comfort": some users want the notebook experience to be like a regular web application where they don't even see the code, while others are experienced enough to read the code and edit it to fit their individual needs.  

[ipywidgets](https://ipywidgets.readthedocs.io/en/stable/) are a very popular and easy way to make rich user interfaces that are engaging for even non-technical users.  It is also common practice to write notebooks designed to work in [dashboard mode](https://github.com/jupyter/dashboards) or which users will interact with by clicking "cell -> run all" right from the start.

The problem is that notebook authors must structure the rest of their code as call-back functions if they want to reference data entered into a widget, such as a query string in a `widgets.Text` box or an option picked from a `widget.Dropdown`.  Wrapping code in a function that is triggered by an `on_click` handler or similar isn't inherently bad, but there are problems that show up over and over.  Generally speaking, using widgets for input data and then using callback functions to do the work in a notebook makes the notebook harder to read, harder to debug, harder to maintain, and harder to build on.

Without `ipython_blocking`, our notebook authors faced the choice of leveraging widgets for user-friendly input forms and then having "ugly" callback code afterwards, or writing "cleaner" exploratory-style code that might not have gotten traction with some non-technical users.  With `ipython_blocking`, notebook authors can get the best of both worlds.

# When to use `ipython_blocking` and when not to
If your notebook is designed to be run once, execute in a linear fashion, and uses widgets for input, then `ipython_blocking` is perfect for you.  However, it's not a library for all use cases.  For instance, if you have a notebook where you expect users to change values in a widget and then that updates a visualization, using regular `on_click` handlers is better.  

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
import ipywidgets
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
        
### Cell 3 (doesn't run until the dropdown value changes)
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

import ipywidgets
dd = widgets.Dropdown(options=['', 'foo', 'bar', 'baz'])
dd

### Cell 2
%block dd
        
### Cell 3 (doesn't run until the dropdown value has changed)
print(dd.value)
```

### Using `%block` with a `Button`
The `%block` cell execution capture context with a `Button` will stop when the button has been clicked.  It's handy to make a button disabled until other validation has been met.

```python
### Cell 1
import ipython_blocking
ipython_blocking.load_ipython_extensions()

import ipywidgets
query_input = widgets.Text(description="Query string:")
button = widgets.Button(description="Submit", disabled=True)

def input_observe(ev):
    value = ev['new']
    if len(value) >= 14:
        button.disabled = False
        button.button_style = 'success'

query_input.observe(input_observe, 'value')
box = widgets.VBox(children=[query_input, button])
box

### Cell 2
%block button

### Cell 3 (doesn't run until the button is pressed)
print(query_input.value)
```

### Using `%block` with a function/method
The `%block` cell execution capture context with a function/method will stop when that function/method returns True.  Use this when you need to do complex input validation.  

```python
### Cell 1
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

### Cell 4 (doesn't run until complex_validation returns True)
print(dd1.value, dd2.value)
```

### Timeout arguments
The `%block` magic accepts one optional argument `-t` / `--timeout`, which is a number of seconds until the cell execution context stops.  The default is no timeout, which means the `%block` will run forever until the criteria is met to stop capturing cell execution and replay any captured cells.
