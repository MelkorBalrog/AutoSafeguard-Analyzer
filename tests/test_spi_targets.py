from AutoML import FaultTreeApp


def test_get_spi_targets_filters_missing_validation_targets():
    class SG:
        def __init__(self, desc, v_target=None):
            self.validation_desc = ""
            self.safety_goal_description = desc
            self.user_name = desc
            self.validation_target = v_target
            self.safety_goal_asil = ""
    class App:
        _spi_label = FaultTreeApp._spi_label
        get_spi_targets = FaultTreeApp.get_spi_targets
        def __init__(self):
            self.top_events = [SG("SPI1", 1e-5), SG("NoSPI", None)]
    app = App()
    assert app.get_spi_targets() == ["SPI1"]
