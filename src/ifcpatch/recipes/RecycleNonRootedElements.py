from collections import deque
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        deleted = []
        hashes = {}
        for element in self.file:
            if element.is_a("IfcRoot"):
                continue
            h = hash(tuple(element))
            if h in hashes:
                for inverse in self.file.get_inverse(element):
                    ifcopenshell.util.element.replace_attribute(inverse, element, hashes[h])
                deleted.append(element.id())
            else:
                hashes[h] = element
        deleted.sort()
        deleted_q = deque(deleted)
        new = ""
        for line in self.file.wrapped_data.to_string().split("\n"):
            try:
                if int(line.split("=")[0][1:]) != deleted_q[0]:
                    new += line + "\n"
                else:
                    deleted_q.popleft()
            except:
                new += line + "\n"
        self.file = new
