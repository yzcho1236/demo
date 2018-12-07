

#from 111 import ClassX



# class ClassA(ClassX):
class ClassX(object):
    def __init__(self, p):
        self.p = p


class ClassA(ClassX):
    def __init__(self, p):
        super(ClassA, self).__init__(p)

class ClassB(object):
    def ff(self):
        return 1

# Create your tests here.
if __name__ == '__main__':
    b = ClassB()