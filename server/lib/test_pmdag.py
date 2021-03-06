############################ IMPORTS ############################
from collections import OrderedDict
import pytest
import networkx as nx

from lib.pmdag import PMDAG
from lib.node import create_appropriate_node

############################ HELPERS ############################
def fill_sample_custom_nodes():
	# creates a graph with a handful of our custom Node objects, but no edges
	pre_a = {"type":"theorem","description":"This is node aaaaaaaaaa","name":"A","importance":3}
	a = create_appropriate_node(pre_a)
	pre_b = {"type":"theorem","description":"This is node bbbbbbbbbb","name":"B","importance":4}
	b = create_appropriate_node(pre_b)
	pre_c = {"type":"theorem","description":"This is node cccccccccc","name":"C","importance":4}
	c = create_appropriate_node(pre_c)
	pre_d = {"type":"theorem","description":"This is node dddddddddd","name":"D","importance":6}
	d = create_appropriate_node(pre_d)
	pre_e = {"type":"theorem","description":"This is node eeeeeeeeee","name":"E","importance":8}
	e = create_appropriate_node(pre_e)
	G = PMDAG()
	G.add_n(a)
	G.add_n(b)
	G.add_n(c)
	G.add_n(d)
	G.add_n(e)
	return G

############################## MAIN ##############################
def test_n():
	pass
	# TODO

def test_add_n():
	pass
	# TODO

def test_as_js_ready_dict():
	pre_a = {"type":"theorem","description":"This is node aaaaaaaaaa","name":"A","importance":3}
	a = create_appropriate_node(pre_a)
	pre_b = {"type":"theorem","description":"This is node bbbbbbbbbb","name":"B","importance":4}
	b = create_appropriate_node(pre_b)
	pre_c = {"type":"theorem","description":"This is node cccccccccc","name":"C","importance":4}
	c = create_appropriate_node(pre_c)

	G = PMDAG()
	d = G.as_js_ready_dict()
	assert d == {'nodes': [], 'links': []}

	G = PMDAG()
	G.add_n(a)
	d = G.as_js_ready_dict()
	assert d == {'nodes': [a.__dict__], 'links': []}

	G = PMDAG()
	G.add_n(a)
	G.add_n(b)
	d = G.as_js_ready_dict()
	dl = d['links']
	dn = d['nodes']
	assert dl == []
	assert (dn == [a.__dict__, b.__dict__] or dn == [b.__dict__, a.__dict__])

	G = PMDAG()
	G.add_n(a)
	G.add_n(b)
	G.add_edge('a', 'b')
	d = G.as_js_ready_dict()
	dl = d['links']
	dn = d['nodes']
	assert (dl == [{'source': 'a', 'target': 'b'}])
	assert (dn == [a.__dict__, b.__dict__] or dn == [b.__dict__, a.__dict__])

	G = PMDAG()
	G.add_n(a)
	G.add_n(b)
	G.add_n(c)
	G.add_path(['a', 'b', 'c'])
	d = G.as_js_ready_dict()
	dl = d['links']
	dn = d['nodes']
	assert (	#ordering is ambiguous so check each possibility
		dl == [{'source': 'a', 'target': 'b'}, {'source': 'b', 'target': 'c'}]
		or
		dl == [{'source': 'b', 'target': 'c'}, {'source': 'a', 'target': 'b'}]
		)
	assert (
		dn == [a.__dict__, b.__dict__, c.__dict__] or dn == [a.__dict__, c.__dict__, b.__dict__]
		or dn == [b.__dict__, a.__dict__, c.__dict__] or dn == [b.__dict__, c.__dict__, a.__dict__]
		or dn == [c.__dict__, a.__dict__, b.__dict__] or dn == [c.__dict__, b.__dict__, a.__dict__]
		)

