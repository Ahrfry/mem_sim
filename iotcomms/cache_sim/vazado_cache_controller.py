import sys
sys.path.insert(0, '../app_gen')

from app_gen import Node , APP
from collections import OrderedDict
from lru_cache import Cache
import random
import numpy as np
import graphviz
import json

def get_prime(start):
    
    end = start + 100
    
    for i in range(start, end+1):
        if i>1:
            for j in range(2,i):
                if(i % j==0):
                    break
            else:
                return i

class HashNode:
 
    # initialising capacity
    def __init__(self ,  topic):
        self.valid = False
        self.topic = topic
        self.access_count = 2
        self.max_state = 4
        self.epoch = 0
        self.epoch_color = "white"
        self.depth = None


class CacheController:
    def __init__(self, dev_cache_capacity, area_cache_capacity, dev_cache_type, area_cache_type, hash_multiplier):
        self.miss_dict = ["cache miss" , "cache miss conflict"]
        self.controller_type = dev_cache_type
        self.dev_cache_capacity = dev_cache_capacity
        self.area_cache_capacity = area_cache_capacity
        self.hash_multiplier = hash_multiplier
        self.ram_hash_multiplier = 100
        self.window_size = 1000
        self.window_count = 0
        self.epoch_size = 2^31
        self.epoch = 0
        self.color = 0
        self.probe = 5
        self.caches = {}
        self.caches["dev"] = Cache(dev_cache_capacity , dev_cache_type , "dev") 
        self.caches["area"] = Cache(area_cache_capacity , area_cache_type , "area")
        self.hash = {}
        self.hash["dev"] = {}
        self.hash["area"] = {}
        self.hash["ram"] = {}
        self.hash_capacity = {}
        self.hash_capacity["dev"] = get_prime(int(dev_cache_capacity*self.hash_multiplier))
        self.hash_capacity["area"] = get_prime(int(area_cache_capacity*self.hash_multiplier))
        print("CACHE CAPACITY " , self.hash_capacity["area"], area_cache_capacity, self.hash_multiplier)
        self.hash_capacity["ram"] = get_prime(int(area_cache_capacity*self.ram_hash_multiplier))
        print("Dev hash Size ", self.hash_capacity["dev"], " Area hash Size ", self.hash_capacity["area"], " RAM Hash Size ", self.hash_capacity["ram"])
        self.stats = {}
        self.conflicts = {}
        self.stats["dev"] = []
        self.stats["dev"].append({"cache miss":0 , "cache miss conflict":0})
        self.stats["area"] = []
        self.bytes_missed = 0
        
        for i in range(self.hash_capacity["dev"]):
            self.hash["dev"][i] = HashNode("")

        for i in range(self.hash_capacity["area"]):
            self.hash["area"][i] = HashNode("")
        
        

        for depth in range(6):
            self.stats["area"].append({"cache miss":0 , "cache miss conflict":0})
            self.stats["area"][depth]["cache miss"] = 0
            self.stats["area"][depth]["cache miss conflict"] = 0
    
    def update_window(self):
        self.window_count = self.window_count + 1
        if self.window_count > self.window_size:
            self.window_size = 0
            self.epoch = self.epoch + 1
            if self.epoch > self.epoch_size:
                self.epoch = 0
                if self.color == 0:
                    self.color = 1
                else:
                    self.color = 0        

    def get(self, key , topic , hash_type):
        topicz = topic
        if self.controller_type != "LRUQUAD" and self.controller_type != "LRUQUADD":
            #print("HASH GET" ,  hash_type , " topic ", topic, " key " , key, " controller type ", self.controller_type)
            if self.hash[hash_type][key].valid == False:
                #print("hash miss " , hash_type)
                return [0 , key]
            elif self.hash[hash_type][key].topic != topic:
                #print("hash conf " , hash_type)
                return [1 , key]
            else:
                #print("HASH GET HIT, " ,  hash_type , " topic ", topicz, " key " , key)
                if self.caches[hash_type].get(topicz):
                    #print("Cache Hit " , hash_type , " topic ", topic)
                    return [2 , key]
                else:
                    #print("Hash Hit Cache Miss" , hash_type , " topic ", topic)
                    return [0 , key]
        else:
            
            max_probbed = key
            if self.hash[hash_type][key].valid == False:
                #print("hash miss 1 invalid" , key)
                return [0, key]
            else:
                  
                key2 = (key % (self.hash_capacity[hash_type] - 2))
                for i in range(self.probe):
                    #print("START PROBBING")  
                    if self.hash[hash_type][key2].valid == False:
                        #print("hash miss 2 invalid")
                        return [0 , key2]
                    elif self.hash[hash_type][key2].topic != topic:
                        key2 = (key + i*key2) % self.hash_capacity[hash_type]   
                        
                        if self.controller_type == "LRUQUADD":
                            #print("k2 depth ", self.hash[hash_type][key2].depth, "max probbed depth" , self.hash[hash_type][max_probbed].depth)
                            if self.hash[hash_type][key2].depth is None:
                                max_probbed = key2

                            elif self.hash[hash_type][key2].depth and self.hash[hash_type][max_probbed].depth:
                                if self.hash[hash_type][key2].depth >= self.hash[hash_type][max_probbed].depth:
                                    max_probbed = key2
                        else:
                            max_probbed = key2    
                                    
                    elif self.hash[hash_type][key2].topic == topic:
                        self.hash[hash_type][key2].probe_count = 0
                        
                        if self.caches[hash_type].get(topic):
                            #print("Hash HIT Cache HIT")
                            return [2 , key2]
                        else:
                            #print("Hash HIT Cache MISS")
                            return [0 , key2]    
                #print("Probe Miss key " , max_probbed)    
                return [1 , max_probbed]

    def stats_update(self, stats_name, cache_type, index, cost):
        if cache_type == "area":
            self.stats[cache_type][index][stats_name] = self.stats[cache_type][index][stats_name] + 1
        #print("Byte cost ", cache_type, cost)
        self.bytes_missed+= cost
        
    
    
    
    
    def FE2HASH(self , topic, depth_cost):
        
        self.update_window()
        areas = topic.split('/')
        #print("Before ", areas)
        areas.pop()
        areas.pop(0)
        #print("After ", areas)
        #Check dev chache for topic
        topic_key = hash(topic) % self.hash_capacity["area"]
        
        
        
        
        if  self.controller_type != "FLAT":
            #check area cache for areas
            for depth , topic in enumerate(areas):
                topic_key = hash(topic) % self.hash_capacity["area"] 
                
                get_return = self.get(topic_key , topic , "area")
                                
                if get_return[0] < 2:
                   
                    self.stats_update(self.miss_dict[get_return[0]] , "area" , depth, depth_cost[depth])
                    rnode = Node("" , topic , get_return[1], None)
                    rnode.valid = True
                    hash_node = HashNode(topic)
                    hash_node.valid = True
                    hash_node.depth = depth
                    self.hash["area"][get_return[1]] = hash_node
                    put_ret = self.caches["area"].put(topic , rnode)
                    #print("Calling get again " , topic_key, "topic " , topic , " depth " , depth,"cost", depth_cost[depth] ," valid ", self.hash["area"][get_return[1]].valid)
                    #n_ret = self.get(topic_key , topic , "area")
                   
                   
                    if put_ret:
                        
                        if put_ret.valid:
                            self.hash["area"][put_ret.hash_key].valid = False
            self.stats_update(self.miss_dict[0] , "dev" , depth, depth_cost[len(depth_cost)-1])
        else:
            get_return = self.get(topic_key , topic , "area")
                                
            if get_return[0] < 2:
                
                self.stats_update(self.miss_dict[get_return[0]] , "area" , 0, sum(depth_cost))
                rnode = Node("" , topic , get_return[1], None)
                rnode.valid = True
                hash_node = HashNode(topic)
                hash_node.valid = True
                
                self.hash["area"][get_return[1]] = hash_node
                put_ret = self.caches["area"].put(topic , rnode)
                #print("Calling get again " , topic_key, "topic " , topic , " depth " , depth, " valid ", self.hash["area"][get_return[1]].valid)
                #n_ret = self.get(topic_key , topic , "area")
                
                
                if put_ret:
                    
                    if put_ret.valid:
                        self.hash["area"][put_ret.hash_key].valid = False
                    
        
    def print_stats(self, n_messages):
        for cache , value in self.stats.items():
            
            for stat_type in value:
               
                print((stat_type["cache miss"] + stat_type["cache miss conflict"])/n_messages)
        print("Total bytes missed ", (self.bytes_missed/1000000))

