# -*- coding: utf-8 -*-
__author__ = 'Brandon Ogle'

from pandas import DataFrame
import pandas as pd
import networkx as nx
import numpy as np

def prep_data(network, metrics):
    """Preps data"""

    loc_tol = 1 # meters at the equator, tolerance is stricter towards the poles
    earth_rad = 6371000 # average radius (meters)
    earth_cir = 2*np.pi*earth_rad # cirumference of earth
    meters_degree = (earth_cir / 360) # meters per degree longitude at the equator
    float_tol = loc_tol / meters_degree # convert meter tolerance to lat_lon

    # convert the node names from coords to integers, cache the coords as attrs
    network = nx.convert_node_labels_to_integers(network, label_attribute='coords')

    # create a dataframe with the network nodes with int label index, attrs as cols
    node_df = DataFrame(network.node).T

    # join (x,y) coords to create a 'metrics coords'
    metrics['m_coords'] = map(tuple, metrics[['X', 'Y']].values)
    
    # cast coords to tuples (hashable)
    node_df['coords'] = node_df['coords'].apply(tuple)
    metrics['m_coords'] = metrics['m_coords'].apply(tuple)
    
    # build a vector of all the coordinates in the metrics dataframe
    coords_mat = np.vstack(metrics['m_coords'].values)

    # eucdist takes a coordinate pair and computes the euclidean distance from all the coords in coords_mat
    # fuzzy_match takes a coordinate pair and returns the approximate match from the metrics dataframe using float_tol
    eucdist = lambda coords: np.sqrt(np.sum(np.square(coords_mat - coords), axis=1))
    fuzzy_match = lambda coords: coords_mat[eucdist(coords) < float_tol**2]

    # map over the coords in the nodal dataframe returning the fuzzy match from metrics
    node_df['m_coords'] = node_df['coords'].apply(lambda coord: next((x for x in fuzzy_match(coord)), []))
    
    # cast the coordinates back to tuples (hashable) 
    node_df['m_coords'] = node_df['m_coords'].apply(tuple)
    metrics['m_coords'] = metrics['m_coords'].apply(tuple)
    
    # now that we have identical metric coords in both node_df and metrics join on that column
    metrics = pd.merge(metrics, node_df, on='m_coords', left_index=True).sort()
    
    # drop the m_coords from both frames
    metrics.drop(labels=['m_coords'], axis=1, inplace=True)
    node_df.drop(labels=['m_coords'], axis=1, inplace=True)
  
    # anything in node_df that failed to find a fuzzy_match is a 'Fake' node
    fake_nodes = node_df.ix[node_df.index - metrics.index]
    
    # tack the fake nodes on to the metrics (all values are NULL, except coord)
    metrics = pd.concat([metrics, fake_nodes]).sort()
    
    # finally assume Network edges are bi-directional
    network = network.to_undirected().to_directed()
    
    return network, metrics
        
