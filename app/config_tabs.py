import panel as pn


class ConfigTabs(pn.Tabs):

    def __init__(self, food_config_tab, nutrient_config_tab, *args, **kwargs):
        self.food_config_tab = food_config_tab
        self.nutrient_config_tab = nutrient_config_tab
        super().__init__(self.food_config_tab, self.nutrient_config_tab)
