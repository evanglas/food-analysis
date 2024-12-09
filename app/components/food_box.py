import param
import panel as pn
import random
from panel.viewable import Viewer
from pyfoodopt import BaseFood


class FoodBox(Viewer):

    food = param.ClassSelector(class_=BaseFood)

    rcolor = lambda: "#%06x" % random.randint(0, 0xFFFFFF)

    enabled_stylesheets = [
        """
    button { background-color: green !important;}
    """
    ]

    disabled_stylesheets = [
        """
        button { background-color: red !important;}
        """
    ]

    def __init__(self, **params):
        super().__init__(**params)
        self.toggle = pn.widgets.Button(
            name="Enabled",
            on_click=self._on_click,
            stylesheets=FoodBox.enabled_stylesheets,
        )
        self._layout = pn.FlexBox(
            pn.pane.Str(self.food.food_name),
            self.toggle,
            flex_direction="column",
            justify_content="center",
            align_items="center",
            align_content="center",
            sizing_mode="fixed",
            width=150,
            height=100,
            margin=10,
            styles={
                "background-color": f"{FoodBox.rcolor()}",
                "border-radius": "10px",
            },
        )
        self.restrictions = set()

    def handle_checkbox_click(self, event, restriction_name):
        if event:
            if not self.food.food_meta.restrictions.__getattribute__(restriction_name):
                self.disable_toggle()
                self.restrictions.add(restriction_name)
        else:
            if not self.food.food_meta.restrictions.__getattribute__(restriction_name):
                self.restrictions.remove(restriction_name)
                if len(self.restrictions) == 0:
                    self.enable_toggle()

    def enable_toggle(self):
        self.toggle.name = "Enabled"
        self.toggle.stylesheets = FoodBox.enabled_stylesheets

    def disable_toggle(self):
        self.toggle.name = "Disabled"
        self.toggle.stylesheets = FoodBox.disabled_stylesheets

    def _on_click(self, event):
        if self.toggle.name == "Enabled":
            self.disable_toggle()
        else:
            self.enable_toggle()

    def __panel__(self):
        return self._layout
