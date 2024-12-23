import panel as pn
import pandas as pd
import param

NUTRIENT_BANK_PATH = "../data/nutrients.csv"
nutrient_bank_df = pd.read_csv(NUTRIENT_BANK_PATH)

# nutrient_constraints = pd.read_csv("../data/nutrient_constraints.csv")

ADDITIONAL_NUTRIENT_NBRS = [312, 313]
NBR_TO_NUTRIENT_NAME = nutrient_bank_df.set_index(
    "nutrient_nbr"
).nutrient_name.to_dict()
NBR_TO_UNIT = (
    nutrient_bank_df.set_index("nutrient_nbr")
    .unit_name.map({"G": "g", "MG": "mg", "UG": "ug"})
    .to_dict()
)

MAIN_NBRS = {
    208: "calories",
    204: "total_fat",
    606: "saturated_fat",
    605: "trans_fat",
    601: "cholesterol",
    307: "sodium",
    205: "carb",
    291: "dietary_fiber",
    269: "total_sugars",
    203: "protein",
}

HTML_STYLE = """
<style>
    * {
    box-sizing: border-box;
  }
  
  html {
    font-size: 16px;
  }
  
  body {
    font-family: 'Open Sans', sans-serif;
  }
  
  .label {
    border: 2px solid black;
    width: 270px;
    margin: 20px auto;
    padding: 0 7px;
  }
  
  header h1 {
    text-align: center;
    margin: -4px 0;
    letter-spacing: 0.15px
  }
  
  p {
    margin: 0;
    display: flex;
    justify-content: space-between;
  }
  
  .divider {
    border-bottom: 1px solid #888989;
    margin: 2px 0;
  }
  
  .bold {
    font-weight: 800;
  }
  
  .large {
    height: 10px;
  }
  
  .large, .medium {
    background-color: black;
    border: 0;
  }
  
  .medium {
    height: 5px;
  }
  
  .small-text {
    font-size: 0.85rem;
  }
  
  
  .calories-info {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  
  .calories-info h2 {
    margin: 0;
  }
  
  .left-container p {
    margin: -5px -2px;
    font-size: 2em;
    font-weight: 700;
  }
  
  .calories-info span {
    margin: -7px -2px;
    font-size: 2.4em;
    font-weight: 700;
  }
  
  .right {
    justify-content: flex-end;
  }
  
  .indent {
    margin-left: 1em;
  }
  
  .double-indent {
    margin-left: 2em;
  }
  
  .daily-value p:not(.no-divider) {
    border-bottom: 1px solid #888989;
  }
  
  .note {
    font-size: 0.6rem;
    margin: 5px 0;
    padding:8px;
    text-indent:-8px;
  }
</style>
"""


