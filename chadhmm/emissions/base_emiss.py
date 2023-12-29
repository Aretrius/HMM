import torch
from abc import abstractmethod, abstractproperty, ABC
from typing import Optional, List
from ..utils import ContextualVariables


class BaseEmission(ABC):

    def __init__(self,
                 n_dims: int,
                 n_features: int,
                 device:Optional[torch.device] = None):

        self.n_dims = n_dims
        self.n_features = n_features
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if device is None else device
        
    def __str__(self):
        return f'{self.__class__.__name__}(n_dims={self.n_dims}, n_features={self.n_features})'

    def check_constraints(self,value:torch.Tensor) -> torch.Tensor:
        not_supported = value[torch.logical_not(self.pdf.support.check(value))].unique()
        events = self.pdf.event_shape
        event_dims = len(events)
        assert len(not_supported) == 0, ValueError(f'Values outside PDF support, got values: {not_supported.tolist()}')
        assert value.ndim == event_dims+1, ValueError(f'Expected number of dims differs from PDF constraints on event shape {events}')
        if event_dims > 0:
            assert value.shape[1:] == events, ValueError(f'PDF event shape differs, expected {events} but got {value.shape[1:]}')
        
        return value

    @abstractproperty
    def pdf(self):
        pass

    @abstractmethod
    def map_emission(self, x:torch.Tensor) -> torch.Tensor:
        """Convert emissions into log probabilities."""
        pass

    @abstractmethod
    def sample_emission_params(self, X:Optional[torch.Tensor]=None):
        """Sample emission parameters."""
        pass

    @abstractmethod
    def update_emission_params(self, X:List[torch.Tensor], posterior:List[torch.Tensor], theta:Optional[ContextualVariables]=None):
        """Update emission parameters in the model."""
        pass