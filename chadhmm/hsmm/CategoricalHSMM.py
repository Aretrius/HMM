from typing import Optional
import torch

from .BaseHSMM import BaseHSMM # type: ignore
from ..emissions import CategoricalEmissions # type: ignore


class CategoricalHSMM(BaseHSMM, CategoricalEmissions):
    """
    Categorical Hidden semi-Markov Model (HSMM)
    ----------
    Hidden semi-Markov model with categorical (discrete) emissions. This model is an extension of classical HMMs where the duration of each state is modeled by a geometric distribution.
    Duration in each state is modeled by a Categorical distribution with a fixed maximum duration.

    Parameters:
    ----------
    n_states (int):
        Number of hidden states in the model.
    n_emissions (int): 
        Number of emissions in the model.
    seed (int):
        Random seed for reproducibility.
    params_init (bool):
        Whether to initialize the model parameters prior to fitting.
    init_dist (SAMPLING_DISTRIBUTIONS):
        Distribution to use for initializing the model parameters.
    alpha (float):
        Dirichlet concentration parameter for the prior over initial state probabilities and transition probabilities.
    verbose (bool):
        Whether to print progress logs during fitting.
    """
    def __init__(self,
                 n_states:int,
                 n_emissions:int,
                 max_duration:int,
                 alpha:float = 1.0,
                 seed:Optional[int] = None, 
                 device:Optional[torch.device] = None):
        
        BaseHSMM.__init__(self,n_states,max_duration,alpha,seed,device)
        
        CategoricalEmissions.__init__(self,n_states,n_emissions,alpha,device)

    @property
    def params(self):
        """Returns the parameters of the model."""
        return {
            'pi': self.initial_vector.logits,
            'A': self.transition_matrix.logits,
            'D': self.duration_matrix.logits,
            'B': self.emission_matrix.logits
        }

    @property    
    def n_fit_params(self):
        """Return the number of trainable model parameters."""
        return {
            'states': self.n_states,
            'transitions': self.n_states**2,
            'durations': self.n_states * self.max_duration,
            'emissions': self.n_states * self.n_features
        }
    
    @property
    def dof(self):
        """Returns the degrees of freedom of the model."""
        return self.n_states ** 2 + self.n_states * self.n_features - 1
    
    def check_sequence(self,X):
        return CategoricalEmissions.check_constraints(self,X)
        
    def map_emission(self,x):
        return CategoricalEmissions.map_emission(self,x)

    def sample_B_params(self,X,seed=None):
        self._emission_matrix = CategoricalEmissions.sample_emission_params(self,X,seed)

    def update_B_params(self,X,log_gamma,theta):
        gamma = [torch.exp(gamma) for gamma in log_gamma]
        CategoricalEmissions.update_emission_params(self,X,gamma,theta)

