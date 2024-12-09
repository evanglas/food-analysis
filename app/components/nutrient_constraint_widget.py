import param
from panel.viewable import Viewer
import panel as pn
from pyfoodopt import NutrientConstraint


class NutrientConstraintWidget(Viewer):

    label = param.String()
    lower_bound = param.Number(default=0)
    upper_bound = param.Number(default=None)
    equality = param.Number(default=None)

    def __init__(self, nutrient_nbrs: tuple, **params):
        super().__init__(**params)
        if self.lower_bound is not None:
            self.lower_bound = round(self.lower_bound, 1)
        if self.upper_bound is not None:
            self.upper_bound = round(self.upper_bound, 1)
        if self.equality is not None:
            self.equality = round(self.equality, 1)
        self.nutrient_nbrs = nutrient_nbrs
        self.layout = self._create_layout()

    def _create_layout(self):
        label_widget = pn.pane.Markdown(f"**{self.label}**", width=200)
        lower_input = pn.widgets.FloatInput.from_param(
            self.param.lower_bound, width=100
        )
        equality_input = pn.widgets.FloatInput.from_param(
            self.param.equality, width=100
        )
        upper_input = pn.widgets.FloatInput.from_param(
            self.param.upper_bound, width=100
        )

        input_row = pn.Row(label_widget, lower_input, equality_input, upper_input)
        return input_row

    def get_constraints(self):
        nbr_to_coefficient = {nbr: 1 for nbr in self.nutrient_nbrs}
        constraints = {self.nutrient_nbrs: {}}
        if self.lower_bound is not None:
            constraints[self.nutrient_nbrs]["lower_bound"] = NutrientConstraint(
                constraint_type="lower_bound",
                constraint_value=self.lower_bound,
                nbr_to_coefficient=nbr_to_coefficient,
            )
        if self.upper_bound is not None:
            constraints[self.nutrient_nbrs]["upper_bound"] = NutrientConstraint(
                constraint_type="upper_bound",
                constraint_value=self.upper_bound,
                nbr_to_coefficient=nbr_to_coefficient,
            )
        if self.equality is not None:
            constraints[self.nutrient_nbrs]["equality"] = NutrientConstraint(
                constraint_type="equality",
                constraint_value=self.equality,
                nbr_to_coefficient=nbr_to_coefficient,
            )
        return constraints

    def __panel__(self):
        return self.layout
