import types
from AutoML import AutoMLApp


def test_enable_stpa_without_pillow():
    app = AutoMLApp.__new__(AutoMLApp)
    app.tool_listboxes = {}
    app.tool_actions = {}
    app.tool_categories = {}
    app.work_product_menus = {}
    app.enabled_work_products = set()
    app.update_views = lambda: None
    app.enable_process_area = lambda area: None
    app.manage_architecture = lambda: None
    app.show_requirements_editor = lambda: None
    AutoMLApp.enable_work_product(app, "STPA")
    assert "STPA" in app.enabled_work_products
