import panel as pn

instructions_title_markdown = pn.pane.Markdown(
    """
    # TOD: The Optimal Diet
    ---

    ### Use this app to find the cost-optimal diet that satisfies all of your nutritional needs.
    ___
    """
)

instructions_instructions_markdown = pn.pane.Markdown(
    """

    ## Instructions
    1. Select the foods to include in the optimization.
    2. Set your nutritional constraints.
    3. Click **Optimize**!

    <br>
    """
)

instructions_about_markdown = pn.pane.Markdown(
    """

    ## How it works?
    - The app solves a linear program using the [PuLP](https://coin-or.github.io/pulp/) library.
    - The problem is to minimize the cost of the diet while satisfying all of the nutritional constraints.
    - Nutritional data is sourced from the [USDA Food Database](https://usda.gov).
    - Pricing data has been set manually to reflect real-world wholesale prices in the United States. Pricing assumptions may be changed below.
    - Nutritional constraints were sourced from multiple sources, including [here](https://odphp.health.gov/sites/default/files/2019-09/Appendix-E3-1-Table-A4.pdf). Nutritional constraints may also be modified below.

    """
)

instructions = pn.Column(
    instructions_title_markdown,
    pn.Accordion(("Instructions", instructions_instructions_markdown)),
    pn.Accordion(("How it Works", instructions_about_markdown), margin=(15, 0, 0, 0)),
)

# instructions = pn.FlexBox(
#     instructions_markdown,
#     flex_direction="column",
#     justify_content="center",
#     align_items="center",
#     align_content="center",
#     margin=(100, 0, 50, 0),
#     width=500,
#     height=500,
#     sizing_mode="fixed",
#     styles={
#         "background-color": "lightgrey",
#         "border-radius": "25px",
#         "padding": "25px",
#     },
# )
