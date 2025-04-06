from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import math
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pile-estimate')
def pile_estimate():
    return render_template('pile_estimate.html')

@app.route('/calculate-pile', methods=['POST'])
def calculate_pile():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract values from the request
        pile_data = {
            'nos': [float(x) if x and x != 'null' else 0 for x in data.get('A', [0]*5)],
            'pile_dia': [float(x) if x and x != 'null' else 0 for x in data.get('B', [0]*5)],
            'total_height': [float(x) if x and x != 'null' else 0 for x in data.get('C', [0]*5)],
            'cut_off_level': [float(x) if x and x != 'null' else 0 for x in data.get('D', [0]*5)],
            'cc': [float(x) if x and x != 'null' else 0 for x in data.get('E', [0]*5)],
            'clear_cover': [float(x) if x and x != 'null' else 0 for x in data.get('F', [0]*5)],
        }
        
        ratio_data = {
            'aa': float(data.get('aa', 0) or 0),
            'bb': float(data.get('bb', 0) or 0),
            'cc': float(data.get('cc', 0) or 0)
        }
        
        rebar_data = {
            'large_dia': [float(x) if x and x != 'null' else 0 for x in data.get('G', [0]*5)],
            'large_dia_nos': [float(x) if x and x != 'null' else 0 for x in data.get('H', [0]*5)],
            'large_dia_lapping': [float(x) if x and x != 'null' else 0 for x in data.get('I', [0]*5)],
            'small_dia': [float(x) if x and x != 'null' else 0 for x in data.get('J', [0]*5)],
            'small_dia_nos': [float(x) if x and x != 'null' else 0 for x in data.get('K', [0]*5)],
            'small_dia_lapping': [float(x) if x and x != 'null' else 0 for x in data.get('L', [0]*5)],
            'spiral_rod_dia': [float(x) if x and x != 'null' else 0 for x in data.get('M', [0]*5)],
            'spacing': [float(x) if x and x != 'null' else 0 for x in data.get('N', [0]*5)],
            'spiral_rod_lapping': [float(x) if x and x != 'null' else 0 for x in data.get('O', [0]*5)]
        }

        # Get rates and wastage with better error handling
        rates_and_wastage = {
            'cement_rate': float(data.get('cement_rate', 0) or 0),
            'sand_rate': float(data.get('sand_rate', 0) or 0),
            'stone_rate': float(data.get('stone_rate', 0) or 0),
            'rebar_rate': float(data.get('rebar_rate', 0) or 0),
            'cement_wastage': float(data.get('cement_wastage', 0) or 0),
            'sand_wastage': float(data.get('sand_wastage', 0) or 0),
            'stone_wastage': float(data.get('stone_wastage', 0) or 0),
            'rebar_wastage': float(data.get('rebar_wastage', 0) or 0)
        }
        
        # Calculate results
        results = calculate_pile_estimates(pile_data, ratio_data, rebar_data, rates_and_wastage)
        print("Debug - Final results:", results)  # Debug line
        return jsonify(results)
    except Exception as e:
        print("Error:", str(e))  # Debug line
        return jsonify({'error': str(e)}), 500

