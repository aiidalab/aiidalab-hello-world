#!/usr/bin/env python
import pytest

from selenium.webdriver.common.by import By


def test_example(selenium, url):
    selenium.get(url('apps/apps/app/example.ipynb'))
    selenium.find_element(By.ID, 'ipython-main-app')
    selenium.find_element(By.ID, 'notebook-container')
    selenium.find_element(By.CLASS_NAME, 'jupyter-widgets-view')
    selenium.get_screenshot_as_file('screenshots/example.png')


@pytest.mark.xfail
def test_example_import_error(selenium, url):
    selenium.get(url('apps/apps/app/example-import-error.ipynb'))
    selenium.find_element(By.ID, 'ipython-main-app')
    selenium.find_element(By.ID, 'notebook-container')
    selenium.find_element(By.CLASS_NAME, 'jupyter-widgets-view')
