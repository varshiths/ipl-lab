{0: 'func', 2: 'main'}
{   0: {'control_type': False, 'goto': 1, 'return_type': 'false', 'stats': [**p = 6]},
    1: {'control_type': False, 'goto': None, 'return_type': 'non_void', 'stats': [0]},
    2: {   'control_type': False,
    'goto': 3,
    'return_type': 'false',
    'stats': [**ptr = 5, t0 = func(), **ptr = t0]},
    3: {   'control_type': True,
    'goto1': 4,
    'goto2': 5,
    'return_type': 'false',
    'stats': [t1 = **ptr > 6, 'if(t1)']},
    4: {'control_type': False, 'goto': 6, 'return_type': 'false', 'stats': [**ptr = 7]},
    5: {'control_type': False, 'goto': 6, 'return_type': 'false', 'stats': [**ptr = 8]},
    6: {'control_type': False, 'goto': None, 'return_type': 'void', 'stats': []}}
{0: t0 = func(), 1: t1 = **ptr > 6}
