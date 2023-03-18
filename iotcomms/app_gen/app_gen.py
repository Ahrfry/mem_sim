import string
import random
import numpy as np

class Device:
    def __init__(self, transport, name, period, parent):
        self.transport = transport
        self.name = name
        self.period = period
        self.parent = parent

class Node:
    def __init__(self, data , topic, hash_key, parent):
        self.data = data
        self.topic = topic
        self.hash_key = hash_key
        self.parent = None
        self.children = []
        self.valid = False
        self.max_state = 4
        self.access_count = 2
        self.epoch = 0
        self.epoch_color = "white"
        self.parent = parent
        self.depth = None

class APP():
    
    def __init__(self, app_distro , topic_size):
        
        self.app = []
        self.letters = string.ascii_lowercase
        self.app_distro = app_distro
        self.n_topics = 0
        self.devices = []
        self.topic_size = topic_size
        self.root = self.build_tree(app_distro)
        
        
    
    def build_tree(self, L):
        root = Node("r","r", None ,None)
        Q = [root]
        depth = len(L)
        while len(L) > 0:
            degs = L.pop(0)
            
            print("depth ", len(L))    
            for d in degs:
                
                node = Q.pop(0)
                node.depth = (depth - len(L))
                node.children = [Node("",''.join(random.choice(string.ascii_lowercase) for i in range(self.topic_size)), None ,node) for _ in range(d)]
                
                if len(L) == 0:
                    for n in node.children:
                        self.devices.append(n)    
                Q += node.children

        return root
            
            
        
    def print_tree(self , node):
        
        for i in range(len(node.children) -1):
            self.print_tree(node.children[i])
            self.n_topics = self.n_topics + 1
    
    def compose_topic(self, dev):
        node = dev
        node.access_count = node.access_count + 1
        topic = dev.topic
        node = dev.parent
        #print("node depth ", node.depth)
        while node:
            node.access_count = node.access_count + 1
            topic = node.topic + "/" + topic
            node = node.parent
        return topic
    
    
    def helper(self , node, level , levels):
            # start the current level
            if len(levels) == level:
                levels.append([])

            # append the current node value
            levels[level].append(node.access_count)

            # process child nodes for the next level
            for i in range(len(node.children)):

                self.helper(node.children[i], level + 1 , levels)

    def order_lvl_print(self):
        """
        :type root: TreeNode
        :rtype: List[List[int]]
        """
        levels = []
        stats = []
        
        if not self.root:
            return levels
        
        self.helper(self.root, 0 , levels)
        
        for item in (levels):
            sum = np.sum(item)
            avg = np.average(item)
            std_d = np.std(item)
            stats.append([avg , std_d])
        return stats

def print_tree(node , dot):
    if len(node.children) == 0:
        return
    dot.node(node.topic , node.topic)
    for child in node.children:
        dot.node(child.topic , child.topic)
        
        dot.edge(node.topic , child.topic)
        print_tree(child , dot)

