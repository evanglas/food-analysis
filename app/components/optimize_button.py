import panel as pn
from panel.viewable import Viewer


class OptimizeButton(Viewer):

    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click
        self._layout = pn.widgets.Button(
            name="Optimize",
            button_type="primary",
            on_click=self._on_click,
            margin=(15, 0, 15, 0),
            width=100,
        )

    def __panel__(self):
        return self._layout
