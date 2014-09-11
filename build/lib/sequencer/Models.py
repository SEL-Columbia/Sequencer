from sequencer import Sequencer

class EnergyMaximizeReturn(Sequencer):
    """This class sequences a proposed electrification plan, optimizing for maximum Demand (kwh) / Distance (m)"""
    
    def nodal_demand(self, df):
        return df['Demand...Projected.nodal.demand.per.year']
    
    def _strip_cols(self):
      del (self.output_frame['nodal_demand'])

    def sequence(self):
        super(EnergyMaximizeReturn, self).sequence()
        self._strip_cols()