def calculate_pile_estimates(pile_data, ratio_data, rebar_data, rates_and_wastage):
    total_rcc_casting = 0
    total_cement = 0
    total_sand = 0
    total_stone = 0
    total_rebar = 0

    # Calculate for each pile set (1 to 5)
    for i in range(5):
        a = pile_data['nos'][i]
        if a > 0:  # Only calculate if number of piles > 0
            b = pile_data['pile_dia'][i]  # Pile diameter in inches
            c = pile_data['total_height'][i]  # Total height in ft
            d = pile_data['cut_off_level'][i]  # Cut off level in ft
            e = pile_data['cc'][i]  # C.C in ft
            f = pile_data['clear_cover'][i]  # Clear cover in inches
            g = rebar_data['large_dia'][i]  # Large dia in mm
            h = rebar_data['large_dia_nos'][i]  # Large dia nos
            i_val = rebar_data['large_dia_lapping'][i]  # Large dia lapping in ft
            j = rebar_data['small_dia'][i]  # Small dia in mm
            k = rebar_data['small_dia_nos'][i]  # Small dia nos
            l = rebar_data['small_dia_lapping'][i]  # Small dia lapping in ft
            m = rebar_data['spiral_rod_dia'][i]  # Spiral rod dia in mm
            n = rebar_data['spacing'][i]  # Spacing in inches
            o = rebar_data['spiral_rod_lapping'][i]  # Spiral rod lapping in ft

            # Calculate Main Dia Length (P)
            p = (c - e) + i_val if a > 0 else 0

            # Calculate Small Dia Lap Length (Q)
            q = (c - e) + l if a > 0 else 0

            # Calculate One Spiral Rod Length (R)
            r = (math.pi * (b - f - f)) / 12 if a > 0 else 0

            # Calculate Total Spiral Rod Length (S)
            s = 0
            if a > 0 and n > 0:
                s = (r * ((c - l - d - e) / (n/12) + 1)) + o

            # Calculate Reinforcement Main Dia Rod (T1)
            t1 = ((g**2) / 532) * h * p * a if a > 0 else 0

            # Calculate Reinforcement Small Dia Rod (T2)
            t2 = 0
            if a > 0 and j > 0:
                t2 = ((j**2) / 532) * k * q * a

            # Calculate Reinforcement Spiral (T3)
            t3 = 0
            if a > 0 and n > 0:
                t3 = ((m**2) / 532) * s * a

            # Calculate RCC Casting (U)
            u = 0
            if a > 0:
                u = ((math.pi * ((b/12)**2) / 4) * c) * a

            # Calculate total ratio
            abc = ratio_data['aa'] + ratio_data['bb'] + ratio_data['cc']
            
            if abc > 0:
                # Calculate Cement (V)
                if a > 0:
                    cement = (u * ratio_data['aa'] * 1.5) / (abc * 1.25)
                    total_cement += cement

                # Calculate Sand (W)
                if a > 0:
                    sand = (u * ratio_data['bb'] * 1.5) / abc
                    total_sand += sand

                # Calculate Stone Chips (X)
                if a > 0:
                    stone = (u * ratio_data['cc'] * 1.5) / abc
                    total_stone += stone

            # Add to total RCC casting
            total_rcc_casting += u

            # Add to total rebar (convert to tons)
            total_rebar += (t1 + t2 + t3) / 1000  # Converting kg to tons

    # Apply wastage
    cement_with_wastage = total_cement * (1 + rates_and_wastage['cement_wastage'] / 100)
    sand_with_wastage = total_sand * (1 + rates_and_wastage['sand_wastage'] / 100)
    stone_with_wastage = total_stone * (1 + rates_and_wastage['stone_wastage'] / 100)
    rebar_with_wastage = total_rebar * (1 + rates_and_wastage['rebar_wastage'] / 100)

    # Calculate costs for each material
    cement_cost = cement_with_wastage * rates_and_wastage['cement_rate']
    sand_cost = sand_with_wastage * rates_and_wastage['sand_rate']
    stone_cost = stone_with_wastage * rates_and_wastage['stone_rate']
    rebar_cost = (rebar_with_wastage / 1000) * rates_and_wastage['rebar_rate']  # Convert to tons only for cost calculation
    
    # Calculate total cost
    total_cost = cement_cost + sand_cost + stone_cost + rebar_cost

    # Ensure we have valid numbers
    results = {
        'cement_bags': round(cement_with_wastage, 2) if cement_with_wastage else 0,
        'cement_cost': round(cement_cost, 2) if cement_cost else 0,
        'sand_cft': round(sand_with_wastage, 2) if sand_with_wastage else 0,
        'sand_cost': round(sand_cost, 2) if sand_cost else 0,
        'stone_chips_cft': round(stone_with_wastage, 2) if stone_with_wastage else 0,
        'stone_cost': round(stone_cost, 2) if stone_cost else 0,
        'rebar_kg': round(rebar_with_wastage, 3) if rebar_with_wastage else 0,
        'rebar_cost': round(rebar_cost, 2) if rebar_cost else 0,
        'total_rcc_casting': round(total_rcc_casting, 2) if total_rcc_casting else 0,
        'total_amount': round(total_cost, 2) if total_cost else 0
    }

    return results

@app.route('/long-tied-column')
def long_tied_column():
    return render_template('long_tied_column.html')

@app.route('/calculate-long-tied-column', methods=['POST'])
def calculate_long_tied_column():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract values from the request
        column_data = {
            'nos': [float(x) if x and x != 'null' else 0 for x in data.get('column_nos', [0]*15)],
            'length': [float(x) if x and x != 'null' else 0 for x in data.get('length', [0]*15)],
            'breadth': [float(x) if x and x != 'null' else 0 for x in data.get('breadth', [0]*15)],
            'clear_cover': [float(x) if x and x != 'null' else 0 for x in data.get('clear_cover', [0]*15)],
            'height': [float(x) if x and x != 'null' else 0 for x in data.get('height', [0]*15)]
        }
        
        rcc_ratio = {
            'input1': float(data.get('ratio_input1', 0) or 0),
            'input2': float(data.get('ratio_input2', 0) or 0),
            'input3': float(data.get('ratio_input3', 0) or 0)
        }
        
        rebar_data = {
            'large_dia': [float(x) if x and x != 'null' else 0 for x in data.get('large_dia', [0]*15)],
            'large_dia_nos': [float(x) if x and x != 'null' else 0 for x in data.get('large_dia_nos', [0]*15)],
            'large_dia_lapping': [float(x) if x and x != 'null' else 0 for x in data.get('large_dia_lapping', [0]*15)],
            'small_dia': [float(x) if x and x != 'null' else 0 for x in data.get('small_dia', [0]*15)],
            'small_dia_nos': [float(x) if x and x != 'null' else 0 for x in data.get('small_dia_nos', [0]*15)],
            'small_dia_lapping': [float(x) if x and x != 'null' else 0 for x in data.get('small_dia_lapping', [0]*15)],
            'tie_rod_dia': [float(x) if x and x != 'null' else 0 for x in data.get('tie_rod_dia', [0]*15)],
            'spacing1': [float(x) if x and x != 'null' else 0 for x in data.get('spacing1', [0]*15)],
            'spacing2': [float(x) if x and x != 'null' else 0 for x in data.get('spacing2', [0]*15)],
            'hook_length': [float(x) if x and x != 'null' else 0 for x in data.get('hook_length', [0]*15)],
            'extra_tie1_length': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie1_length', [0]*15)],
            'extra_tie1_spacing': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie1_spacing', [0]*15)],
            'extra_tie2_length': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie2_length', [0]*15)],
            'extra_tie2_spacing': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie2_spacing', [0]*15)]
        }

        rates_and_wastage = {
            'cement_rate': float(data.get('cement_rate', 550.0)),
            'sand_rate': float(data.get('sand_rate', 45.0)),
            'stone_rate': float(data.get('stone_rate', 45.0)),
            'rebar_rate': float(data.get('rebar_rate', 95000.0)),
            'formwork_rate': float(data.get('formwork_rate', 30.0)),
            'casting_rate': float(data.get('casting_rate', 0)),
            'wastage_percent': float(data.get('wastage_percent', 10.0))
        }

        # Calculate results
        results = calculate_long_tied_column_estimates(column_data, rcc_ratio, rebar_data, rates_and_wastage)
        return jsonify(results)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

