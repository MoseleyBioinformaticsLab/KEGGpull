"""
Usage:
    kegg_pull rest -h | --help
    kegg_pull rest info <database-name> [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest list <database-name> [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest get <entry-ids> [--entry-field=<entry-field>] [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest find <database-name> <keywords> [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest find <database-name> (--formula=<formula>|--exact-mass=<exact-mass>...|--molecular-weight=<molecular-weight>...) [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest conv <kegg-database-name> <outside-database-name> [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest conv --conv-target=<target-database-name> <entry-ids> [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest link <target-database-name> <source-database-name> [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest link --link-target=<target-database-name> <entry-ids> [--test] [--output=<output>] [--zip-file=<zip-file>]
    kegg_pull rest ddi <drug-entry-ids> [--test] [--output=<output>] [--zip-file=<zip-file>]

Options:
    -h --help                               Show this help message.
    info                                    Executes the "info" KEGG API operation, pulling information about a KEGG database.
    <database-name>                         The name of the database to pull information about or entry IDs from.
    [--test]                                If set, test the request to ensure it works rather than sending it. Print True if the request would succeed and False if the request would fail. Ignores --output and/or --zip-file if these options are set along with --test.
    --output=<output>                       The file to store the response body from the KEGG web API operation. Prints to the console if not set. If ends in ".zip", saves file in a zip archive.
    --zip-file=<zip-file>                   The name of the file to store in a zip archive. If not set, defaults to saving a file with the same name as the zip archive minus the .zip extension. Ignored if --output does not end in ".zip".
    list                                    Executes the "list" KEGG API operation, pulling the entry IDs of the provided database.
    get                                     Executes the "get" KEGG API operation, pulling the entries of the provided entry IDs.
    <entry-ids>                             Comma separated list of entry IDs.
    --entry-field=<entry-field>             Optional field to extract from an entry instead of the default entry info (i.e. flat file or htext in the case of brite entries).
    find                                    Executes the "find" KEGG API operation, finding entry IDs based on provided queries.
    <keywords>                              Comma separated list of keywords to search entries with.
    --formula=<formula>                     Sequence of atoms in a chemical formula format to search for (e.g. "O5C7" searchers for molecule entries containing 5 oxygen atoms and/or 7 carbon atoms).
    --exact-mass=<exact-mass>               Either a single number (e.g. --exact-mass=155.5) or two numbers (e.g. --exact-mass=155.5 --exact-mass=244.4). If a single number, searches for molecule entries with an exact mass equal to that value rounded by the last decimal point. If two numbers, searches for molecule entries with an exact mass within the two values (a range).
    --molecular-weight=<molecular-weight>   Same as --exact-mass but searches based on the molecular weight.
    conv                                    Executes the "conv" KEGG API operation, converting entry IDs from an outside database to those of a KEGG database and vice versa.
    <kegg-database-name>                    The name of the KEGG database from which to view equivalent outside database entry IDs.
    <outside-database-name>                 The name of the non-KEGG database from which to view equivalent KEGG database entry IDs.
    --conv-target=<target-database-name>    The outside or KEGG database from which to view equivalent versions of the provided entry IDs. If a KEGG database, the provided entry IDs must be from an outside database and vice versa.
    link                                    Executes the "link" KEGG API operation, showing the IDs of entries that are connected/related to entries of other databases.
    <target-database-name>                  The name of the database to find cross-references in the source database.
    <source-database-name>                  The name of the database from which cross-references are found in the target database.
    --link-target-<target-database-name>    The name of the database to find cross-references in the provided entry IDs.
    ddi                                     Executes the "ddi" KEGG API operation, searching for drug to drug interactions. Providing one entry ID reports all known interactions, while providing multiple checks if any drug pair in a given set of drugs is CI or P. If providing multiple, all entries must belong to the same database.
    <drug-entry-ids>                        Comma separated list of drug entry IDs from the following databases: drug, ndc, or yj
"""
import docopt as d
import logging as l

from . import kegg_url as ku
from . import rest as r
from . import _utils as u


