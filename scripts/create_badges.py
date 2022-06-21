import importlib
import pathlib
import yaml
import requests


def generate_url(property_name: str, property_value: str, property_color: str) -> str:
    badge_name = property_name.split('_')[0]
    badge_value = property_value
    badge_color = property_color
    badge_template = f"https://img.shields.io/badge/{badge_name}-{badge_value}-{badge_color}"
    return badge_template


def get_image(url: str, file_name: str) -> None:
    res = requests.get(url, stream=True)

    if res.status_code == 200:
        with open(str(pathlib.Path(__file__).parent.parent) + '/media/badges/' + file_name + '.svg', 'w') as f:
            f.write(res.text)
    else:
        raise Exception('Download image failure.')


class BadgeColor:
    """Badge color percentage, and stability."""

    BRIGHTGREEN = "brightgreen"
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

    def __getitem__(self, item):
        # If item is integer it is the coverage percentage
        if isinstance(item, int):
            if 0 <= item <= 50 or item > 100:
                return self.RED
            elif 50 < item <= 75:
                return self.YELLOW
            elif 75 < item <= 100:
                return self.BRIGHTGREEN
        # If item is string it is the stability
        elif isinstance(item, str):
            if item == "stable":
                return self.BRIGHTGREEN
            elif item == "unstable":
                return self.RED
            else:
                return self.BRIGHTGREEN


class CreateBadges:

    def __init__(self):
        self._version = None
        self._stability_status = None
        self._coverage_percentage = None
        self._supported_python_versions = None
        self._badge_types = {'coverage_percentage': self.coverage_percentage,
                             'stability_status': self.stability_status,
                             'package_version': self.version,
                             'python_versions': self.supported_python_versions}

    @property
    def version(self) -> str:
        if self._version is None:
            self._version = self.get_version()
        return self._version

    @property
    def stability_status(self) -> str:
        if self._stability_status is None:
            self._stability_status = self.get_stability_status()
        return self._stability_status

    @property
    def coverage_percentage(self) -> str:
        if self._coverage_percentage is None:
            percentage = self.get_coverage_percentage()
            if not 0 < percentage < 100:
                raise ValueError(
                    "Coverage percentage should be between 0 and 100")
            self._coverage_percentage = percentage
        return self._coverage_percentage

    @property
    def supported_python_versions(self) -> str:
        if self._supported_python_versions is None:
            self._supported_python_versions = self.get_supported_python_versions()
        return self._supported_python_versions

    @staticmethod
    def get_stability_status() -> str:
        import pytest
        importlib.reload(pytest)

        test_status = pytest.main(["-x", str(pathlib.Path(__file__).parent.parent) + '/pycognaize/tests'])
        if test_status == 0:
            return "stable"
        else:
            return "unstable"

    @staticmethod
    def get_coverage_percentage() -> int:
        import coverage
        import pytest

        importlib.reload(pytest)
        importlib.reload(coverage)
        coverage.process_startup()

        cov = coverage.Coverage(config_file=True)
        test_path = str(pathlib.Path(__file__).parent.parent) + '/pycognaize/tests'
        cov.start()
        pytest.main(['-x', test_path])
        cov.stop()
        coverage = int(round(cov.report().real))
        return coverage

    @staticmethod
    def get_version() -> str:
        import pycognaize
        importlib.reload(pycognaize)
        return pycognaize.__version__

    @staticmethod
    def get_supported_python_versions():
        workflow_file_path = str(pathlib.Path(__file__).parent.parent) + '/.github/workflows/pytest.yml'
        with open(workflow_file_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        try:
            supported_versions_list = data_loaded['jobs']['build']['strategy']['matrix']['python-version']
            supported_versions = ' | '.join(supported_versions_list)
        except KeyError:
            return "Supported versions not found"
        return supported_versions

    def get_badges(self) -> None:
        for badge_type, badge_value in self._badge_types.items():
            print(f"Generating badge for {badge_type}")
            badge_color = BadgeColor()[badge_value]

            # Special case for coverage
            if badge_type == "coverage_percentage":
                badge_value = str(badge_value) + "%"
            url = generate_url(badge_type, badge_value, badge_color)
            get_image(url, badge_type)


test = CreateBadges()
test.get_badges()
