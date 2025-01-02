import panel as pn

title_styles = {"font-size": "20px", "font-weight": "bold"}

navbar_title = pn.pane.Str("TOD", styles=title_styles)

navbar = pn.FlexBox(navbar_title, flex_direction="row", justify_content="center")
