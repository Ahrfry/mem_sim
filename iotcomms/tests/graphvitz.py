import graphviz

dot = graphviz.Digraph(comment='The Round Table')
dot.node('A', 'King Arthur')
dot.node('B', 'Sir Bedevere the Wise')
dot.node('L', 'Sir Lancelot the Brave')

dot.edge('A', 'L')
dot.edge('A', 'B')

dot.render('test-output/round-table.gv', view=True)