def test_unselected_dependency_tree():
	G = PMDAG()
	G.add_path(['l1', 't'])
	assert G.unselected_dependency_tree('t', ['l1']) == {'t'}

	G = PMDAG()
	G.add_path(['l1', 'u1', 't']) #selected, unselected, target
	with pytest.raises(nx.NetworkXError):
		G.unselected_dependency_tree('NotANode', ['l1'])
	with pytest.raises(nx.NetworkXError):
		G.unselected_dependency_tree(['t'], ['l1'])
	assert G.unselected_dependency_tree('t', ['l1']) == {'u1', 't'}
	with pytest.raises(ValueError):
		G.unselected_dependency_tree('t', 'l1')
	assert G.unselected_dependency_tree('t', []) == {'l1', 'u1', 't'}
	assert G.unselected_dependency_tree('t', ['NotANode', 'StillNotANode']) == {'l1', 'u1', 't'}

	G = PMDAG()
	G.add_path(['l1', 'u1', 't'])
	G.add_path(['u2', 'u1'])
	assert G.unselected_dependency_tree('t', ['l1']) == {'u1', 'u2', 't'}
	assert G.unselected_dependency_tree('t', []) == {'u1', 'u2', 'l1', 't'}
	assert G.unselected_dependency_tree('t', ['l1', 'u1']) == {'t'}

	G = PMDAG()
	G.add_path(['l1', 'u1', 't'])
	G.add_edge('u2', 't')
	assert G.unselected_dependency_tree('t', ['l1']) == {'u1', 'u2', 't'}

	G = PMDAG()
	G.add_path(['l1', 'u1', 't'])
	G.add_edge('u3', 'l1')
	assert G.unselected_dependency_tree('t', ['l1']) == {'u1', 't'}

	G = PMDAG()
	G.add_path(['l1', 'u1', 't'])
	G.add_path(['u4', 'l2', 't'])
	assert G.unselected_dependency_tree('t', ['l1', 'l2']) == {'u1', 't'}

def test_unselected_count():
	G = PMDAG()
	G.add_path(['l1', 'u1', 't'])
	with pytest.raises(nx.NetworkXError):
		G.unselected_count('NotANode', ['l1'])
	with pytest.raises(nx.NetworkXError):
		G.unselected_count(['t'], ['l1'])
	with pytest.raises(ValueError):
		G.unselected_count('t', 'l1')
	assert G.unselected_count('t', ['NotANode']) == 3
	assert G.unselected_count('t', []) == 3
	assert G.unselected_count('t', ['l1']) == 2
	assert G.unselected_count('t', ['u1']) == 1

def test_unselected_counts():
	G = PMDAG()
	G.add_path(['l1', 'u1', 't'])
	assert G.unselected_counts(['t', 'u1'], []) == [3, 2]

