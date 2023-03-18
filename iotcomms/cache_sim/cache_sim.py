import sys
sys.path.insert(0, '../app_gen')

from app_gen import Node , APP
from collections import OrderedDict
import string
import random
import numpy as np
import graphviz
import json


class LRUCache:
 
    # initialising capacity
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
 
    #function to make a reference to to the Topic Hash
    #if not found, return -1
    #else return the node
    def get(self, key , topic):
        
        if key not in self.cache:
            #print("miss")
            return [0 , None]
        elif self.cache[key].topic != topic:
            #print("conf")
            return [1 , None]
        else:
            #print("hit")
            self.cache.move_to_end(key)
            return [2 , self.cache[key]]
    
    def put(self, key: int, value: Node) -> None:
         
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last = False)
 
    def put_quad(self, key: int, value: Node) -> None:
        if key not in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        elif self.cache[key].topic != topic:
            #print("conf")
            return [1 , None]

class CacheController:
    def __init__(self, dev_cache_capacity, area_cache_capacity):
        self.miss_dict = ["cache miss" , "cache miss conflict"]
        self.dev_cache_capacity = dev_cache_capacity
        self.area_cache_capacity = area_cache_capacity
        self.dev_cache = LRUCache(dev_cache_capacity)
        self.area_cache = LRUCache(area_cache_capacity)
        self.stats = {}
        self.conflicts = {}
        self.stats["dev"] = []
        self.stats["dev"].append({"cache miss":0 , "cache miss conflict":0})
        
        self.stats["area"] = []
        for depth in range(6):
            self.stats["area"].append({"cache miss":0 , "cache miss conflict":0})
            self.stats["area"][depth]["cache miss"] = 0
            self.stats["area"][depth]["cache miss conflict"] = 0
    
    def stats_update(self, stats_name, cache_type, index):
        
        self.stats[cache_type][index][stats_name] = self.stats[cache_type][index][stats_name] + 1
        
    def FE2HASH(self , topic):
        areas = topic.split('/')
        areas.pop()
        areas.pop(0)
        #Check dev chache for topic
        topic_key = hash(topic) % self.dev_cache_capacity 
        node = self.dev_cache.get(topic_key , topic)
        #topic missed
        if node[0] < 2:
            self.stats_update(self.miss_dict[node[0]] , "dev" , 0)
            if node[0] == 1:
                if topic_key in self.conflicts.keys():
                    self.conflicts[topic_key].append(topic)
                else:
                    self.conflicts[topic_key] = []
                    self.conflicts[topic_key].append(topic)
            node = Node("" , topic)
            self.dev_cache.put(topic_key , node)
        #check area cache for areas
        for depth , area in enumerate(areas):
            key = hash(area) % self.area_cache_capacity
            node = self.area_cache.get(key , area)
            
            if node[0] < 2:
                print("key " , key, "topic " , area , " depth " , depth)
                
                self.stats_update(self.miss_dict[node[0]] , "area" , depth)
                node = Node("" , area)
                self.area_cache.put(key , node)

    def print_stats(self):
        for cache , value in self.stats.items():
            for stat_type in value:
                print(cache , stat_type)


def print_tree(node , dot):
    if len(node.children) == 0:
        return
    dot.node(node.topic , node.topic)
    for child in node.children:
        dot.node(child.topic , child.topic)
        
        dot.edge(node.topic , child.topic)
        print_tree(child , dot)

cache_controller = CacheController(2017 , 1000) 

f = open("../app_gen/config.json")
config = json.load(f)
print(config["hierarchy"])
a1 = config["hierarchy"]["dist"][0]
a2 = config["hierarchy"]["dist"][1]
a3 = config["hierarchy"]["dist"][2]
#a4 = config["hierarchy"]["dist"][3]

app = APP([a1 , a2 , a3, np.random.poisson(lam=100 , size=(a3*a2*10)).tolist()] , config["topic_size"])


dot = graphviz.Digraph(comment='Normal')
dot.graph_attr['rankdir'] = 'LR'

if config["display_graph"]:
    print_tree(app.root, dot)
    dot.render('test-output/gen_tree.gv', view=True) 


topic_indexes = []

for i in range(len(app.devices) -1):
    topic_indexes.append(i)


"""
for i in range(10):
    random.shuffle(topic_indexes)
    for dev_index in topic_indexes:
        topic = app.compose_topic(app.devices[dev_index])
        cache_controller.FE2HASH(topic)
"""

for i in range(100000):
    rand = random.randint(0 , 99)
    n_dev = len(app.devices) -1
    most_frequent = int(0.1*n_dev)
    if rand < 90:
        index = random.randint(0 , most_frequent)
    else:
        index = random.randint(most_frequent +1 , n_dev -1)
    
    #print("index is " , index)
    topic = app.compose_topic(app.devices[index])
    cache_controller.FE2HASH(topic)

cache_controller.print_stats()

print("Number of devices " , len(app.devices))

#for i , conf in cache_controller.conflicts.items():
#    print(len(conf))
