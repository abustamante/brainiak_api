from tests.sparql import QueryTestCase

from brainiak.schema.resource import build_class_schema_query, \
        _query_superclasses, query_superclasses
from brainiak import triplestore


class ClassSchemaQueryTestCase(QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/schemas.n3"]

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query: self.query(query)

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_query_superclasses(self):
        params = {"class_uri": "http://example.onto/City"}

        expected_bindings = [{u'class': {u'type': u'uri', u'value': u'http://example.onto/City'}},
                             {u'class': {u'type': u'uri', u'value': u'http://example.onto/Place'}}]

        response = _query_superclasses(params)
        self.assertEqual(response["results"]["bindings"], expected_bindings)

    def test_query_superclasses_result(self):
        params = {"class_uri": "http://example.onto/City"}

        expected_list = [u'http://example.onto/City',
                             u'http://example.onto/Place']

        response = query_superclasses(params)
        self.assertEqual(response, expected_list)

    def test_schema_with_label_and_comment_in_pt(self):
        params = {"class_uri": "http://example.onto/Place",
                  "graph_uri": self.graph_uri,
                  "lang": "pt"}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Procure no dicionario.'},
                              u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Lugar'}}]

        self.assertEqual(response_bindings, expected_bindings)

    def test_schema_with_label_and_comment_in_en(self):
        params = {"class_uri": "http://example.onto/Place",
                  "graph_uri": self.graph_uri,
                  "lang": "en"}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'comment': {u'xml:lang': u'en', u'type': u'literal', u'value': u'Search in the dictionary.'},
                              u'title': {u'xml:lang': u'en', u'type': u'literal', u'value': u'Place'}}]

        self.assertEqual(response_bindings, expected_bindings)

    def test_schema_with_label_and_comment_without_lang(self):
        params = {"class_uri": "http://example.onto/PlaceWithoutLanguage",
                  "graph_uri": self.graph_uri,
                  "lang": False}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'comment': {u'type': u'literal', u'value': u'Search in the dictionary.'},
                              u'title': {u'type': u'literal', u'value': u'Place'}}]

        self.assertEqual(response_bindings, expected_bindings)

    def test_schema_with_label_and_without_comment(self):
        params = {"class_uri": "http://example.onto/Lugar",
                  "graph_uri": self.graph_uri,
                  "lang": False}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'title': {u'type': u'literal', u'value': u'Lugar'}}]

        self.assertEqual(response_bindings, expected_bindings)
