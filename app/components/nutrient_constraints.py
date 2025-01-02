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


class NutrientConstraintDefaultSelector(Viewer):

    constraint_options = param.List(item_type=dict)

    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click
        self.select = pn.widgets.Select(
            options={
                constraint_option["age_sex"]
                + " "
                + constraint_option["age_range"]: constraint_option
                for constraint_option in self.constraint_options
            }
        )

        def on_button_click(event):
            self._on_click(self.select.value["age_sex"], self.select.value["age_range"])

        self.set_constraints_button = pn.widgets.Button(
            name="Set Constraints", button_type="primary"
        )

        pn.bind(on_button_click, self.set_constraints_button, watch=True)

    def _layout(self):
        return pn.Row(self.select, self.set_constraints_button)

    def __panel__(self):
        return self._layout


class NutrientConstraints(Viewer):

    constraints_file_path = param.String(constant=True)
    age_sex = param.String(default="male")
    age_range = param.String(default="19-30")
    nutrient_bank = param.ClassSelector(class_=NutrientBank)
    constraint_widgets = param.List(default=None)

    def __init__(self, **params):
        super().__init__(**params)
        self.set_constraints()
        self.constraint_selector = NutrientConstraintDefaultSelector(
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
            on_click=self.set_age_sex_and_age_range,
        )
        self.set_constraint_widgets()

    def set_age_sex_and_age_range(self, age_sex="male", age_range="19-30"):
        self.param.update(age_sex=age_sex, age_range=age_range)

    def set_constraints(self):
        constraints = Constraints()
        constraints.add_nutrient_constraints_from_json(
            json_path=self.constraints_file_path,
            age_sex=self.age_sex,
            age_range=self.age_range,
        )
        self.constraints = constraints

    @param.depends("age_sex", "age_range", watch=True)
    def set_constraint_widgets(self):
        self.set_constraints()
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

    @param.depends("constraint_widgets")
    def _layout(self):
        return pn.Column(
            self.constraint_selector,
            pn.Column(
                pn.FlexBox(
                    *self.constraint_widgets,
                    sizing_mode="stretch_width",
                    flex_direction="row",
                ),
                height=400,
                scroll=True,
            ),
        )

    def get_constraints(self):
        constraints = {}
        for nutrient_constraint_widget in self.constraint_widgets:
            constraints.update(nutrient_constraint_widget.get_constraints())
        return constraints

    def __panel__(self):
        return self._layout
