import panel as pn


class RestrictionCheckBox(pn.widgets.Checkbox):
    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click
        self.rx.watch(self._on_click, "value")
