# ipython_blocking
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/kafonek/ipython_blocking/master)

`ipython_blocking` is a context manager for capturing cell execution messages in a Jupyter notebook, along with magic commands `%block` and `%blockrun` for convenience.  The primary use-case for blocking notebook execution is to wait for users to interact with [ipywidgets](https://github.com/jupyter-widgets/ipywidgets) and then reference the values entered in those Widgets.


### Install
`ipython_blocking` is on [PyPI](https://pypi.org/project/ipython_blocking/), install with pip.

```python
pip install ipython_blocking
```

### Usage
Try out the demo notebooks in Binder to see `ipython_blocking` in action.  The most common way to use `ipython_blocking` is with the `%blockrun` magic and running a notebook with "cell -> run all".  `%blockrun button` stops the cell execution messages from the initial "cell -> run all", and attaches a "cell -> run all below" handler to the button so that a notebook can be run in a linear fashion without callback functions after a user has filled out other Widget values.

```python
### cell #1
import ipywidgets as widgets
import ipython_blocking # enables %block and %blockrun magic

text = widgets.Text()
dropdown = widgets.Dropdown(options=['', 'foo', 'bar', 'baz'])
button = widgets.Button(description='Run')
box = widgets.VBox(children=[text, dropdown, button])
box

### cell #2
%blockrun button

### cell #3 -- doesn't execute until the 'Run' button is pressed
### This gives the user a chance to interact with the Text and Dropdown widgets
print(text.value)
print(dropdown.value)
```

![](example.gif)


### Alternatives



Most notebooks that use `ipywidgets` use call-back functions to make sure they're only referencing the values in the Widgets after a user has interacting with that Widget.  For example:

```python
import ipywidgets as widgets
from IPython.display import display
dropdown = widgets.Dropdown(options=['foo', 'bar', 'baz'])
button = widgets.Button(description="Print")
box = widgets.VBox(children=[dropdown, button])

def handler(w):
    print(dropdown.value)
button.on_click(handler)
display(box)
```

The problem is that all of the application logic must be bundled inside a call back function, which dampens many of the best advantages of working in a Jupyter Notebook environment to begin with.
 
 * Introspection of the data inside the call-back functions is much harder than in the global scope (and littering your code with `global` is ugly)
 * All other variables in the function are destroyed if an error happens, which can make debug harder (again, unless you litter your code with `global`)
 * There is no sense of small input/visualizing the output throughout the application logic workflow (unless you litter your code with `print` statements)
 * General readability and code comprehension takes a hit
 
### Alternatives
If you structure your code in an asynchronous fashion, you can use [`%gui asyncio`](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Asynchronous.html#) to wait for user interaction with a Widget.  
 
 





























