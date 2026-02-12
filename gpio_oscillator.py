# import numpy as np
import time
class sqrwvave_oscillator:
    def __init__(self, frequency=440, duty_cycle=0.5):
        self.duty_cycle = duty_cycle
        self.phase = 0. # 0.0 to 1/frequency
        self.latched = False
        self.bpm = 120 # default bpm for quantization

        if frequency == 0:
            self.cycle = 0
            self.latched = True
        else:
            self.cycle = 1./frequency
            
        self.time = time.monotonic()
        self.prev_time = self.time
        self.delta_time = 0.
        self.in_sync = False
        self.running = False
        
    def set_bpm(self, bpm):
        self.bpm = bpm
    def reset(self):
        self.time = time.monotonic()
        self.prev_time = self.time
        self.delta_time = 0.
    def start(self):
        self.running = True
    def stop(self):
        self.running = False
    def set_phase(self, phase):
        self.phase = phase  # from milliseconds to nanoseconds

    def set_frequency(self, frequency):
        if frequency == 0:
            self.cycle = 0
            self.latched = True
        else:
            self.latched = False
            self.cycle = 1/frequency
            print("Cycle length set to: ", self.cycle, frequency)
            self.reset()
        

    def set_duty_cycle(self, duty_cycle):
        if 0 <= duty_cycle <= 1:
            self.duty_cycle = duty_cycle
        else:
            raise ValueError("Duty cycle must be between 0 and 1")

    def update(self):
        self.time = time.monotonic()
        #***********************************************************
        if self.running:
            if self.latched:
                output = True
            else:
                if(self.delta_time < self.cycle*self.duty_cycle):
                    output = True
                else:
                    output = False
        else:
            output = False
        #***********************************************************
        self.delta_time += (self.time - self.prev_time) - self.phase
        if self.delta_time >= self.cycle:
            self.delta_time -= self.cycle

        elif self.delta_time < 0:
            self.delta_time += self.cycle

        self.prev_time = self.time
        return output