def calculate_long_tied_column_estimates(column_data, rcc_ratio, rebar_data, rates_and_wastage):
    total_rcc_casting = 0
    total_cement = 0
    total_sand = 0
    total_stone = 0
    total_rebar = 0
    total_formwork = 0
    
    # Dictionary to store rebar quantities by size
    rebar_by_size = {
        8: 0, 10: 0, 12: 0, 16: 0, 20: 0, 25: 0, 28: 0, 32: 0
    }

    # Calculate for each column type (1 to 15)
    for i in range(15):
        if column_data['nos'][i] > 0:
            # Calculate RCC volume
            length = column_data['length'][i] / 12  # Convert inches to feet
            breadth = column_data['breadth'][i] / 12  # Convert inches to feet
            height = column_data['height'][i]
            volume = length * breadth * height * column_data['nos'][i]
            total_rcc_casting += volume

            # Calculate formwork area
            formwork = ((length + breadth) * 2 * height) * column_data['nos'][i]
            total_formwork += formwork

            # Calculate rebar weights
            if rebar_data['large_dia'][i] > 0:
                weight = ((rebar_data['large_dia'][i]**2) / 532) * rebar_data['large_dia_nos'][i] * \
                        (height + rebar_data['large_dia_lapping'][i]) * column_data['nos'][i]
                total_rebar += weight
                rebar_by_size[int(rebar_data['large_dia'][i])] += weight

            if rebar_data['small_dia'][i] > 0:
                weight = ((rebar_data['small_dia'][i]**2) / 532) * rebar_data['small_dia_nos'][i] * \
                        (height + rebar_data['small_dia_lapping'][i]) * column_data['nos'][i]
                total_rebar += weight
                rebar_by_size[int(rebar_data['small_dia'][i])] += weight

            # Calculate tie rod weight
            if rebar_data['tie_rod_dia'][i] > 0:
                perimeter = 2 * ((length + breadth) - 4 * column_data['clear_cover'][i]/12)
                avg_spacing = (rebar_data['spacing1'][i] + rebar_data['spacing2'][i]) / 2
                num_ties = (height * 12 / avg_spacing) + 1 if avg_spacing > 0 else 0
                tie_length = perimeter + 2 * rebar_data['hook_length'][i]/12
                weight = ((rebar_data['tie_rod_dia'][i]**2) / 532) * num_ties * tie_length * column_data['nos'][i]
                total_rebar += weight
                rebar_by_size[int(rebar_data['tie_rod_dia'][i])] += weight

    # Calculate material quantities based on ratio
    total_ratio = rcc_ratio['input1'] + rcc_ratio['input2'] + rcc_ratio['input3']
    if total_ratio > 0:
        total_cement = (total_rcc_casting * rcc_ratio['input1'] * 1.54) / (total_ratio * 1.25)
        total_sand = (total_rcc_casting * rcc_ratio['input2'] * 1.54) / total_ratio
        total_stone = (total_rcc_casting * rcc_ratio['input3'] * 1.54) / total_ratio

    # Apply wastage
    wastage_multiplier = 1 + rates_and_wastage['wastage_percent'] / 100
    cement_with_wastage = total_cement * wastage_multiplier
    sand_with_wastage = total_sand * wastage_multiplier
    stone_with_wastage = total_stone * wastage_multiplier
    rebar_with_wastage = total_rebar * wastage_multiplier  # Keep in kg, don't convert to tons

    # Calculate costs
    cement_cost = cement_with_wastage * rates_and_wastage['cement_rate']
    sand_cost = sand_with_wastage * rates_and_wastage['sand_rate']
    stone_cost = stone_with_wastage * rates_and_wastage['stone_rate']
    rebar_cost = (rebar_with_wastage / 1000) * rates_and_wastage['rebar_rate']  # Convert to tons only for cost calculation
    formwork_cost = total_formwork * rates_and_wastage['formwork_rate']
    casting_cost = total_rcc_casting * rates_and_wastage['casting_rate']

    # Calculate total cost
    total_cost = cement_cost + sand_cost + stone_cost + rebar_cost + formwork_cost + casting_cost

    # Prepare rebar breakdown
    rebar_breakdown = {
        f'{size}_mm': round(weight, 3) if weight > 0 else 0  # Keep in kg, don't convert to tons
        for size, weight in rebar_by_size.items()
    }

    results = {
        'cement_bags': round(cement_with_wastage, 2),
        'sand_cft': round(sand_with_wastage, 2),
        'stone_chips_cft': round(stone_with_wastage, 2),
        'rebar_kg': round(rebar_with_wastage, 3),  # Changed from rebar_ton to rebar_kg
        'formwork_sft': round(total_formwork, 2),
        'casting_cft': round(total_rcc_casting, 2),
        'cement_cost': round(cement_cost, 2),
        'sand_cost': round(sand_cost, 2),
        'stone_cost': round(stone_cost, 2),
        'rebar_cost': round(rebar_cost, 2),
        'formwork_cost': round(formwork_cost, 2),
        'casting_cost': round(casting_cost, 2),
        'total_amount': round(total_cost, 2),
        'rebar_breakdown': rebar_breakdown
    }

    return results

@app.route('/slab-estimate')
def slab_estimate():
    return render_template('slab_estimate.html')