def test_most_important():
	a = create_appropriate_node({"type":"theorem","description":"This is node aaaaaaaaaa","name":"A","importance":3})
	b = create_appropriate_node({"type":"theorem","description":"This is node bbbbbbbbbb","name":"B","importance":4})
	c = create_appropriate_node({"type":"theorem","description":"This is node cccccccccc","name":"C","importance":4})
	d = create_appropriate_node({"type":"theorem","description":"This is node dddddddddd","name":"D","importance":6})
	e = create_appropriate_node({"type":"theorem","description":"This is node eeeeeeeeee","name":"E","importance":8})
	f = create_appropriate_node({"type":"theorem","description":"This is node ffffffffff","name":"F","importance":8})

	# we will REUSE the SAME graph for below tests:
	G = PMDAG()
	G.add_n([a, b, c, d, e, f])

	#testing sort by node's own importance and id
	with pytest.raises(ValueError):
		G.most_important([], 1)

	# trivial test
	assert G.most_important(['a'], 1) == ['a']

	# test that number defaults to 1
	assert G.most_important(['a']) == ['a']

	# bad number
	with pytest.raises(ValueError):
		G.most_important(['a'], -1)

	# and more...
	assert G.most_important(['a', 'b']) == ['b']
	assert G.most_important(['a', 'b'], 2) == ['b', 'a']
	with pytest.raises(ValueError):
		G.most_important(['a', 'b'], 4) == ['b', 'a']
	assert G.most_important(['a', 'b', 'c'], 2) == ['c', 'b'] #sorts alphabetically, but remember we use reverse=True to sort by numerical importance so the alphabetical sort is reversed too
	assert G.most_important(['a', 'b', 'c', 'd']) == ['d']
	assert G.most_important(['a', 'b', 'c', 'd'], 2) == ['d', 'c']
	assert G.most_important(['a', 'b', 'c', 'd'], 3) == ['d', 'c', 'b']


	# using DIFFERENT graphs for the BELOW TESTS:

	#testing sort by weighted importance of neighbors when node's own importance is a tie
	G = PMDAG()
	G.add_n([a, b, c, d, e, f])
	G.add_edges_from([
			['a', 'c'], ['d', 'b']	#d is a more important neighbor than a, so b should be more important than c
	])
	node_list = ['b', 'c']
	assert G.most_important(node_list, 2) == ['b', 'c']

	G = PMDAG()
	G.add_n([a, b, c, d, e, f])
	G.add_edges_from([
			['c', 'a'], ['b', 'd']
	])
	node_list = ['b', 'c']
	assert G.most_important(node_list, 2) == ['b', 'c']

	G = PMDAG()
	G.add_n([a, b, c, d, e, f])
	G.add_edges_from([
			['c', 'a'], ['d', 'b']	#d is a more important neighbor than a but this time a is a descendant while d is only an ancestor; this time c should be more important than b
	])
	node_list = ['b', 'c']
	assert G.most_important(node_list, 2) == ['c', 'b']

	#remember that when the nodes being compared are neighbors with each other, we will get some shared common neighbors, although they have different distances to the two compared nodes
	G = PMDAG()
	G.add_n([a, b, c, d, e, f])
	G.add_edge('b', 'c')
	node_list = ['b', 'c']
	assert G.most_important(node_list, 2) == ['b', 'c']	#descendants are given more weight
	G.add_edge('c', 'b')
	assert G.most_important(node_list, 2) == ['c', 'b']	#now sorts (reverse) alphabetically because neighbor weights are symmetric

def test_choose_destination():
	# NOTE: our criteria for which destination to choose may change in the future.  In which case, some of the tests below may fail
	a = create_appropriate_node({"type":"theorem","description":"This is node aaaaaaaaaa","name":"A","importance":5})
	b = create_appropriate_node({"type":"theorem","description":"This is node bbbbbbbbbb","name":"B","importance":5})
	c = create_appropriate_node({"type":"theorem","description":"This is node cccccccccc","name":"C","importance":5})
	d = create_appropriate_node({"type":"theorem","description":"This is node dddddddddd","name":"D","importance":5})
	e = create_appropriate_node({"type":"theorem","description":"This is node eeeeeeeeee","name":"E","importance":5})
	f = create_appropriate_node({"type":"theorem","description":"This is node ffffffffff","name":"F","importance":5})

	# choose deepest destination
	G = PMDAG()
	G.add_n([a, b, c, d, e, f])
	G.add_path(['a', 'b', 'c'])
	G.add_path(['a', 'd', 'e', 'f'])
	assert G.choose_destination(['a'], ['b', 'd', 'e']) == 'f'

	# make sure this case is symmetric and node id does not affect it:
	G = PMDAG()
	G.add_n([a, b, c, d, e, f])
	G.add_path(['a', 'b', 'f'])
	G.add_path(['a', 'd', 'e', 'c'])
	assert G.choose_destination(['a'], ['b', 'd', 'e']) == 'c'

	# next sort by unselected count:
	G = PMDAG()
	G.add_n([a, c, d, e])
	G.add_edges_from([
		('a', 'c'), ('a', 'd'), ('e', 'd')
	])
	d.importance = 10
	c.importance = 3
	# d now has a higher unselected count than c but the same depth (d is more important)
	assert G.choose_destination(['a'], ['a']) == 'c'

	# again make sure this is symmetric:
	G = PMDAG()
	G.add_n([a, c, d, e])
	G.add_edges_from([
		('a', 'd'), ('a', 'c'), ('e', 'c')
	])
	d.importance = 10
	c.importance = 3
	# d now has a higher unselected count than c but the same depth (d is more important)
	assert G.choose_destination(['a'], ['a']) == 'd'

	# then sort by importance:
	G = PMDAG()
	G.add_n([a, b, c, d])
	G.add_edges_from([
		('a', 'b'), ('b', 'c'), ('b', 'd')
	])
	d.importance = 10
	c.importance = 3
	# same depth and unselected count but d is more important than c
	assert G.choose_destination(['a'], ['b']) == 'd'

	#finally sort by id
	G = PMDAG()
	G.add_n([a, b, c, d])
	G.add_edges_from([
		('a', 'd'),
		     ('d', 'b'),
		     ('d', 'c'),
	])
	# this goes in alphabetical order, unlike digraph.most_important which goes in reverse alphabetical
	assert G.choose_destination(['a'], ['d']) == 'b'