class VazadoCacheController:
    def __init__(self, dev_cache_capacity, area_cache_capacity, dev_cache_type, area_cache_type, hash_multiplier):
        self.miss_dict = ["cache miss" , "cache miss conflict"]
        self.controller_type = dev_cache_type
        self.dev_cache_capacity = dev_cache_capacity
        self.area_cache_capacity = area_cache_capacity
        self.hash_multiplier = hash_multiplier
        self.ram_hash_multiplier = 100
        self.window_size = 6000
        self.window_count = 0
        self.damping_size = 5
        self.epoch_size = 10000
        self.epoch = 0
        self.epoch_color = "white"
        self.probe = 10
        self.caches = {}
        self.caches["dev"] = Cache(dev_cache_capacity , dev_cache_type , "dev") 
        self.caches["area"] = Cache(area_cache_capacity , area_cache_type , "area")
        self.hash = {}
        self.hash["dev"] = {}
        self.hash["area"] = {}
        self.hash["ram"] = {}
        self.hash_capacity = {}
        self.hash_capacity["dev"] = get_prime(int(dev_cache_capacity*self.hash_multiplier))
        self.hash_capacity["area"] = get_prime(int(area_cache_capacity*self.hash_multiplier))
        self.hash_capacity["ram"] = get_prime(int(area_cache_capacity*self.ram_hash_multiplier))
        print("Dev hash Size ", self.hash_capacity["dev"], " Area hash Size ", self.hash_capacity["area"], " RAM Hash Size ", self.hash_capacity["ram"])
        self.stats = {}
        self.conflicts = {}
        self.stats["dev"] = []
        self.stats["dev"].append({"cache miss":0 , "cache miss conflict":0})
        self.stats["area"] = []
        
        for i in range(self.hash_capacity["dev"]):
            self.hash["dev"][i] = HashNode("")

        for i in range(self.hash_capacity["area"]):
            self.hash["area"][i] = HashNode("")
        
        

        for depth in range(6):
            self.stats["area"].append({"cache miss":0 , "cache miss conflict":0})
            self.stats["area"][depth]["cache miss"] = 0
            self.stats["area"][depth]["cache miss conflict"] = 0
    
    def update_window(self):
        self.window_count = self.window_count + 1
        #print("updating window " , self.window_count , " epoch ", self.epoch, " color ", self.epoch_color)
        if self.window_count > self.window_size:
            #print("updating window " , self.window_count , " epoch ", self.epoch, " color ", self.epoch_color)
            self.window_count = 0
            self.epoch = self.epoch + 1
            if self.epoch > self.epoch_size:
                self.epoch = 0
                if self.epoch_color == "white":
                    self.epoch_color = "black"
                else:
                    self.epoch_color = "white"    
    
    def update_state(self , node: Node , update):
        if node.epoch != self.epoch or node.epoch_color != self.epoch_color:
            #print("wrong epoch or color")
            node.epoch = self.epoch
            node.access_count = 1
            return node.access_count
        
        
        node.access_count += update
        #print("Epoch " ,  self.epoch , " window " , self.window_count, " access count ", node.access_count , " dev epoch ", node.epoch)
        if node.access_count > self.damping_size:
            node.access_count = self.damping_size
        elif node.access_count < 0:
            node.access_count = 0
        
        return node.access_count

    def get(self, key , topic , hash_type):
               
        max_probbed = key
        invalid = -1
        
        #print("START PROBBING")    
        key2 = key
        
        for i in range(self.probe):
            #print("Probing again " , self.hash[hash_type][key2].topic , " key2 ", key2)
                            
            if self.hash[hash_type][key2].topic != topic:
                    
                if self.hash[hash_type][key2].valid == True:
                    
                    #print("Hash Type " , hash_type, " topic " , self.hash[hash_type][key2].topic , " valid " , self.hash[hash_type][key2].valid , " key " , key2)
                    
                    
                    #print("GET PROBING key " , key, " key2 " , key2 , " prob count ", self.hash[hash_type][key2].access_count, " key " , key2)
                    if self.hash[hash_type][max_probbed].access_count < self.caches[hash_type].cache[self.hash[hash_type][key2].topic].access_count:
                        max_probbed = key2
                else:
                    invalid = key2      
            elif self.hash[hash_type][key2].topic == topic:
                self.hash[hash_type][key2].access_count = self.update_state(self.hash[hash_type][key2], 1)                    
                if self.caches[hash_type].get(topic):
                    
                    #print("Hash HIT Cache HIT")
                    return [2 , key2]
                else:
                    #print("Hash HIT Cache MISS")
                    return [0 , key2]
            if i == 0:
                
                key2 = (key % (self.hash_capacity[hash_type] - 2))
            else:        
                key2 = (key + i*key2) % self.hash_capacity[hash_type]  

        #print("MAXXXXXXXX PRROOBEEE Miss key " , max_probbed , self.hash[hash_type][key2].topic)    
        if invalid > -1:
            max_probbed = invalid
            miss = 0
        else:
            self.hash[hash_type][key2].access_count = self.update_state(self.hash[hash_type][key2], -1) 
            miss = 1
        return [miss , max_probbed]

    def stats_update(self, stats_name, cache_type, index):
        
        self.stats[cache_type][index][stats_name] = self.stats[cache_type][index][stats_name] + 1
        
    
    
    
    
    def FE2HASH(self , topic):
        
        self.update_window()
        
        areas = topic.split('/')
        areas.pop()
        areas.pop(0)
        #Check dev chache for topic
        topic_key = hash(topic) % self.hash_capacity["dev"]
        
        get_return = self.get(topic_key , topic , "dev")
        if topic not in self.hash["ram"]:
            #print("not found in ram")
            self.hash["ram"][topic] = Node("" , topic , topic, None)
        
        
            
            #topic missed
        if get_return[0] < 2:
            self.stats_update(self.miss_dict[get_return[0]] , "dev" , 0)
            if get_return[0] == 1:
                if topic_key in self.conflicts.keys():
                    self.conflicts[topic_key].append(topic)
                else:
                    self.conflicts[topic_key] = []
                    self.conflicts[topic_key].append(topic)

            #self.update_state(self.hash["ram"][topic] , 1)
            self.hash["ram"][topic].access_count = self.update_state(self.hash["ram"][topic], 1)
            ram_node = self.hash["ram"][topic]
            
            if ram_node.access_count >= 2:
                ram_node.hash_key = get_return[1]
                
                
                #print("Returned Value " , get_return)
                if get_return[0] == 1:
                    #print("Delting from cache " , self.hash["dev"][get_return[1]].topic , " valid ", self.hash["dev"][get_return[1]].valid, " key " , get_return[1])                
                    if self.hash["dev"][get_return[1]].topic in self.caches["dev"].cache:
                        self.caches["dev"].cache[self.hash["dev"][get_return[1]].topic].access_count = self.hash["dev"][get_return[1]].access_count
                        self.caches["dev"].cache[self.hash["dev"][get_return[1]].topic].epoch = self.hash["dev"][get_return[1]].epoch
                        self.caches["dev"].cache[self.hash["dev"][get_return[1]].topic].epoch_color = self.hash["dev"][get_return[1]].epoch_color
                        self.hash["ram"][self.hash["dev"][get_return[1]].topic] = self.caches["dev"].cache[self.hash["dev"][get_return[1]].topic]
                        del self.caches["dev"].cache[self.hash["dev"][get_return[1]].topic]
                ram_node.valid = True
                hash_node = HashNode(topic)
                hash_node.valid = True
                hash_node.access_count = ram_node.access_count
                hash_node.epoch = ram_node.epoch
                hash_node.epoch_color = ram_node.epoch_color
                self.hash["dev"][get_return[1]] = hash_node
                

                #print("Putting in cache " , ram_node.topic , " hash key " , ram_node.hash_key)        
                put_ret = self.caches["dev"].put(topic , ram_node)
                if put_ret != None:
                    if put_ret.hash_key != None:
                        self.hash["ram"][put_ret.topic] = put_ret
                        if put_ret.valid:
                            #print("Invalidating ", put_ret.hash_key , " topic " , put_ret.topic)
                            self.hash["dev"][put_ret.hash_key].valid = False
                            
        
        
    def print_stats(self):
        for cache , value in self.stats.items():
            for stat_type in value:
                print(cache , stat_type)







