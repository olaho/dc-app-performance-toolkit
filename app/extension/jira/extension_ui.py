from selenium.webdriver.common.by import By
from selenium_ui.conftest import print_timing
from util.conf import JIRA_SETTINGS

from selenium_ui.base_page import BasePage
from selenium_ui.jira.pages.pages import Login, PopupManager, Issue, Project, Search, ProjectsList, \
    BoardsList, Board, Dashboard, Logout


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:view_report")
        def sub_measure():
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugin/report")
            page.wait_until_visible((By.ID, 'report_app_element_id'))
        sub_measure()

        @print_timing("selenium_app_custom_action:view_dashboard")
        def sub_measure():
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugin/dashboard")
            page.wait_until_visible((By.ID, 'dashboard_app_element_id'))
        sub_measure()
    measure()
