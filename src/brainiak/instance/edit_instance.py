from tornado.web import HTTPError
from brainiak import triplestore
from brainiak.utils.sparql import is_result_true, create_explicit_triples, create_implicit_triples,\
    join_triples, is_modify_response_successful, join_prefixes


def edit_instance(query_params, instance_data):
    try:
        instance_uri = query_params['instance_uri']
        graph_uri = query_params['graph_uri']
        class_uri = query_params['class_uri']
    except KeyError as ex:
        raise HTTPError(404, log_message="Parameter <{0:s}> is missing in order to update instance.".format(ex))

    triples = create_explicit_triples(instance_uri, instance_data)
    implicit_triples = create_implicit_triples(instance_uri, class_uri)
    triples.extend(implicit_triples)
    unique_triples = set(triples)
    string_triples = join_triples(unique_triples)

    prefixes = instance_data.get("@context", {})
    string_prefixes = join_prefixes(prefixes)

    response = modify_instance(string_triples, instance_uri, graph_uri, string_prefixes)
    if not is_modify_response_successful(response):
        raise HTTPError(500, log_message="Triplestore could not update triples.")


MODIFY_QUERY = u"""
%(prefix)s
MODIFY GRAPH <%(graph_uri)s>
DELETE
{ <%(instance_uri)s> ?predicate ?old_value }
INSERT
{ %(triples)s }
WHERE
{ <%(instance_uri)s> ?predicate ?old_value }
"""


def modify_instance(triples, instance_uri, graph_uri, string_prefixes):
    query = MODIFY_QUERY % {
        "triples": triples,
        "instance_uri": instance_uri,
        "graph_uri": graph_uri,
        "prefix": string_prefixes
    }
    return triplestore.query_sparql(query)


QUERY_INSTANCE_EXISTS_TEMPLATE = """
ASK
FROM <%(graph_uri)s>
WHERE {
   <%(instance_uri)s> ?p ?o
}
"""


def instance_exists(query_params):
    query = QUERY_INSTANCE_EXISTS_TEMPLATE % query_params
    result_dict = triplestore.query_sparql(query)
    return is_result_true(result_dict)