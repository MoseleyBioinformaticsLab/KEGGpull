import pytest as pt
import os

import kegg_pull.__main__ as m


@pt.fixture(autouse=True)
def teardown():
    yield

    os.remove('pull-results.txt')


# TODO: Test from entry ID file and entry ID string
def test_main(mocker):
    mock_database = 'brite'
    mocker.patch('sys.argv', ['kegg_pull', 'multiple', f'--database-name={mock_database}'])
    mock_web_request = mocker.MagicMock()
    MockWebRequest = mocker.patch('kegg_pull.__main__.wr.WebRequest', return_value=mock_web_request)
    mock_single_pull = mocker.MagicMock()
    MockSinglePull = mocker.patch('kegg_pull.__main__.sp.SinglePull', return_value=mock_single_pull)
    mock_entry_ids = ['1', '2', '3']
    mock_from_database = mocker.patch('kegg_pull.__main__.ge.from_database', return_value=mock_entry_ids)

    mock_pull_result = mocker.MagicMock(
        successful_entry_ids=('a', 'b', 'c', 'x'), failed_entry_ids=('y', 'z'), timed_out_entry_ids=()
    )

    mock_pull = mocker.patch('kegg_pull.__main__.mp.SingleProcessMultiplePull.pull', return_value=mock_pull_result)
    mock_multiple_pull = mocker.MagicMock(pull=mock_pull)

    MockSingleProcessMultiplePull = mocker.patch(
        'kegg_pull.__main__.mp.SingleProcessMultiplePull', return_value=mock_multiple_pull
    )

    m.main()
    MockWebRequest.assert_called_once_with(n_tries=None, time_out=None, sleep_time=None)
    MockSinglePull.assert_called_once_with(output_dir='.', web_request=mock_web_request, entry_field=None)
    MockSingleProcessMultiplePull.assert_called_once_with(single_pull=mock_single_pull, force_single_entry=True)
    mock_from_database.assert_called_once_with(database_name=mock_database)
    mock_pull.assert_called_once_with(entry_ids=mock_entry_ids)

    expected_pull_results = '\n'.join([
        '### Successful Entry IDs ###',
        'a',
        'b',
        'c',
        'x',
        '### Failed Entry IDs ###',
        'y',
        'z',
        '### Timed Out Entry IDs ###\n'
     ])

    with open('pull-results.txt', 'r') as f:
        actual_pull_results = f.read()

        assert actual_pull_results == expected_pull_results
