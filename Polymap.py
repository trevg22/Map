

class cellPatch:

    def __init__(self, inc_polygonPatch,inc_poly):
        self.polygonPatch = inc_polygonPatch
        self.cell = None
        self.alpha = None
        self.polygon=inc_poly

    def set_alpha(self, inc_alpha):
        self.polygonPatch.set_alpha(inc_alpha)

    def set_data(self, inc_dataObj):
        self.data = inc_dataObj

    def set_cell(self,cell_num):
        self.cell=cell_num
    
    def get_cell(self):
        return self.cell
    
    def get_data(self):
        return self.data