def main():
    args: dict = d.docopt(__doc__)
    database_name: str = args['<database-name>']
    entry_ids: str = args['<entry-ids>']
    output: str = args['--output']
    test: bool = args['--test']
    is_binary = False
    test_result: bool = None
    kegg_response: r.KEGGresponse = None
    kegg_rest = r.KEGGrest()

    if args['info']:
        if test:
            test_result: bool = kegg_rest.test(KEGGurl=ku.InfoKEGGurl, database_name=database_name)
        else:
            kegg_response: r.KEGGresponse = kegg_rest.info(database_name=database_name)
    elif args['list']:
        if test:
            test_result: bool = kegg_rest.test(KEGGurl=ku.ListKEGGurl, database_name=database_name)
        else:
            kegg_response: r.KEGGresponse = kegg_rest.list(database_name=database_name)
    elif args['get']:
        entry_ids: list = u.split_comma_separated_list(list_string=entry_ids)
        entry_field: str = args['--entry-field']

        if test:
            test_result: bool = kegg_rest.test(KEGGurl=ku.GetKEGGurl, entry_ids=entry_ids, entry_field=entry_field)
        else:
            if ku.GetKEGGurl.is_binary(entry_field=entry_field):
                is_binary = True

            kegg_response: r.KEGGresponse = kegg_rest.get(entry_ids=entry_ids, entry_field=entry_field)
    elif args['find']:
        if args['<keywords>']:
            keywords: list = u.split_comma_separated_list(list_string=args['<keywords>'])

            if test:
                test_result: bool = kegg_rest.test(
                    KEGGurl=ku.KeywordsFindKEGGurl, database_name=database_name, keywords=keywords
                )
            else:
                kegg_response: r.KEGGresponse = kegg_rest.keywords_find(database_name=database_name, keywords=keywords)
        else:
            formula, exact_mass, molecular_weight = u.get_molecular_attribute_args(args=args)

            if test:
                test_result: bool = kegg_rest.test(
                    KEGGurl=ku.MolecularFindKEGGurl, database_name=database_name, formula=formula,
                    exact_mass=exact_mass, molecular_weight=molecular_weight
                )
            else:
                kegg_response: r.KEGGresponse = kegg_rest.molecular_find(
                    database_name=database_name, formula=formula, exact_mass=exact_mass, molecular_weight=molecular_weight
                )
    elif args['conv']:
        if args['--conv-target']:
            target_database_name: str = args['--conv-target']
            entry_ids: list = u.split_comma_separated_list(list_string=entry_ids)

            if test:
                test_result: bool = kegg_rest.test(KEGGurl=ku.EntriesConvKEGGurl, target_database_name=target_database_name, entry_ids=entry_ids)
            else:
                kegg_response: r.KEGGresponse = kegg_rest.entries_conv(
                    target_database_name=target_database_name, entry_ids=entry_ids
                )
        else:
            kegg_database_name = args['<kegg-database-name>']
            outside_database_name = args['<outside-database-name>']

            if test:
                test_result: bool = kegg_rest.test(
                    KEGGurl=ku.DatabaseConvKEGGurl, kegg_database_name=kegg_database_name,
                    outside_database_name=outside_database_name
                )
            else:
                kegg_response: r.KEGGresponse = kegg_rest.database_conv(
                    kegg_database_name=kegg_database_name, outside_database_name=outside_database_name
                )
    elif args['link']:
        if args['--link-target']:
            target_database_name: str = args['--link-target']
            entry_ids: list = u.split_comma_separated_list(list_string=entry_ids)

            if test:
                test_result: bool = kegg_rest.test(
                    KEGGurl=ku.EntriesLinkKEGGurl, target_database_name=target_database_name, entry_ids=entry_ids
                )
            else:
                kegg_response: r.KEGGresponse = kegg_rest.entries_link(
                    target_database_name=target_database_name, entry_ids=entry_ids
                )
        else:
            target_database_name: str = args['<target-database-name>']
            source_database_name: str = args['<source-database-name>']

            if test:
                test_result: bool = kegg_rest.test(
                    KEGGurl=ku.DatabaseLinkKEGGurl, target_database_name=target_database_name,
                    source_database_name=source_database_name
                )
            else:
                kegg_response: r.KEGGresponse = kegg_rest.database_link(
                    target_database_name=target_database_name, source_database_name=source_database_name
                )
    else:
        drug_entry_ids: str = args['<drug-entry-ids>']
        drug_entry_ids: list = u.split_comma_separated_list(list_string=drug_entry_ids)

        if test:
            test_result: bool = kegg_rest.test(KEGGurl=ku.DdiKEGGurl, drug_entry_ids=drug_entry_ids)
        else:
            kegg_response: r.KEGGresponse = kegg_rest.ddi(drug_entry_ids=drug_entry_ids)

    if test:
        print(test_result)
    else:
        if kegg_response.status == r.KEGGresponse.Status.FAILED:
            raise RuntimeError(
                f'The request to the KEGG web API failed with the following URL: {kegg_response.kegg_url.url}'
            )
        elif kegg_response.status == r.KEGGresponse.Status.TIMEOUT:
            raise RuntimeError(
                f'The request to the KEGG web API timed out with the following URL: {kegg_response.kegg_url.url}'
            )

        if is_binary:
            response_body: bytes = kegg_response.binary_body
            save_type: str = 'wb'
        else:
            response_body: str = kegg_response.text_body
            save_type: str = 'w'

        if output is None:
            if is_binary:
                l.warning('Printing binary response body')

            print(response_body)
        else:
            if output.endswith('.zip'):
                u.save_to_zip_archive(zip_archive_path=output, zip_file_name=args['--zip-file'], file_content=response_body)
            else:
                with open(output, save_type) as file:
                    file.write(response_body)
