class Node:
    @property
    def MASTER(self):
        return 'master'

    @property
    def BOOTSTRAP(self):
        return 'bootstrap'

    @property
    def WORKER(self):
        return 'worker'

    @property
    def INFRA(self):
        return 'infra'
