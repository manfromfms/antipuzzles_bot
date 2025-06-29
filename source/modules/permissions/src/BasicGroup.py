from __future__ import annotations


class BasicGroup:
    def __init__(self, name='', pgroup=1000) -> None:
        self.name = name
        self.pgroup = pgroup

        self.rules = {}


    def __gt__(self, other: BasicGroup):
        return self.pgroup > other.pgroup
    

    def __lt__(self, other: BasicGroup):
        return self.pgroup < other.pgroup
    

    def addRule(self, name: str, state: bool):
        self.rules[name] = state


    def hasPermission(self, name: str):
        if self.pgroup <= 0:
            # ROOT has all the rules without a need to check.
            return True
        
        return self.rules[name]
    
    
    @staticmethod
    def get(pgroup: int):
        if pgroup <= 0:
            return ROOT
        
        if pgroup <= 10:
            return SUPERADMIN
        
        if pgroup <= 100:
            return ADMIN
        
        if pgroup <= 1000:
            return DEFAULT
        
        if pgroup <= 10000:
            return RESTRICTED
        
        if pgroup <= 100000:
            return BANNED
        

ROOT =       BasicGroup(name='root',       pgroup=0)
SUPERADMIN = BasicGroup(name='superadmin', pgroup=10)
ADMIN =      BasicGroup(name='admin',      pgroup=100)
DEFAULT =    BasicGroup(name='default',    pgroup=1000)
RESTRICTED = BasicGroup(name='restricted', pgroup=10000)
BANNED =     BasicGroup(name='banned',     pgroup=100000)
