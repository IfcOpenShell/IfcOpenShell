import bcf
import bcf.v2.bcfxml

class BcfStore:
    bcfxml = None

    @staticmethod
    def get_bcfxml():
        if not BcfStore.bcfxml:
            BcfStore.bcfxml = bcf.v2.bcfxml.BcfXml()
        return BcfStore.bcfxml
