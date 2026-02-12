from gpio_oscillator import sqrwvave_oscillator
from gpiozero import LED
import jack
import mido
import time

midi_on = False
midi_note = 0
midi_pitch_bend = 1 #combines with note to determine frequency
midi_velocity = 0 # determines duty cycle 0-127 to 0.0-1.0
cc_phase = 0 #determines phase offset of oscillator from 0-127 to miliseconds
cc_quantized = 0 # if >64, quantize to transport bpm
cc_sync = 0 # if >64, sync to transport beat

bpm = 0 # beats per minute from transport is used to sync oscillator frequency when quantized
led = LED(5)

oscillator = sqrwvave_oscillator(frequency=2, duty_cycle=0.5)

def print_midi_messages(msg):
    global oscillator
    global midi_on, midi_note, midi_velocity, midi_pitch_bend
    global cc_phase, cc_quantized, cc_sync
    # print("Note received: ", msg)
    if msg.type == 'note_on':
        if not midi_on:
            midi_on = True
            oscillator.reset()
            oscillator.start()

        if midi_note != msg.note:
            print("Note changed: ", msg)
            midi_note = msg.note
            oscillator.set_frequency(oscillator.bpm/60*midi_note/midi_pitch_bend)

        # if midi_velocity != msg.velocity:
        #     print("Velocity changed: ", msg)
        #     midi_velocity = msg.velocity
        #     oscillator.set_duty_cycle(midi_velocity/127)

    if msg.type == 'note_off':
        # print("Note Off received: ", msg)
        midi_on = False
        oscillator.stop()
    if msg.type == 'pitchwheel':
        if midi_pitch_bend != msg.pitch:
            print("Pitch Bend changed: ", msg)
            midi_pitch_bend = msg.pitch + 1
            oscillator.set_frequency(oscillator.bpm*midi_note/midi_pitch_bend)
    
    if msg.type == 'control_change':
        if msg.control == 1: #phase
            if cc_phase != msg.value:
                print("Phase changed: ", msg)
                cc_phase = msg.value
                oscillator.set_phase(cc_phase/127*oscillator.cycle)
            
        if msg.control == 2: #quantization
            if not msg.value:
                print("Transport Stoped")
                midi_on = False
                oscillator.stop()
            else:                
                print("Transport Started")
        if msg.control == 3: #cc_sync
            cc_sync = msg.value
    # recieved_value = True
    
    # print(msg)
def main():
    print("GPIO Oscillator started")
    inport = mido.open_input('totem_in', virtual=True)
    # outport = mido.open_output('totem_out', virtual=True)
    inport.callback = print_midi_messages

    client = jack.Client("GPIO_Oscillator_1")
    
    client.deactivate()
    client.activate()
    transport_init = client.transport_query()
    bpm = transport_init[1]['beats_per_minute']
    oscillator.set_bpm(bpm)

    # print(transport_init)
    
    
    
    prev_transport = transport_init

    try:
        while True:
            #TRANSPORT PROCESSING
            tranport = client.transport_query()
            # print(tranport)
            if tranport[1]['usecs'] != prev_transport[1]['usecs']:
                prev_transport = tranport
                if tranport[1]['beats_per_minute'] != bpm:
                    bpm = tranport[1]['beats_per_minute']
                    oscillator.set_bpm(bpm)
                    print("BPM updated: ", bpm)

            # print(client.transport_state.__getstate__()[1]['_code'])
                # if cc_sync > 64:
                #     if tranport[1]['beat'] != prev_transport[1]['beat']: # wont work is oscillation is slower that 1 beat
                #         oscillator.reset()
            
            #OSCILLATOR processing
            output = oscillator.update()
            if output:
                led.on()
            else:
                led.off()
    except KeyboardInterrupt:
        client.deactivate()
        print("Exiting...")
        inport.close()

if __name__ == "__main__":  
    main()