import numpy as np
import math 

class ParametricModel:
    valid=False
    def __init__(self, time: np.array, values: np.array):
        """Fit the model to the data"""
        pass
    def calcValue(self, time: np.array) -> np.array:
        """Evaluate the model at the specified time points"""
        pass
    def calcMeanSquaredError(self,time: np.array, values: np.array) -> float:
        """Evaluate the mean squared error of the model"""
        if self.valid:
            nanItems=np.isnan(values)
            if len(values[nanItems]) > 0:
                timeUpd=time[~nanItems]
                valuesUpd=values[~nanItems]          
                modelValues = self.calcValue(timeUpd)
                return np.mean( (modelValues-valuesUpd)**2 )
            else:
                return math.nan
        else:
            return math.nan
    def getEquationLabel(self, scale:float) -> str:
        """Return the equation of the model as a string"""
        pass

class ConstantModel(ParametricModel):
    """y(x)=a"""
    a = 0.
    def __init__(self, time: np.array, values: np.array):
        if len(values) > 0:
            nanItems=np.isnan(values)
            if len(values[~nanItems]) > 0:
                self.valid=True
                self.a = np.nanmean(values)
    def calcValue(self, time: np.array):
        if self.valid:
            return np.ones(np.shape(time))*self.a        
        else:
            return np.ones(np.shape(time))*math.nan
    def getEquationLabel(self,scale:float):
        if self.valid:
            return '$y={:.2f}$'.format(self.a*scale)
        else:
            return 'empty-constant-model'

class LinearModel(ParametricModel):
    """y(x) = b*(x-x_0)+a"""
    a = 0.
    b = 0.
    x0 = 0.
    def __init__(self, time: np.array, values: np.array):
        if len(values) > 0:
            nanItems=np.isnan(values)
            if len(values[~nanItems]) > 0:
                self.x0=time[0]
                nanItems=np.isnan(values)
                timeUpd=time[~nanItems]
                valuesUpd=values[~nanItems]        
                A = np.vstack([(timeUpd-timeUpd[0]),np.ones(len(timeUpd))]).T
                self.b,self.a = np.linalg.lstsq(A,valuesUpd,rcond=None)[0]
                self.valid=True
    def calcValue(self,time: np.array):
        if self.valid:
            return self.b*(time-self.x0) + self.a
        else:
            return np.ones(np.shape(time))*math.nan
    def getEquationLabel(self, scale:float):
        if self.valid:
            return '$y = {:.2e}(x-x_0) + {:.2e} [{:.2f}]$'.format(self.b,self.a,self.b*scale)
        else:
            return 'empty-linear-model'

class ExponentialModel(ParametricModel):
    """y(x) = b*pow(c,(x-x_0))+a"""
    a = 0
    b = 0
    c = 0
    x0 = 0    
    def __init__(self,time,values):
        if len(time) > 0 and len(values) > 0:
            nanItems=np.isnan(values)
            if len(values[~nanItems]) > 0:            
                timeUpd=time[~nanItems]
                valuesUpd=values[~nanItems]
                nonzeroItems= np.count_nonzero(valuesUpd)

                self.x0=timeUpd[0]        
                A = np.vstack([(timeUpd-timeUpd[0], np.ones(len(timeUpd)))]).T  
                #We need at least two data points to fit 
                if len(valuesUpd) >= 2 and nonzeroItems > 2:
                    if(min(valuesUpd)<=0.0):
                        self.a= abs(min(valuesUpd)) \
                                +2*abs(max(valuesUpd)-min(valuesUpd))         
                    if self.a <= 0.0:
                        self.a=1.0
                    log10m,log10c=\
                        np.linalg.lstsq(A,np.log10(valuesUpd+self.a),rcond=None)[0]
                    self.c = np.power(10.,log10m)
                    self.b = np.power(10.,log10c)
                    self.valid=True
    def calcValue(self, time: np.array):
        if self.valid:
            return self.b*np.power(self.c,time-self.x0)-self.a
        else:
            return np.ones(np.shape(time))*math.nan
    def getEquationLabel(self, scale:float):
        if self.valid:
            if self.a > 0:
                return '$y = {:.2e}({:.2e})'.format(self.b,self.c)\
                        +'^{(x-x_0)} - '+' {:.2e} [{:.2f}\%]$'.format(\
                            self.a,(self.c-1)*scale)
            else:
                return '$y = {:.2e}({:.2e})'.format(self.b,self.c)\
                        +'^{(x-x_0)},'+' [{:.2f}\%]$'.format((self.c-1)*scale)
        else:
            return 'empty-exponential-model'
