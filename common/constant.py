from enum import Enum


class Node(Enum):
    MASTER = 'master'
    BOOTSTRAP = 'bootstrap'
    WORKER = 'worker'