@app.route('/calculate-slab', methods=['POST'])
def calculate_slab():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract values from the request
        slab_data = {
            'nos': [float(x) if x and x != 'null' else 0 for x in data.get('nos', [0]*5)],
            'long_direction_length': [float(x) if x and x != 'null' else 0 for x in data.get('long_direction_length', [0]*5)],
            'short_direction_length': [float(x) if x and x != 'null' else 0 for x in data.get('short_direction_length', [0]*5)],
            'slab_thickness': [float(x) if x and x != 'null' else 0 for x in data.get('slab_thickness', [0]*5)],
            'clear_cover': [float(x) if x and x != 'null' else 0 for x in data.get('clear_cover', [0]*5)]
        }
        
        ratio_data = {
            'type1': float(data.get('ratio_type1', 0) or 0),
            'type2': float(data.get('ratio_type2', 0) or 0),
            'type3': float(data.get('ratio_type3', 0) or 0)
        }
        
        rebar_data = {
            'long_direction': {
                'large_dia': [float(x) if x and x != 'null' else 0 for x in data.get('long_large_dia', [0]*5)],
                'spacing': [float(x) if x and x != 'null' else 0 for x in data.get('long_spacing', [0]*5)],
                'lapping': [float(x) if x and x != 'null' else 0 for x in data.get('long_lapping', [0]*5)]
            },
            'short_direction': {
                'large_dia': [float(x) if x and x != 'null' else 0 for x in data.get('short_large_dia', [0]*5)],
                'spacing': [float(x) if x and x != 'null' else 0 for x in data.get('short_spacing', [0]*5)],
                'lapping': [float(x) if x and x != 'null' else 0 for x in data.get('short_lapping', [0]*5)]
            },
            'long_extra_top': {
                'rebar_dia': [float(x) if x and x != 'null' else 0 for x in data.get('long_extra_dia', [0]*5)],
                'nos': [float(x) if x and x != 'null' else 0 for x in data.get('long_extra_nos', [0]*5)],
                'length': [float(x) if x and x != 'null' else 0 for x in data.get('long_extra_length', [0]*5)]
            },
            'short_extra_top': {
                'rebar_dia': [float(x) if x and x != 'null' else 0 for x in data.get('short_extra_dia', [0]*5)],
                'nos': [float(x) if x and x != 'null' else 0 for x in data.get('short_extra_nos', [0]*5)],
                'length': [float(x) if x and x != 'null' else 0 for x in data.get('short_extra_length', [0]*5)]
            }
        }

        rates_and_wastage = {
            'cement_rate': float(data.get('cement_rate', 0) or 0),
            'sand_rate': float(data.get('sand_rate', 0) or 0),
            'stone_rate': float(data.get('stone_rate', 0) or 0),
            'rebar_rate': float(data.get('rebar_rate', 0) or 0),
            'formwork_rate': float(data.get('formwork_rate', 0) or 0),
            'casting_rate': float(data.get('casting_rate', 0) or 0),
            'wastage_percent': float(data.get('wastage_percent', 0) or 0)
        }

        # Calculate results
        results = calculate_slab_estimates(slab_data, ratio_data, rebar_data, rates_and_wastage)
        return jsonify(results)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

