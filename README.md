# ipython_blocking
A Python library that offers a context manager and IPython magic to capture cell execution messages (`execute_request`) and then replay them later.  It is a way to "block" Jupyter notebooks from running while waiting for a Widget value to change, a Widget button to be pressed, or other validation functions to happen.


# Use-case
The intended use-case of this library was to handle "blocking" until a widget value changed or was filled out to satisfy some validation function.  Widgets are often used in notebooks to offer elegant and robust form input for queries to remote API's or other complex inputs.  Unfortunately, it's typical that the rest of the code in a "widget-based notebook" ends up being created as callbacks and is forced into a style that is hard to read, hard to debug, and hard to manipulate.

`ipython_blocking` offers a way to capture cell execution requests and then replay them after a condition is met, such as a widget changing value, a button being pressed, or other validation function returning `True`.  That effectively "blocks" a notebook so that you can write regular non-callback code that expects to access a widget's value directly and will only run after an appropriate value is set.

# Examples
See [the demo notebook](demo_notebook.ipynb) for an interactive example.

### Using the CaptureExecution context manager
The most explicit way to use `ipython_blocking` is to use the context manager directly.  In this example, cell #3 (printing the dropdown value) will not execute until you have chosen a new value besides the default empty string.
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
        
### Cell 3
print(dd.value)
```

# IPython `%block` line magic
Creating the context is verbose so `ipython_blocking` offers a line magic that will set up the context and break out of it in common situations.  It expects one of three types of objects: a function/method, a `ValueWidget`, or a `ButtonWidget`

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
        
### Cell 3
print(dd.value)
```

### Using `%block` with a `ButtonWidget`
The `%block` cell execution capture context with a `Button` will stop when the button has been clicked.  It's handy to make a button disabled until other validation has been met.



