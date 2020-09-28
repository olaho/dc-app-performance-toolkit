from selenium.webdriver.common.by import By
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS

from selenium_ui.base_page import BasePage
from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Page, Dashboard, TopNavPanel, Editor, \
    Logout


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:view_report")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugin/report")
            page.wait_until_visible((By.ID, 'report_app_element_id'))
        sub_measure()

        @print_timing("selenium_app_custom_action:view_dashboard")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugin/dashboard")
            page.wait_until_visible((By.ID, 'dashboard_app_element_id'))
        sub_measure()
    measure()