def calculate_slab_estimates(slab_data, ratio_data, rebar_data, rates_and_wastage):
    # Initialize totals
    total_rcc_casting = 0
    total_cement = 0
    total_sand = 0
    total_stone = 0
    total_rebar = 0
    total_formwork = 0
    
    # Dictionary to store rebar quantities by size
    rebar_by_size = {
        8: 0, 10: 0, 12: 0, 16: 0, 20: 0, 25: 0, 28: 0, 32: 0
    }

    # Calculate total ratio
    total_ratio = ratio_data['type1'] + ratio_data['type2'] + ratio_data['type3']

    # Calculate for each slab type (1 to 5)
    for i in range(5):
        if slab_data['nos'][i] > 0:
            # Calculate RCC volume
            length = slab_data['long_direction_length'][i]
            breadth = slab_data['short_direction_length'][i]
            thickness = slab_data['slab_thickness'][i] / 12  # Convert inches to feet
            volume = length * breadth * thickness * slab_data['nos'][i]
            total_rcc_casting += volume

            # Calculate formwork area
            formwork = length * breadth * slab_data['nos'][i]
            total_formwork += formwork

            # Calculate long direction rebar
            if rebar_data['long_direction']['large_dia'][i] > 0:
                spacing = rebar_data['long_direction']['spacing'][i]
                if spacing > 0:
                    num_bars = (breadth / (spacing/12)) + 1
                    rebar_length = length + rebar_data['long_direction']['lapping'][i]
                    weight = ((rebar_data['long_direction']['large_dia'][i]**2) / 532) * num_bars * rebar_length
                    total_rebar += weight
                    rebar_by_size[int(rebar_data['long_direction']['large_dia'][i])] += weight

            # Calculate short direction rebar
            if rebar_data['short_direction']['large_dia'][i] > 0:
                spacing = rebar_data['short_direction']['spacing'][i]
                if spacing > 0:
                    num_bars = (length / (spacing/12)) + 1
                    rebar_length = breadth + rebar_data['short_direction']['lapping'][i]
                    weight = ((rebar_data['short_direction']['large_dia'][i]**2) / 532) * num_bars * rebar_length
                    total_rebar += weight
                    rebar_by_size[int(rebar_data['short_direction']['large_dia'][i])] += weight

            # Calculate long direction extra top rebar
            if rebar_data['long_extra_top']['rebar_dia'][i] > 0:
                weight = ((rebar_data['long_extra_top']['rebar_dia'][i]**2) / 532) * \
                        rebar_data['long_extra_top']['nos'][i] * \
                        rebar_data['long_extra_top']['length'][i]
                total_rebar += weight
                rebar_by_size[int(rebar_data['long_extra_top']['rebar_dia'][i])] += weight

            # Calculate short direction extra top rebar
            if rebar_data['short_extra_top']['rebar_dia'][i] > 0:
                weight = ((rebar_data['short_extra_top']['rebar_dia'][i]**2) / 532) * \
                        rebar_data['short_extra_top']['nos'][i] * \
                        rebar_data['short_extra_top']['length'][i]
                total_rebar += weight
                rebar_by_size[int(rebar_data['short_extra_top']['rebar_dia'][i])] += weight

    # Calculate material quantities based on ratio
    if total_ratio > 0:
        total_cement = (total_rcc_casting * ratio_data['type1'] * 1.54) / (total_ratio * 1.25)
        total_sand = (total_rcc_casting * ratio_data['type2'] * 1.54) / total_ratio
        total_stone = (total_rcc_casting * ratio_data['type3'] * 1.54) / total_ratio

    # Apply wastage
    wastage_multiplier = 1 + rates_and_wastage['wastage_percent'] / 100
    cement_with_wastage = total_cement * wastage_multiplier
    sand_with_wastage = total_sand * wastage_multiplier
    stone_with_wastage = total_stone * wastage_multiplier
    rebar_with_wastage = total_rebar * wastage_multiplier

    # Calculate costs
    cement_cost = cement_with_wastage * rates_and_wastage['cement_rate']
    sand_cost = sand_with_wastage * rates_and_wastage['sand_rate']
    stone_cost = stone_with_wastage * rates_and_wastage['stone_rate']
    rebar_cost = (rebar_with_wastage / 1000) * rates_and_wastage['rebar_rate']  # Convert to tons for cost
    formwork_cost = total_formwork * rates_and_wastage['formwork_rate']
    casting_cost = total_rcc_casting * rates_and_wastage['casting_rate']

    # Calculate total cost
    total_cost = cement_cost + sand_cost + stone_cost + rebar_cost + formwork_cost + casting_cost

    # Prepare rebar breakdown
    rebar_breakdown = {
        f'{size}_mm': round(weight, 3) if weight > 0 else 0
        for size, weight in rebar_by_size.items()
    }

    return {
        'cement_bags': round(cement_with_wastage, 2),
        'sand_cft': round(sand_with_wastage, 2),
        'stone_chips_cft': round(stone_with_wastage, 2),
        'rebar_kg': round(rebar_with_wastage, 3),
        'formwork_sft': round(total_formwork, 2),
        'casting_cft': round(total_rcc_casting, 2),
        'cement_cost': round(cement_cost, 2),
        'sand_cost': round(sand_cost, 2),
        'stone_cost': round(stone_cost, 2),
        'rebar_cost': round(rebar_cost, 2),
        'formwork_cost': round(formwork_cost, 2),
        'casting_cost': round(casting_cost, 2),
        'total_amount': round(total_cost, 2),
        'rebar_breakdown': rebar_breakdown
    }

@app.route('/long-circular-column')
def long_circular_column():
    return render_template('long_circular_column.html')

@app.route('/calculate-long-circular-column', methods=['POST'])
def calculate_long_circular_column():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract values from the request
        column_data = {
            'nos': [float(x) if x and x != 'null' else 0 for x in data.get('column_nos', [0]*15)],
            'dia': [float(x) if x and x != 'null' else 0 for x in data.get('column_dia', [0]*15)],
            'clear_cover': [float(x) if x and x != 'null' else 0 for x in data.get('clear_cover', [0]*15)],
            'height': [float(x) if x and x != 'null' else 0 for x in data.get('height', [0]*15)]
        }
        
        rcc_ratio = {
            'type1': float(data.get('ratio_type1', 0) or 0),
            'type2': float(data.get('ratio_type2', 0) or 0),
            'type3': float(data.get('ratio_type3', 0) or 0)
        }
        
        rebar_data = {
            'large_dia': [float(x) if x and x != 'null' else 0 for x in data.get('large_dia', [0]*15)],
            'large_dia_nos': [float(x) if x and x != 'null' else 0 for x in data.get('large_dia_nos', [0]*15)],
            'large_dia_lapping': [float(x) if x and x != 'null' else 0 for x in data.get('large_dia_lapping', [0]*15)],
            'small_dia': [float(x) if x and x != 'null' else 0 for x in data.get('small_dia', [0]*15)],
            'small_dia_nos': [float(x) if x and x != 'null' else 0 for x in data.get('small_dia_nos', [0]*15)],
            'small_dia_lapping': [float(x) if x and x != 'null' else 0 for x in data.get('small_dia_lapping', [0]*15)],
            'tie_rod_dia': [float(x) if x and x != 'null' else 0 for x in data.get('tie_rod_dia', [0]*15)],
            'spacing1': [float(x) if x and x != 'null' else 0 for x in data.get('spacing1', [0]*15)],
            'spacing2': [float(x) if x and x != 'null' else 0 for x in data.get('spacing2', [0]*15)],
            'hook_length': [float(x) if x and x != 'null' else 0 for x in data.get('hook_length', [0]*15)],
            'extra_tie1_length': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie1_length', [0]*15)],
            'extra_tie1_spacing': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie1_spacing', [0]*15)],
            'extra_tie2_length': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie2_length', [0]*15)],
            'extra_tie2_spacing': [float(x) if x and x != 'null' else 0 for x in data.get('extra_tie2_spacing', [0]*15)]
        }

        rates_and_wastage = {
            'cement_rate': float(data.get('cement_rate', 0) or 0),
            'sand_rate': float(data.get('sand_rate', 0) or 0),
            'stone_rate': float(data.get('stone_rate', 0) or 0),
            'rebar_rate': float(data.get('rebar_rate', 0) or 0),
            'formwork_rate': float(data.get('formwork_rate', 0) or 0),
            'casting_rate': float(data.get('casting_rate', 0) or 0),
            'wastage_percent': float(data.get('wastage_percent', 0) or 0)
        }

        # Calculate results
        results = calculate_long_circular_column_estimates(column_data, rcc_ratio, rebar_data, rates_and_wastage)
        return jsonify(results)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

