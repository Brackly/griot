import pandas as pd

class Data:
    def __init__(self,
                 path:str,
                 dataset_type:str = "pandas"
                 ):
        self.path = path
        self.dataset_type = dataset_type

    def _pandas_df(self):
        return pd.read_csv(self.path)

    def _torch_data(self):
        raise NotImplementedError("Pytorch datasets have not been implemented yet")

    def __call__(self, *args, **kwargs):
        if self.dataset_type == "pandas":
            return self._pandas_df()
