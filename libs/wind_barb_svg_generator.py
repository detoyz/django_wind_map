__author__ = 'Ciuv'
"""
This functions provides generation of svg-path for wind barb icons.
At input it takes knots value, and at output give us "path" for svg icon.
Icons can be generated for values from 0 to 150 knots, with step 5 knots.
If knots value is more than 150, will be generated icon for 150 knots value.
"""

barb_items = {
    'base_stick': 'M 0,0 h -40',
    'half_stick': 'l -2.5,-8.5',
    'full_stick': 'l -5,-17',
    'first_triangle': 'M -40,0 L -44,0 L -40,-13.75 L -36,0 L -42,0 L -40,-11.25 L -38,0 L -41,0 L -40,-9 L -39,0',
    'second_triangle': 'M -30,0 L -34,0 L -30,-13.75 L -26,0 L -32,0 L -30,-11.25 L -28,0 L -31,0 L -30,-9 L -29,0',
    'third_triangle': 'M -20,0 L -24,0 L -20,-13.75 L -16,0 L -22,0 L -20,-11.25 L -18,0 L -21,0 L -20,-9 L -19,0'
}


def wind_barb_svg_generator(knots):
    knots_round = str(int(round(knots/5)*5))

    if len(knots_round) == 1 or len(knots_round) == 0:
        path = barb_items['base_stick']+'M -35,0 '+barb_items['half_stick']

    elif len(knots_round) == 2:
        first_number = int(knots_round[0])
        second_number = int(knots_round[1])
        path = barb_items['base_stick']
        if first_number < 5:
            for i in range(first_number):
                path += 'M -'+str(45-(i+1)*5)+',0 '+barb_items['full_stick']
            if second_number == 5:
                path += 'M -'+str(40-first_number*5)+',0 '+barb_items['half_stick']
        else:
            path += barb_items['first_triangle']
            for i in range(first_number-5):
                path += 'M -'+str(35-(i+1)*5)+',0 '+barb_items['full_stick']
            if second_number == 5:
                path += 'M -'+str(35-(first_number-4)*5)+',0 '+barb_items['half_stick']

    else:
        first_number = int(knots_round[0])
        second_number = int(knots_round[1])
        path = barb_items['base_stick']+barb_items['first_triangle']+barb_items['second_triangle']
        if first_number < 5:
            for i in range(first_number):
                path += 'M -'+str(25-(i+1)*5)+',0 '+barb_items['full_stick']
            if second_number == 5:
                path += 'M -'+str(20-first_number*5)+',0 '+barb_items['half_stick']
        else:
            path += barb_items['third_triangle']

    return path