def calculate_long_circular_column_estimates(column_data, rcc_ratio, rebar_data, rates_and_wastage):
    total_rcc_casting = 0
    total_cement = 0
    total_sand = 0
    total_stone = 0
    total_rebar = 0
    total_formwork = 0
    
    # Calculate total ratio
    total_ratio = rcc_ratio['type1'] + rcc_ratio['type2'] + rcc_ratio['type3']
    
    # Process each column
    for i in range(15):  # For each type (1-15)
        if column_data['nos'][i] > 0:  # Only calculate if number of columns > 0
            # Basic column calculations
            column_height = column_data['height'][i]  # Height in ft
            column_dia = column_data['dia'][i]  # Diameter in mm
            clear_cover = column_data['clear_cover'][i]  # Clear cover in inches
            num_columns = column_data['nos'][i]

            # Calculate RCC volume
            rcc_volume = (math.pi * ((column_dia/12)**2) / 4) * column_height * num_columns
            total_rcc_casting += rcc_volume

            # Calculate formwork area
            formwork_area = math.pi * (column_dia/12) * column_height * num_columns
            total_formwork += formwork_area

            # Calculate rebar quantities
            if rebar_data['large_dia'][i] > 0:
                # Main rebar calculation
                main_rebar_length = column_height + rebar_data['large_dia_lapping'][i]
                main_rebar_weight = ((rebar_data['large_dia'][i]**2) / 532) * rebar_data['large_dia_nos'][i] * main_rebar_length * num_columns
                total_rebar += main_rebar_weight

            if rebar_data['small_dia'][i] > 0:
                # Secondary rebar calculation
                small_rebar_length = column_height + rebar_data['small_dia_lapping'][i]
                small_rebar_weight = ((rebar_data['small_dia'][i]**2) / 532) * rebar_data['small_dia_nos'][i] * small_rebar_length * num_columns
                total_rebar += small_rebar_weight

            if rebar_data['tie_rod_dia'][i] > 0:
                # Tie rod calculations
                tie_perimeter = math.pi * (column_dia - clear_cover - clear_cover + rebar_data['hook_length'][i] + rebar_data['hook_length'][i]) / 12
                avg_spacing = (rebar_data['spacing1'][i] + rebar_data['spacing2'][i]) / 2
                num_ties = (column_height * 12) / avg_spacing if avg_spacing > 0 else 0
                tie_weight = ((rebar_data['tie_rod_dia'][i]**2) / 532) * tie_perimeter * num_ties * num_columns
                total_rebar += tie_weight

                # Extra ties calculations
                if rebar_data['extra_tie1_spacing'][i] > 0:
                    extra_tie1_length = rebar_data['extra_tie1_length'][i]
                    num_extra_ties1 = (column_height * 12) / rebar_data['extra_tie1_spacing'][i]
                    extra_tie1_weight = ((rebar_data['tie_rod_dia'][i]**2) / 532) * extra_tie1_length * num_extra_ties1 * num_columns
                    total_rebar += extra_tie1_weight

                if rebar_data['extra_tie2_spacing'][i] > 0:
                    extra_tie2_length = rebar_data['extra_tie2_length'][i]
                    num_extra_ties2 = (column_height * 12) / rebar_data['extra_tie2_spacing'][i]
                    extra_tie2_weight = ((rebar_data['tie_rod_dia'][i]**2) / 532) * extra_tie2_length * num_extra_ties2 * num_columns
                    total_rebar += extra_tie2_weight

    # Calculate material quantities based on ratio
    if total_ratio > 0:
        total_cement = (total_rcc_casting * rcc_ratio['type1'] * 1.54) / (total_ratio * 1.25)
        total_sand = (total_rcc_casting * rcc_ratio['type2'] * 1.54) / total_ratio
        total_stone = (total_rcc_casting * rcc_ratio['type3'] * 1.54) / total_ratio

    # Apply wastage
    wastage_multiplier = 1 + rates_and_wastage['wastage_percent'] / 100
    cement_with_wastage = total_cement * wastage_multiplier
    sand_with_wastage = total_sand * wastage_multiplier
    stone_with_wastage = total_stone * wastage_multiplier
    rebar_with_wastage = total_rebar * wastage_multiplier
    formwork_with_wastage = total_formwork * wastage_multiplier
    casting_with_wastage = total_rcc_casting * wastage_multiplier

    # Calculate costs
    cement_cost = cement_with_wastage * rates_and_wastage['cement_rate']
    sand_cost = sand_with_wastage * rates_and_wastage['sand_rate']
    stone_cost = stone_with_wastage * rates_and_wastage['stone_rate']
    rebar_cost = (rebar_with_wastage / 1000) * rates_and_wastage['rebar_rate']  # Convert to tons for cost
    formwork_cost = formwork_with_wastage * rates_and_wastage['formwork_rate']
    casting_cost = casting_with_wastage * rates_and_wastage['casting_rate']

    # Calculate total cost
    total_cost = cement_cost + sand_cost + stone_cost + rebar_cost + formwork_cost + casting_cost

    # Prepare results
    results = {
        'cement_bags': round(cement_with_wastage, 2),
        'sand_cft': round(sand_with_wastage, 2),
        'stone_chips_cft': round(stone_with_wastage, 2),
        'rebar_kg': round(rebar_with_wastage, 3),
        'formwork_sft': round(formwork_with_wastage, 2),
        'casting_cft': round(casting_with_wastage, 2),
        'cement_cost': round(cement_cost, 2),
        'sand_cost': round(sand_cost, 2),
        'stone_cost': round(stone_cost, 2),
        'rebar_cost': round(rebar_cost, 2),
        'formwork_cost': round(formwork_cost, 2),
        'casting_cost': round(casting_cost, 2),
        'total_amount': round(total_cost, 2),
        'rebar_breakdown': calculate_reinforcement_details(rebar_data, column_data, rates_and_wastage['wastage_percent'])
    }

    return results

