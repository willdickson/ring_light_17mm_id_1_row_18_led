from __future__ import print_function
import os
import sys
import pcbnew
import numpy as np
import pprint


def inch_to_nanometer(value):
    return (value*25.4)*1e6

def nanometer_to_inch(value):
    return value/(25.4*1.e6)


def get_led_data(num,cx,cy,radius,length,ref_offset,prefix):
    led_refs = ['{}{}'.format(prefix,i+1) for i in range(num)]
    led_pos_data = {}
    led_ref_data = {}
    for i, ref in enumerate(led_refs):
        angle = i*(360.0/num)
        x = radius*np.cos(np.deg2rad(-angle)) + cx
        y = radius*np.sin(np.deg2rad(-angle)) + cy
        led_pos_data[ref] = {'angle': angle, 'x': x, 'y': y}

        x = (radius + 0.2*length)*np.cos(np.deg2rad(-angle - ref_offset)) + cx
        y = (radius + 0.2*length)*np.sin(np.deg2rad(-angle - ref_offset)) + cy
        led_ref_data[ref] = {'angle': angle, 'x': x, 'y': y}

    return led_pos_data, led_ref_data


def print_module_info(module):
    ref = module.GetReference()
    pos = module.GetPosition()
    x = nanometer_to_inch(pos.x)
    y = nanometer_to_inch(pos.y)
    angle = 0.1*module.GetOrientation()
        
    print('  R: {}'.format(ref))
    print('  X: {}'.format(x))
    print('  Y: {}'.format(y))
    print('  A: {}'.format(angle))
    print()


# ---------------------------------------------------------------------------------------


number_of_led = 18 
led_center_x = 2.0
led_center_y = 2.0 
led_radius = 0.5*22/25.4 
led_length = 0.186
ref_offset = 8.5
led_ref_prefix = 'D'


filename = sys.argv[1]


print()
print('loading pcb: {}'.format(filename))
print()
pcb = pcbnew.LoadBoard(filename)
print()
print('done')
print()

# Get data for placing LEDs
led_pos_data_dict, led_ref_data_dict = get_led_data(
        number_of_led, 
        led_center_x, 
        led_center_y, 
        led_radius, 
        led_length, 
        ref_offset,
        led_ref_prefix
        )

print('led_data')
print()
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(led_pos_data_dict)
print()

print('modules')
print()
for module in pcb.GetModules():

    ref_str = str(module.GetReference())

    try:
        led_pos_data = led_pos_data_dict[ref_str]
        led_ref_data = led_ref_data_dict[ref_str]
    except KeyError:
        continue

    print_module_info(module)

    # Move to new position
    pos = module.GetPosition()
    angle = 0.1*module.GetOrientation()
    x_new = led_pos_data['x']
    y_new = led_pos_data['y']
    angle_new = led_pos_data['angle']
    pos.x = int(inch_to_nanometer(x_new))
    pos.y = int(inch_to_nanometer(y_new))
    module.SetPosition(pos)
    module.SetOrientation(10.0*angle_new)

    # Make value invisible
    value_obj = module.Value()
    value_obj.SetVisible(False)

    # Move reference designators
    ref_obj = module.Reference()
    ref_pos = ref_obj.GetPosition()
    ref_pos.x = int(inch_to_nanometer(led_ref_data['x']))
    ref_pos.y = int(inch_to_nanometer(led_ref_data['y']))
    ref_obj.SetPosition(ref_pos)


    print_module_info(module)



pathname, basename = os.path.split(filename)
new_basename = 'mod_{}'.format(basename)
new_filename = os.path.join(pathname,new_basename)

pcb.Save(new_filename)

        