class NutritionFactsView(param.Parameterized):
    nbr_to_amount = param.Dict()
    additional_nutrient_nbrs = param.List(item_type=int, default=[])
    nbr_to_nutrient_name = param.Dict(default=NBR_TO_NUTRIENT_NAME)
    nbr_to_unit = param.Dict(default=NBR_TO_UNIT)

    def __init__(self, **params):
        super().__init__(**params)
        if not self.additional_nutrient_nbrs:
            self.additional_nutrient_nbrs = [
                nbr for nbr in self.nbr_to_amount if nbr not in MAIN_NBRS
            ]

    def get_head(self):
        return """<head>

                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Nutrition Label</title>
                    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700,800" rel="stylesheet">
                    <link href="./nutrition_facts.css" rel="stylesheet">
                </head>
                """

    def get_header_html(self, serving_size="100g"):
        html = """<header>
                    <h1 class="bold">Nutrition Facts</h1>
                    <div class="divider"></div>
                    <!-- <p>8 servings per container</p> -->"""
        html += f'<p class="bold">Serving size <span>{serving_size}</span></p>'
        html += "</header>"
        return html

    def get_calories_html(self, calories_nbr=208):
        html = """
                <div class="divider large"></div>
                <div class="calories-info">
                    <div class="left-container">
                        <!-- <h2 class="bold small-text">Amount per serving</h2> -->
                        <p>Calories</p>
                    </div>
                """
        html += f"<span>{self.nbr_to_amount[calories_nbr]}</span>"
        html += "</div>"
        html += self.get_divider(classes=["medium"])
        return html

    def get_nutrients_box(self):
        html = """<div class="daily-value small-text">"""
        html += self.get_daily_value_text_html()
        html += self.get_divider()
        html += self.get_main_nutrients_html()
        html += self.get_additional_nutrients_html()
        html += "</div>"
        return html

    def get_daily_value_text_html(self):
        return """<p class="bold right no-divider">% Daily Value *</p>"""

    def get_fat_div_html(self):
        html = self.get_total_fat_html()
        html += self.get_saturated_fat_html()
        html += self.get_divider()
        html += self.get_trans_fat_html()
        return html

    def get_total_fat_html(self, total_fat_nbr=204, dv=None):
        html = """<p><span><span class="bold">Total Fat</span> """
        html += f"{self.nbr_to_amount[total_fat_nbr]}{self.nbr_to_unit[total_fat_nbr]}</span>"
        html += self.get_main_nutrient_dv_html(dv)
        html += "</p>"
        return html

    def get_saturated_fat_html(self, saturated_fat_nbr=606, dv=None):
        html = """<p class="indent no-divider">Saturated Fat """
        html += f"{self.nbr_to_amount[saturated_fat_nbr]}{self.nbr_to_unit[saturated_fat_nbr]} "
        html += self.get_main_nutrient_dv_html(dv)
        html += "</p>"
        return html

    def get_trans_fat_html(self, trans_fat_nbr=605):
        html = """<p class="indent no-divider"><span><i>Trans</i> Fat """
        html += f"{self.nbr_to_amount[trans_fat_nbr]}{self.nbr_to_unit[trans_fat_nbr]}"
        html += "</span></p>"
        return html

    def get_cholesterol_html(self, cholesterol_nbr=601, dv=None):
        html = self.get_divider()
        html += f'<p><span><span class="bold">Cholesterol</span> {self.nbr_to_amount[cholesterol_nbr]}{self.nbr_to_unit[cholesterol_nbr]}</span>'
        html += self.get_main_nutrient_dv_html(dv)
        html += "</p>"
        return html

    def get_sodium_html(self, sodium_nbr=307, dv=None):
        html = f'<p><span><span class="bold">Sodium</span> {self.nbr_to_amount[sodium_nbr]}{self.nbr_to_unit[sodium_nbr]}</span>'
        html += self.get_main_nutrient_dv_html(dv)
        html += "</p>"
        return html

    def get_carb_html(
        self,
        carb_nbr=205,
        dietary_fiber_nbr=291,
        total_sugars_nbr=269,
        added_sugars_nbr=539,
        carb_dv=None,
        added_sugars_dv=None,
    ):
        html = f'<p><span><span class="bold">Total Carbohydrate</span> {self.nbr_to_amount[carb_nbr]}{self.nbr_to_unit[carb_nbr]}</span>'
        html += self.get_main_nutrient_dv_html(carb_dv)
        html += "</p>"
        html += f'<p class="indent no-divider">Dietary Fiber {self.nbr_to_amount[dietary_fiber_nbr]}{self.nbr_to_unit[dietary_fiber_nbr]}</p>'
        html += f'<div class="divider"></div>'
        html += f'<p class="indent no-divider">Total Sugars {self.nbr_to_amount[total_sugars_nbr]}{self.nbr_to_unit[total_sugars_nbr]}</p>'
        html += self.get_added_sugars_html()
        return html

    def get_added_sugars_html(self, added_sugars_nbr=539, added_sugars_dv=None):
        if added_sugars_nbr not in self.nbr_to_amount:
            return ""
        html = f'<div class="divider double-indent"></div>'
        html += f'<p class="double-indent no-divider">Includes {self.nbr_to_amount[added_sugars_nbr]}{self.nbr_to_unit[added_sugars_nbr]} Added Sugars'
        html += self.get_main_nutrient_dv_html(added_sugars_dv)
        return html

    def get_protein_html(self, protein_nbr=203):
        html = """<div class="divider"></div>"""
        html += f'<p class="no-divider"><span class="bold">Protein</span> {self.nbr_to_amount[protein_nbr]}{self.nbr_to_unit[protein_nbr]}</p>'
        return html

    def get_main_nutrient_dv_html(self, dv):
        if dv is not None:
            return f'<span class="bold">{dv}%</span>'
        else:
            return f'<span class="bold">N/A %</span>'
        return ""

    def get_main_nutrients_html(self):
        html = self.get_fat_div_html()
        html += self.get_cholesterol_html()
        html += self.get_sodium_html()
        html += self.get_carb_html()
        html += self.get_protein_html()
        return html

    def get_additional_nutrients_html(self):
        html = self.get_divider(
            classes=["large"],
        )
        for i, nbr in enumerate(self.additional_nutrient_nbrs):
            amount = self.nbr_to_amount.get(nbr, 0)
            if i == len(self.additional_nutrient_nbrs) - 1:
                html += self.get_additional_nutrient_html(
                    nutrient_name=self.nbr_to_nutrient_name.get(nbr),
                    amount=amount,
                    unit=self.nbr_to_unit.get(nbr),
                    classes=["no-divider"],
                )
            else:
                html += self.get_additional_nutrient_html(
                    nutrient_name=self.nbr_to_nutrient_name.get(nbr),
                    amount=amount,
                    unit=self.nbr_to_unit.get(nbr),
                )
        return html

    def get_divider(self, classes=[]):
        return f"<div class='divider {" ".join(classes)}'></div>"

    def get_additional_nutrient_html(
        self, nutrient_name, amount, unit=None, dv=None, classes=[]
    ):
        return f'<p class="{" ".join(classes)}">{nutrient_name} {amount}{unit} <span>{"N/A " if dv is None else dv}%</span></p>'

    def get_footer_html(self):
        return """<div class="divider medium"></div>
        <p class="note">* The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a
            daily
            diet. 2,000 calories a day is used for general nutrition advice.</p>"""

    def get_nutrition_facts_body(self):
        html = """<body><div class="label">"""
        html += self.get_header_html()
        html += self.get_calories_html()
        html += self.get_nutrients_box()
        html += self.get_footer_html()
        html += """</div></body>"""
        return html

    def get_nutrition_facts_html(self):
        html = HTML_STYLE
        html += self.get_head()
        html += self.get_nutrition_facts_body()
        return html
