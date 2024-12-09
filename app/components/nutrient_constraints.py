from panel.viewable import Viewer
from pyfoodopt import Constraints, NutrientBank
import param
from nutrient_constraint_widget import NutrientConstraintWidget
import panel as pn


class NutrientConstraints(Viewer):

    constraints = param.ClassSelector(class_=Constraints)
    nutrient_bank = param.ClassSelector(class_=NutrientBank)

    def __init__(self, **params):
        super().__init__(**params)
        self.constraint_widgets = []
        for (
            nutrient_nbrs,
            nbr_constraints,
        ) in self.constraints.nutrient_constraints.items():
            label = " + ".join(
                [
                    self.nutrient_bank.get_nutrient_by_id(nbr).nutrient_name
                    for nbr in nutrient_nbrs
                ]
            )
            label += f" ({self.nutrient_bank.get_nutrient_by_id(nutrient_nbrs[0]).unit_name})"
            lower_bound = nbr_constraints.get("lower_bound")
            upper_bound = nbr_constraints.get("upper_bound")
            equality = nbr_constraints.get("equality")

            if lower_bound is not None:
                lower_bound = lower_bound.constraint_value
            else:
                lower_bound = 0
            if upper_bound is not None:
                upper_bound = upper_bound.constraint_value
            if equality is not None:
                equality = equality.constraint_value
            self.constraint_widgets.append(
                NutrientConstraintWidget(
                    nutrient_nbrs=nutrient_nbrs,
                    label=label,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    equality=equality,
                )
            )
        self._layout = pn.Column(
            pn.FlexBox(
                *self.constraint_widgets,
                sizing_mode="stretch_width",
                flex_direction="row",
            ),
            height=800,
            scroll=True,
        )

    def get_constraints(self):
        constraints = {}
        for nutrient_constraint_widget in self.constraint_widgets:
            constraints.update(nutrient_constraint_widget.get_constraints())
        return constraints

    def __panel__(self):
        return self._layout
