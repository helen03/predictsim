# encoding: utf-8
import numpy as np

class WeightedSquaredLoss(object):
    def __init__(self,model):
        """Instanciate a weighted squared loss for a specific model"""
        self.model=model

    def loss(self,x,y,w):
        """Return the squared loss of the model on example (x,y) with weight p"""
        p=self.model.predict(x)
        return 0.5*(p-y)*(p-y)*p*w

    def d_loss_directional(self,x,y,i,w):
        """Return the derivative of the loss with respect to the i-th entry of the parameter vector of the model"""
        return self.model.d_predict_directional(x, i)*(self.model.predict(x)-y)*w

    def grad_loss(self,x,y,w):
        """
        Gradient of the loss of the model on example (x,y)
        Should be np.array(map(lambda i:d_loss_directional(model, x, i),range(0,len(x))).
        In the case where this can be optimized, it will be different.
        """
        return (self.model.predict(x)-y)*np.array(map(lambda i:self.model.d_predict_directional(x, i),range(0,self.model.dim)))*w