def test_selectable_predestinations():
	G = PMDAG()
	G.add_path(['l1', 't'])
	with pytest.raises(nx.NetworkXError):
		G.selectable_predestinations(['t'], ['l1'])
	with pytest.raises(ValueError):
		G.selectable_predestinations('t', 'l1')
	assert G.selectable_predestinations('t', []) == {'l1'}
	assert G.selectable_predestinations('t', ['l1']) == {'t'}

	G = PMDAG()
	G.add_edges_from([
		('l1', 't'), ('u1', 't') # selected, unselected, target
	])
	assert G.selectable_predestinations('t', ['l1']) == {'u1'}

	G = PMDAG()
	G.add_edges_from([
		('l1', 't'), ('l2', 'u1'), ('u1', 't'), ('u2', 't')
	])
	assert G.selectable_predestinations('t', ['l1', 'l2']) == {'u1', 'u2'}

def test_choose_selectable_predestinations():
	G = fill_sample_custom_nodes()
	G.add_edge('a', 'b')
	with pytest.raises(ValueError):
		print(G.choose_selectable_predestinations(['b'], 'a'))
	assert G.choose_selectable_predestinations(['b'], ['a']) == ['b']

	#first sort by unselected count
	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('b', 'c'), ('a', 'd')
	])
	assert G.choose_selectable_predestinations(['c', 'd'], ['a']) == ['d']

	#then sort by importance
	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('a', 'c'), ('a', 'd')
	])
	assert G.choose_selectable_predestinations(['b', 'c', 'd'], ['a']) == ['d']

	#finally sort by name
	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('a', 'c')
	])
	assert G.choose_selectable_predestinations(['b', 'c'], ['a']) == ['b']

	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('a', 'c')
	])
	assert G.choose_selectable_predestinations(['a'], []) == ['a']
	assert G.choose_selectable_predestinations(['a'], ['a']) == ['b']

	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('b', 'c'), ('b', 'd')
	])
	assert G.choose_selectable_predestinations(['a'], ['b']) == ['d']

	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('b', 'c'), ('b', 'd'), ('e', 'd')
	])
	assert G.choose_selectable_predestinations(['a'], ['b']) == ['c']

	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('b', 'c'), ('b', 'd'), ('e', 'c'), ('e', 'd'), ('b', 'e')
	])
	assert G.choose_selectable_predestinations(['a'], ['b']) == ['e']

	G = fill_sample_custom_nodes()
	G.add_edges_from([
		('a', 'b'), ('a', 'c'), ('d', 'b'), ('e', 'c'), ('a', 'd'), ('a', 'e')
	])
	assert G.choose_selectable_predestinations(['a'], ['a']) == ['e']
