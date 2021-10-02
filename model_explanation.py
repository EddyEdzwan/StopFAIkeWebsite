import numpy as np
import shap

# Create Custom SHAP Object inhereting from Explanation class (of a typical shap value) in order for plot to work
class CustomSHAPObject(shap._explanation.Explanation):
    def __init__(self, values, base_values, data, output_names):
        super().__init__(values)
        self.values = np.array(values)
        self.base_values = base_values
        self.data = np.array(data)
        self.output_names = output_names