def calculate_reinforcement_details(rebar_data, column_data, wastage_percent):
    # Initialize dictionary to store rebar quantities by size
    rebar_by_size = {
        8: 0,   # 8 MM
        10: 0,  # 10 MM
        12: 0,  # 12 MM
        16: 0,  # 16 MM
        20: 0,  # 20 MM
        25: 0,  # 25 MM
        28: 0,  # 28 MM
        32: 0   # 32 MM
    }

    # Process each column type
    for i in range(15):
        if column_data['nos'][i] > 0:
            # Process large diameter bars
            if rebar_data['large_dia'][i] > 0:
                size = rebar_data['large_dia'][i]
                if size in rebar_by_size:
                    length = column_data['height'][i] + rebar_data['large_dia_lapping'][i]
                    weight = ((size**2) / 532) * rebar_data['large_dia_nos'][i] * length * column_data['nos'][i]
                    rebar_by_size[size] += weight

            # Process small diameter bars
            if rebar_data['small_dia'][i] > 0:
                size = rebar_data['small_dia'][i]
                if size in rebar_by_size:
                    length = column_data['height'][i] + rebar_data['small_dia_lapping'][i]
                    weight = ((size**2) / 532) * rebar_data['small_dia_nos'][i] * length * column_data['nos'][i]
                    rebar_by_size[size] += weight

            # Process tie rods
            if rebar_data['tie_rod_dia'][i] > 0:
                size = rebar_data['tie_rod_dia'][i]
                if size in rebar_by_size:
                    # Main ties
                    tie_length = math.pi * (column_data['dia'][i] - column_data['clear_cover'][i] * 2 + 
                               rebar_data['hook_length'][i] * 2) / 12
                    avg_spacing = (rebar_data['spacing1'][i] + rebar_data['spacing2'][i]) / 2
                    if avg_spacing > 0:
                        num_ties = (column_data['height'][i] * 12) / avg_spacing
                        weight = ((size**2) / 532) * tie_length * num_ties * column_data['nos'][i]
                        rebar_by_size[size] += weight

                    # Extra ties 1
                    if rebar_data['extra_tie1_spacing'][i] > 0:
                        num_extra_ties1 = (column_data['height'][i] * 12) / rebar_data['extra_tie1_spacing'][i]
                        weight = ((size**2) / 532) * rebar_data['extra_tie1_length'][i] * num_extra_ties1 * column_data['nos'][i]
                        rebar_by_size[size] += weight

                    # Extra ties 2
                    if rebar_data['extra_tie2_spacing'][i] > 0:
                        num_extra_ties2 = (column_data['height'][i] * 12) / rebar_data['extra_tie2_spacing'][i]
                        weight = ((size**2) / 532) * rebar_data['extra_tie2_length'][i] * num_extra_ties2 * column_data['nos'][i]
                        rebar_by_size[size] += weight

    # Apply wastage to all rebar quantities
    for size in rebar_by_size:
        if rebar_by_size[size] > 0:
            rebar_by_size[size] = round(rebar_by_size[size] * (1 + wastage_percent / 100), 2)

    return rebar_by_size

@app.route('/short-tied-column')
def short_tied_column():
    return render_template('short-tied-column.html')

