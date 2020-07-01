#!/usr/bin/env python
import pytest

from selenium.webdriver.common.by import By


def test_example(selenium, url):
    selenium.get(url('apps/apps/app/example.ipynb'))
    selenium.find_element(By.ID, 'ipython-main-app')
    selenium.find_element(By.ID, 'notebook-container')
    selenium.find_element(By.CLASS_NAME, 'jupyter-widgets-view')
    selenium.get_screenshot_as_file('screenshots/example.png')


def test_tests_notebook(selenium, url):  #  backend tests
    selenium.get(url('apps/apps/app/tests.ipynb'))
    selenium.find_element(By.ID, 'ipython-main-app')
    selenium.find_element(By.ID, 'notebook-container')
    output = selenium.find_element(By.CSS_SELECTOR, '.output_area')
    print(output.text)
    assert 'ModuleNotFoundError' not in test_output.text
    test_output = selenium.find_element(By.CSS_SELECTOR, '.output_stdout')
    # Print test output, which will be shown in case that tests failed.
    print(test_output.text)
    assert 'FAILURES' not in test_output.text
