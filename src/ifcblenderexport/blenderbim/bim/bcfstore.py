import bcf
import bcf.bcfxml

class BcfStore:
    bcfxml = None

    @staticmethod
    def get_bcfxml():
        if not BcfStore.bcfxml:
            BcfStore.bcfxml = bcf.bcfxml.BcfXml()
        return BcfStore.bcfxml
