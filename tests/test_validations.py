import os
import json
import re
from glob import glob
from click.testing import CliRunner
from seq_tools.cli import main
from seq_tools.utils import find_files

test_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))


def find_expected_report_jsonls(metadata_file):
    # pattern of metadata_file: /xxx/yyy/tests/submissions/metadata_file_only/HCC1143N.WGS.meta.json
    # pattern of expected_reports: /xxx/yyy/tests/expected_reports/metadata_file_only/HCC1143N.WGS.meta.validation_report.*.jsonl
    metapath = os.path.basename(os.path.dirname(metadata_file))
    metafile_pre = os.path.splitext(os.path.basename(metadata_file))[0]
    expected_report_pattern = os.path.join(
        test_dir, 'expected_reports', metapath, '%s.validation_report.*.jsonl' % metafile_pre)
    return glob(expected_report_pattern)


def pytest_generate_tests(metafunc):
    if 'submission' in metafunc.fixturenames:
        submissions = []

        for metadatq_file in sorted(glob(os.path.join(test_dir, 'submissions', '*', '*.json'))):
            seq_files = find_files(
                            os.path.dirname(metadatq_file),
                            r'^.+?\.(bam|fq\.gz|fastq\.gz|fq\.bz2|fastq\.bz2)$'
                        )
            submissions.append([metadatq_file, seq_files])

        metafunc.parametrize('submission', submissions, ids=[s[0] for s in submissions])


def test_validate(submission):
    runner = CliRunner()
    metadata_file, seq_files = submission
    cli_option = ['validate', metadata_file]
    if not seq_files:
        cli_option += ['-d', 'seq-data/']

    runner.invoke(main, cli_option)

    expected_report_jsonls = find_expected_report_jsonls(metadata_file)
    assert len(expected_report_jsonls) > 0

    for expected_report in expected_report_jsonls:
        report = '.'.join(expected_report.split('.')[-3:])

        # now just compare
        with open(expected_report) as f:
            expected_str = f.read()
            expected_str = re.sub(r' under: .+\.log"', ' under: xxx/logs/yyy.log"', expected_str)  # remove run-dependent path
            expected_obj = json.loads(expected_str)

        assert os.path.isfile(report)
        with open(report) as f:
            report_str = f.read()
            report_str = re.sub(r' under: .+\.log"', ' under: xxx/logs/yyy.log"', report_str)  # remove run-dependent path
            report_obj = json.loads(report_str)

        if 'status' in expected_obj['validation']:
            assert report_obj['validation']['status'] == expected_obj['validation']['status']

        assert len(report_obj['validation']['checks']) == len(expected_obj['validation']['checks'])

        for check in expected_obj['validation']['checks']:
            assert check in report_obj['validation']['checks']
