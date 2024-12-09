import param
import panel as pn
from panel.viewable import Viewer
from food_box import FoodBox


class FoodBoxesContainer(Viewer):

    food_boxes = param.List(class_=FoodBox)

    def __init__(self, **params):
        super().__init__(**params)
        self.food_boxes = self.food_boxes
        self._layout = pn.Column(
            pn.FlexBox(
                *self.food_boxes,
                flex_direction="row",
                justify_content="flex-start",
                sizing_mode="stretch_width",
            ),
            height=800,
            scroll=True,
        )

    def handle_restriction_checkbox_clicked(self, event, restriction_name):
        for food_box in self.food_boxes:
            food_box.handle_checkbox_click(event, restriction_name)

    def get_active_foods_fdc_ids(self, *args):
        return [fb.food.fdc_id for fb in self.food_boxes if fb.toggle.name == "Enabled"]

    def __panel__(self):
        return self._layout
