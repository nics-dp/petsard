from .SDV_SingleTable import SDV_SingleTable
from sdv.single_table import TVAESynthesizer
import pandas as pd


class SDV_SingleTable_TVAE(SDV_SingleTable):
    """
    Implement TVAE synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.

    Return:
        None
    """
    def __init__(self, data: pd.DataFrame, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method: str = 'TVAE'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = TVAESynthesizer(self.metadata)
