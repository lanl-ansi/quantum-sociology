class Network(object):
    def __init__(self):
        self.maxNode = 0
        self.j = {}
    def friend(self, n1, n2):
        self.maxNode = max(self.maxNode, n1, n2)
        self.j[(n1,n2)] = 1
    def enemy(self, n1, n2):
        self.maxNode = max(self.maxNode, n1, n2)
        self.j[(n1,n2)] = -1
