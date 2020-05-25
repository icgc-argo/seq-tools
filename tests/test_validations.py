import os
import json
from glob import glob
from click.testing import CliRunner
from seq_tools.cli import main

test_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))


def pytest_generate_tests(metafunc):
    if 'submission' in metafunc.fixturenames:
        submissions = []

        for submmission_dir in glob(os.path.join(test_dir, 'submissions', '*.*')):
            submissions.append(submmission_dir)

        metafunc.parametrize('submission', submissions)


def test_validate(submission):
    runner = CliRunner()
    result = runner.invoke(main, ['validate', '-d', submission])

    with open(os.path.join(submission, 'expected.json')) as f:
        expected = json.load(f)

    with open(os.path.join(submission, 'report.json')) as f:
        report = json.load(f)

    assert result.exit_code == 0   # this may need to change later

    # disable std output text check for now
    # assert 'status: INVALID. Please find details in' in result.output

    if 'metadata' in expected:
        assert report['metadata'] == expected['metadata']

    if 'files' in expected:
        assert sorted(report['files']) == sorted(expected['files'])

    if 'status' in expected['validation']:
        assert report['validation']['status'] == expected['validation']['status']

    if len(expected['validation']['checks']) == 0:
        assert len(report['validation']['checks']) == 0

    for check in expected['validation']['checks']:
        assert check in report['validation']['checks']
