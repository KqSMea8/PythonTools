#!/usr/bin/python
#coding=utf-8

from xml.etree.ElementTree import ElementTree, Element

""" read and parse the xml file
    in_path: the xml file path
	return : ElementTree
"""
def read_xml(in_path):
	tree = ElementTree()
	tree.parse(in_path)
	return tree

def write_xml(tree, out_path):
	tree.write(out_path, encoding="utf-8", xml_declaration=True)

def if_match(node, kv_map):
	for key in kv_map:
		if node.get(key) != kv_map.get(key):
			return False
	return True

def find_nodes(tree, path):
	return tree.findall(path)

def get_node_by_keyvalue(nodelist, kv_map):
	result_nodes=[]
	for node in nodelist:
		if if_match(node, kv_map):
			result_nodes.append(node)
	
	return result_nodes

def change_node_properties(nodelist, kv_map, is_delete=False):
	for node in nodelist:
		for key in kv_map:
			if is_delete:
				if key in node.attrib:
					del node.attrib[key]
			else:
				node.set(key, kv_map.get(key))

def change_node_text(nodelist, text, is_add=False, is_delete=False):
	for node in nodelist:
		if is_add:
			node.text += text
		elif is_delete:
			node.text = ""
		else:
			node.text = text


