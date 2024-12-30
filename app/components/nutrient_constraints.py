from panel.viewable import Viewer
from pyfoodopt import Constraints, NutrientBank
import param
from components.nutrient_constraint_widget import NutrientConstraintWidget
import panel as pn


class NutrientConstraintCheckBox(pn.widgets.Checkbox):

    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click
        self.rx.watch(self._on_click, "value")


class NutrientConstraintChecks(Viewer):

    constraint_options = param.List(item_type=dict)

    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click

    def _layout(self):
        return pn.GridBox(
            *[
                NutrientConstraintCheckBox(
                    on_click=self._on_click,
                    name=constraint_option["age_sex"]
                    + " "
                    + constraint_option["age_range"],
                )
                for constraint_option in self.constraint_options
            ],
            ncols=4,
        )

    def __panel__(self):
        return self._layout


class NutrientConstraints(Viewer):

    constraints = param.ClassSelector(class_=Constraints)
    nutrient_bank = param.ClassSelector(class_=NutrientBank)
    constraint_widgets = param.List(default=[])

    def __init__(self, constraint_checkbox_on_click, **params):
        super().__init__(**params)
        self.constraint_checkboxes = NutrientConstraintChecks(
            constraint_options=[
                {"age_sex": "child", "age_range": "1-3"},
                {"age_sex": "female", "age_range": "4-8"},
                {"age_sex": "male", "age_range": "4-8"},
                {"age_sex": "female", "age_range": "9-13"},
                {"age_sex": "male", "age_range": "9-13"},
                {"age_sex": "female", "age_range": "14-18"},
                {"age_sex": "male", "age_range": "14-18"},
                {"age_sex": "female", "age_range": "19-30"},
                {"age_sex": "male", "age_range": "19-30"},
                {"age_sex": "female", "age_range": "31-50"},
                {"age_sex": "male", "age_range": "31-50"},
                {"age_sex": "female", "age_range": "51+"},
                {"age_sex": "male", "age_range": "51+"},
            ],
            on_click=constraint_checkbox_on_click,
        )
        self.constraint_checkbox_on_click = constraint_checkbox_on_click
        self.set_constraint_widgets()

    @param.depends("constraints", watch=True)
    def set_constraint_widgets(self):
        constraint_widgets = []
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
            constraint_widgets.append(
                NutrientConstraintWidget(
                    nutrient_nbrs=nutrient_nbrs,
                    label=label,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    equality=equality,
                )
            )
        self.constraint_widgets = constraint_widgets

    @param.depends("constraint_widgets", watch=True)
    def _layout(self):
        return pn.Column(
            self.constraint_checkboxes,
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
