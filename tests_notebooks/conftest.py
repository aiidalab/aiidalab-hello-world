import os
from pathlib import Path
from urllib.parse import urljoin

import pytest
import requests
from playwright.sync_api import expect
from requests.exceptions import ConnectionError

APP_NAME = "aiidalab-hello-world"

# By default, let Playwright assertions retry for 90s
# till a given element is loaded.
expect.set_options(timeout=90_000)


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def screenshot_dir():
    sdir = Path.joinpath(Path.cwd(), "screenshots")
    try:
        os.mkdir(sdir)
    except FileExistsError:
        pass
    return sdir


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(Path(pytestconfig.rootdir) / "tests_notebooks" / "docker-compose.yml")


@pytest.fixture(scope="session")
def docker_compose(docker_services):
    return docker_services._docker_compose


@pytest.fixture(scope="session")
def aiidalab_exec(docker_compose, nb_user):
    """Execute command inside the AiiDAlab test container"""

    def execute(command, user=None, **kwargs):
        workdir = f"/home/{nb_user}/apps/{APP_NAME}"
        if user is None:
            user = nb_user
        command = (
            f"exec --workdir {workdir} -T --user={user} aiidalab bash -c '{command}'"
        )
        return docker_compose.execute(command, **kwargs)

    return execute


@pytest.fixture(scope="session")
def nb_user():
    return "jovyan"


@pytest.fixture(scope="session", autouse=True)
def notebook_service(docker_ip, docker_services, aiidalab_exec, nb_user):
    """Ensure that HTTP service is up and responsive."""
    # Directory ~/apps/home/ is mounted by docker,
    # make it writeable for jovyan user, needed for `pip install`
    aiidalab_exec(f"chmod -R a+rw /home/{nb_user}/apps/{APP_NAME}", user="root")

    aiidalab_exec("pip install --no-cache-dir .")

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("aiidalab", 8888)
    url = f"http://{docker_ip}:{port}"
    token = os.environ["JUPYTER_TOKEN"]
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url, token


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 800, "height": 800},
    }


@pytest.fixture(scope="function")
def notebook_page(page, notebook_service):
    """This is the main fixture to be used in tests.

    We're already guaranteed that the container is up and responding to HTTP requests.
    (via `notebook_service` fixture).
    """

    def _notebook_page(nb_path, url_params=None):
        url, token = notebook_service
        url_with_token = urljoin(url, f"apps/apps/{APP_NAME}/{nb_path}?token={token}")
        if url_params is not None:
            for key, value in url_params.items():
                url_with_token += f"&{key}={value}"
        # By default, let's allow Playwright actions to wait for 90s
        # till a given element is loaded.
        page.set_default_timeout(90_000)
        page.goto(url_with_token)

        page.locator("#ipython-main-app").wait_for(state="attached")
        page.locator("#notebook-container").wait_for(state="attached")
        appmode_busy = page.locator("#appmode-busy")
        appmode_busy.wait_for(state="attached")
        # We wait until the appmode spinner disappears. However,
        # this does not seem to be fully robust, as the spinner might flash
        # while the page is still loading. So we add explicit wait here as well.
        appmode_busy.wait_for(state="hidden", timeout=240_000)
        page.wait_for_timeout(5_000)

        return page

    return _notebook_page


@pytest.fixture
def final_screenshot(request, screenshot_dir, page):
    """Take screenshot at the end of the test.

    Screenshot name is generated from the test function name
    by stripping the 'test_' prefix.
    """
    screenshot_name = f"{request.function.__name__[5:]}.png"
    screenshot_path = Path.joinpath(screenshot_dir, screenshot_name)
    yield
    page.screenshot(path=screenshot_path)
