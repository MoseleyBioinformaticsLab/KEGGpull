"""
Usage:
    kegg_pull rest -h | --help
    kegg_pull rest list <database-name> [--output=<output>]
    kegg_pull rest get <entry-ids> [--entry-field=<entry-field>] [--output=<output>]
    kegg_pull rest find <database-name> <keywords> [--output=<output>]
    kegg_pull rest find <database-name> (--formula=<formula>|--exact-mass=<exact-mass>...|--molecular-weight=<molecular-weight>...) [--output=<output>]

Options:
    list                                    Executes the "list" KEGG API operation.
    <database-name>                         The name of the database to get entry IDs from.
    --output=<output>                       The file to store the response body from the KEGG web API operation. Prints to the console if --output is not specified.
    get                                     Executes the "get" KEGG API operation.
    <entry-ids>                             Comma separated list of IDs of entries to get.
    --entry-field=<entry-field>             Optional field to extract from an entry instead of the default entry info (i.e. flat file or htext in the case of brite entries).
    find                                    Executes the "find" KEGG API operation.
    <keywords>                              Comma separated list of keywords to search entries with.
    --formula=<formula>                     Sequence of atoms in a chemical formula format to search for (e.g. "O5C7" searchers for molecule entries containing 5 oxygen atoms and/or 7 carbon atoms).
    --exact-mass=<exact-mass>               Either a single number (e.g. --exact-mass=155.5) or two numbers (e.g. --exact-mass=155.5 --exact-mass=244.4). If a single number, searches for molecule entries with an exact mass equal to that value rounded by the last decimal point. If two numbers, searches for molecule entries with an exact mass within the two values (a range).
    --molecular-weight=<molecular-weight>   Same as --exact-mass but searches based on the molecular weight.
"""
import docopt as d
import logging as l

from . import kegg_request as kr
from . import kegg_url as ku
from . import utils as u


class KEGGrestAPI:
    def __init__(self, kegg_request: kr.KEGGrequest = None):
        self._kegg_request = kegg_request if kegg_request is not None else kr.KEGGrequest()

    def list(self, database_name: str) -> kr.KEGGresponse:
        list_url = ku.ListKEGGurl(database_name=database_name)

        return self._kegg_request.execute_api_operation(kegg_url=list_url)

    def get(self, entry_ids: list, entry_field: str = None) -> kr.KEGGresponse:
        get_url = ku.GetKEGGurl(entry_ids=entry_ids, entry_field=entry_field)

        return self._kegg_request.execute_api_operation(kegg_url=get_url)

    def keywords_find(self, database_name: str, keywords: list) -> kr.KEGGresponse:
        find_url = ku.KeywordsFindKEGGurl(database_name=database_name, keywords=keywords)

        return self._kegg_request.execute_api_operation(kegg_url=find_url)

    def molecular_find(
        self, database_name: str, formula: str = None, exact_mass: float = None, molecular_weight: int = None
    ) -> kr.KEGGresponse:
        find_url = ku.MolecularFindKEGGurl(
            database_name=database_name, formula=formula, exact_mass=exact_mass, molecular_weight=molecular_weight
        )

        return self._kegg_request.execute_api_operation(kegg_url=find_url)


def main():
    args: dict = d.docopt(__doc__)

    if args['--help']:
        print(__doc__)
        exit(0)

    database_name: str = args['<database-name>']
    output: str = args['--output']
    is_binary = False
    kegg_rest_api = KEGGrestAPI()

    if args['list']:
        kegg_response: kr.KEGGresponse = kegg_rest_api.list(database_name=database_name)
    elif args['get']:
        entry_ids: list = u.split_comma_separated_list(list_string=args['<entry-ids>'])
        entry_field: str = args['--entry-field']

        if ku.GetKEGGurl.is_binary(entry_field=entry_field):
            is_binary = True

        kegg_response: kr.KEGGresponse = kegg_rest_api.get(entry_ids=entry_ids, entry_field=entry_field)
    elif args['find']:
        if args['<keywords>']:
            keywords: list = u.split_comma_separated_list(list_string=args['<keywords>'])
            kegg_response: kr.KEGGresponse = kegg_rest_api.keywords_find(database_name=database_name, keywords=keywords)
        else:
            formula, exact_mass, molecular_weight = u.get_molecular_attribute_args(args=args)

            kegg_response: kr.KEGGresponse = kegg_rest_api.molecular_find(
                database_name=database_name, formula=formula, exact_mass=exact_mass, molecular_weight=molecular_weight
            )
    # TODO: finish the rest of the operations


    if kegg_response.status == kr.KEGGresponse.Status.FAILED:
        raise RuntimeError(
            f'The request to the KEGG web API failed with the following URL: {kegg_response.kegg_url.url}'
        )
    elif kegg_response.status == kr.KEGGresponse.Status.TIMEOUT:
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
        with open(output, save_type) as f:
            f.write(response_body)
