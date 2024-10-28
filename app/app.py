import panel as pn

pn.extension("tabulator")

title_styles = {"font-size": "20px", "font-weight": "bold"}

sidebar_title = pn.pane.Str("Requirements", styles=title_styles)

age_input = pn.widgets.IntInput(name="Age", value=30)

weight_input = pn.widgets.IntInput(name="Weight", value=70)

height_input = pn.widgets.IntInput(name="Height", value=170)

number_demographic_inputs = pn.Column(age_input, weight_input, height_input)


class LabeledRBGroup(pn.Column):
    def __init__(self, options: list[str], label: str, **kwargs):
        self.label = pn.pane.Str(label)
        self.radio_buttons = pn.widgets.RadioButtonGroup(
            options=options, name=label, **kwargs
        )
        super().__init__(self.label, self.radio_buttons)


sex_radio_buttons = LabeledRBGroup(options=["Male", "Female"], label="Sex")

activity_radio_buttons = LabeledRBGroup(
    options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"],
    label="Activity",
)


weight_goal_radio_buttons = LabeledRBGroup(
    options=["Lose", "Maintain", "Gain"], label="Weight Goal"
)

select_demographic_widgets = pn.Column(
    sex_radio_buttons, activity_radio_buttons, weight_goal_radio_buttons
)

demographic_widgets = pn.Column(number_demographic_inputs, select_demographic_widgets)

vegan_check = pn.widgets.Checkbox(name="Vegan")

vegetarian_check = pn.widgets.Checkbox(name="Vegetarian")

pescatarian_check = pn.widgets.Checkbox(name="Pescatarian")

keto_check = pn.widgets.Checkbox(name="Keto")

halal_check = pn.widgets.Checkbox(name="Halal")

kosher_check = pn.widgets.Checkbox(name="Kosher")

label_common_diet_checks = pn.pane.Str("Common Diets")

common_diet_checks = pn.GridBox(
    vegan_check,
    vegetarian_check,
    pescatarian_check,
    keto_check,
    halal_check,
    kosher_check,
    ncols=2,
)

label_common_restrictions = pn.pane.Str("Common Restrictions")

low_sodium_check = pn.widgets.Checkbox(name="Low Sodium")

nut_allergy_check = pn.widgets.Checkbox(name="Nut Allergy")

lactose_intolerant_check = pn.widgets.Checkbox(name="Lactose Intolerant")

gluten_free_check = pn.widgets.Checkbox(name="Gluten Free")

label_common_restrictions_checks = pn.pane.Str("Common Restrictions")

common_restrictions_checks = pn.GridBox(
    low_sodium_check,
    nut_allergy_check,
    lactose_intolerant_check,
    gluten_free_check,
    ncols=2,
)


goals_tab = pn.FlexBox(
    demographic_widgets,
    label_common_diet_checks,
    common_diet_checks,
    label_common_restrictions,
    common_restrictions_checks,
    name="Goals",
    flex_direction="column",
    height=300,
)

foods_tab = pn.FlexBox("Foods", name="Foods")

contraints_tab = pn.FlexBox("Constraints", name="Constraints")

sidebar_content = pn.layout.Tabs(goals_tab, foods_tab, contraints_tab)

sidebar = pn.FlexBox(
    sidebar_title,
    sidebar_content,
    flex_direction="column",
    height=800,
    styles={"background-color": "grey"},
    sizing_mode="stretch_width",
    flex_wrap="nowrap",
)

results_title = pn.pane.Str("Results", styles=title_styles)

results_diet = pn.FlexBox("Beef", "Potato", "Pepper", flex_direction="column")

results_nutrition = pn.FlexBox("Calories", "Protein", "Fat", flex_direction="column")

results_content = pn.FlexBox(results_diet, results_nutrition)

results = pn.FlexBox(
    results_title,
    results_content,
    flex_direction="column",
    align_items="center",
    sizing_mode="stretch_width",
)

content = pn.GridBox(sidebar, results, ncols=2, sizing_mode="stretch_width")

navbar_title = pn.pane.Str("TOD", styles=title_styles)

navbar = pn.FlexBox(navbar_title, flex_direction="row", justify_content="center")

app = pn.FlexBox(navbar, content, flex_direction="column", sizing_mode="stretch_width")

app.servable()
