from playwright.sync_api import expect


def test_example(notebook_page, final_screenshot):
    page = notebook_page("notebooks/example.ipynb")
    expect(page.locator("#ipython-main-app")).to_be_attached()
    expect(page.locator("#notebook-container")).to_be_attached()
    expect(page.locator(".jupyter-widgets-view").first).to_be_visible()