@app.route('/calculate-short-tied-column', methods=['POST'])
def calculate_short_tied_column():
    try:
        data = request.get_json()
        
        # Extract column data
        column_data = []
        for i in range(15):  # Support up to 15 columns
            col_key = f'type_{i+1}'
            if col_key in data:
                col = data[col_key]
                if col['column_nos']:  # Only process if column_nos exists
                    column_data.append({
                        'column_nos': float(col['column_nos']),
                        'length': float(col['length']),
                        'breadth': float(col['breadth']),
                        'clear_cover': float(col['clear_cover']),
                        'height': float(col['height']),
                        'large_dia': {
                            'size': float(col['large_dia_size']) if col['large_dia_size'] else 0,
                            'nos': float(col['large_dia_nos']) if col['large_dia_nos'] else 0
                        },
                        'small_dia': {
                            'size': float(col['small_dia_size']) if col['small_dia_size'] else 0,
                            'nos': float(col['small_dia_nos']) if col['small_dia_nos'] else 0
                        },
                        'development_length': float(col['development_length']) if col['development_length'] else 0,
                        'tie_rod': {
                            'size': float(col['tie_rod_size']) if col['tie_rod_size'] else 0,
                            'spacing': float(col['tie_spacing']) if col['tie_spacing'] else 0,
                            'hook_length': float(col['hook_length']) if col['hook_length'] else 0
                        },
                        'extra_tie_1': float(col['extra_tie_1']) if col['extra_tie_1'] else 0,
                        'extra_tie_2': float(col['extra_tie_2']) if col['extra_tie_2'] else 0
                    })

        # Extract RCC casting ratio
        rcc_ratio = {
            'type_1': float(data['rcc_ratio']['type_1']) if data['rcc_ratio']['type_1'] else 0,
            'type_2': float(data['rcc_ratio']['type_2']) if data['rcc_ratio']['type_2'] else 0,
            'type_3': float(data['rcc_ratio']['type_3']) if data['rcc_ratio']['type_3'] else 0
        }
        total_ratio = sum(rcc_ratio.values())

        # Get rates and wastage
        rates_and_wastage = data.get('rates_and_wastage', {})
        wastage_percent = float(rates_and_wastage.get('wastage_percent', 0))
        rates = {
            'cement': float(rates_and_wastage.get('cement_rate', 0)),
            'sand': float(rates_and_wastage.get('sand_rate', 0)),
            'aggregate': float(rates_and_wastage.get('aggregate_rate', 0)),
            'brick': float(rates_and_wastage.get('brick_rate', 0)),
            'rebar': float(rates_and_wastage.get('rebar_rate', 0)),
            'formwork': float(rates_and_wastage.get('formwork_rate', 0)),
            'casting': float(rates_and_wastage.get('casting_rate', 0))
        }

        # Calculate quantities for each column
        results = {
            'cement': 0,
            'sand': 0,
            'aggregate': 0,
            'brick': 0,
            'rebar': 0,
            'formwork': 0,
            'casting': 0
        }

        rebar_sizes = {8: 0, 10: 0, 12: 0, 16: 0, 20: 0, 25: 0, 28: 0, 32: 0}

        for col in column_data:
            # Calculate volume in cubic feet
            volume = (col['length']/12 * col['breadth']/12 * col['height']) * col['column_nos']
            
            # Calculate materials based on ratio
            if total_ratio > 0:
                results['cement'] += (volume * rcc_ratio['type_1'] * 1.54) / (total_ratio * 1.25)
                results['sand'] += (volume * rcc_ratio['type_2'] * 1.54) / total_ratio
                results['aggregate'] += (volume * rcc_ratio['type_3'] * 1.54) / total_ratio
                results['brick'] += results['aggregate'] * 9.5  # Convert aggregate to brick numbers
            
            # Calculate formwork area in square feet
            formwork = (col['height'] * ((col['length']+col['length'])/12) * 
                       ((col['breadth']+col['breadth'])/12)) * col['column_nos']
            results['formwork'] += formwork
            
            # Calculate casting volume
            results['casting'] += volume

            # Calculate rebar weights
            def calc_rebar_weight(dia, nos, length):
                if dia and nos:
                    return (dia * dia / 532) * nos * length
                return 0

            # Large diameter bars
            if col['large_dia']['size'] and col['large_dia']['nos']:
                length = col['height'] + (col['development_length']/12 if col['development_length'] else 0)
                weight = calc_rebar_weight(col['large_dia']['size'], 
                                        col['large_dia']['nos'], 
                                        length) * col['column_nos']
                results['rebar'] += weight
                rebar_sizes[int(col['large_dia']['size'])] += weight

            # Small diameter bars
            if col['small_dia']['size'] and col['small_dia']['nos']:
                length = col['height'] + (col['development_length']/12 if col['development_length'] else 0)
                weight = calc_rebar_weight(col['small_dia']['size'], 
                                        col['small_dia']['nos'], 
                                        length) * col['column_nos']
                results['rebar'] += weight
                rebar_sizes[int(col['small_dia']['size'])] += weight

            # Tie rods
            if col['tie_rod']['size'] and col['tie_rod']['spacing']:
                ties_count = (col['height']/(col['tie_rod']['spacing']/12)) + 1
                perimeter = ((col['length']*2 - col['clear_cover']*2) + 
                           (col['breadth']*2 - col['clear_cover']*2))/12
                
                # Main ties
                weight = calc_rebar_weight(col['tie_rod']['size'], 
                                        ties_count, 
                                        perimeter) * col['column_nos']
                results['rebar'] += weight
                rebar_sizes[int(col['tie_rod']['size'])] += weight

                # Extra ties
                for extra_tie in [col['extra_tie_1'], col['extra_tie_2']]:
                    if extra_tie:
                        weight = calc_rebar_weight(col['tie_rod']['size'], 
                                                ties_count, 
                                                extra_tie/12) * col['column_nos']
                        results['rebar'] += weight
                        rebar_sizes[int(col['tie_rod']['size'])] += weight

        # Add wastage
        for key in results:
            if results[key] > 0:
                results[key] = results[key] * (1 + wastage_percent/100)

        # Calculate costs
        costs = {
            'cement': results['cement'] * rates['cement'],
            'sand': results['sand'] * rates['sand'],
            'aggregate': results['aggregate'] * rates['aggregate'],
            'brick': results['brick'] * rates['brick'],
            'rebar': results['rebar'] * rates['rebar'],
            'formwork': results['formwork'] * rates['formwork'],
            'casting': results['casting'] * rates['casting']
        }

        # Add wastage to rebar sizes
        for size in rebar_sizes:
            if rebar_sizes[size] > 0:
                rebar_sizes[size] = rebar_sizes[size] * (1 + wastage_percent/100)

        return jsonify({
            'success': True,
            'results': results,
            'costs': costs,
            'rebar_sizes': rebar_sizes,
            'rates': rates
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Make sure there are no spaces or tabs before this line
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
