from django.shortcuts import render

from math import sqrt
from fractions import Fraction

import datetime

def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:      
        a, b = b, a % b
    return a

def lcm(a, b):
    """Return lowest common multiple."""
    return a * b // gcd(a, b)

def lcmm(*args):
    """Return lcm of args."""   
    return reduce(lcm, args)


def find_factors(n):  
    """ 
    Generator for getting factors for a number 
    """  
    #yield 1  
    i = 2  
    limit = sqrt(n) 
    while i <= limit:  
        if n % i == 0:  
            yield i  
            n = n / i  
            limit = sqrt(n)  
        else:  
            i += 1  
    if n > 1:  
            yield n   


def nice_factor(n):
    factors = find_factors(n)
    
    reduced_factors = {}
    
    for factor in factors:
        try:
            reduced_factors[factor] += 1
        except KeyError:
            reduced_factors[factor] = 1
    
    return reduced_factors
        
def determine_burden(m, k):  
    k_contribution = k * 200
    
    k_test = k - 35 #How much bigger than 35 is k?
    
    
    
    m_contribution = (float(m) / 10000) + 1
    
    
    
    if k_test > 0:
        k_adjustment = k_test * 300 #Add another 300 for each point above 35. 
        k_contribution += k_adjustment
            
    m_adjustment = 10 - m
    
    low_numbers_bonus = 40 - (k + m)
    
    both_adjustment = m_adjustment + low_numbers_bonus
    
    if both_adjustment < 1:
        both_adjustment = 1
    
    burden = (k_contribution  / both_adjustment) * m_contribution
    
    return burden

def get_sigma(request):
    '''
    Take a sequence of integers - let's say 8-10.  That'd be sigma(8,3).
    Add up the reciprocals of the sequence: 1/8 + 1/9 + 1/10. 
    Return the value as a fraction, reduced to the powers of primes.
    '''
    
    starting_integer = int(request.GET['m'])
    sequence_length = int(request.GET['k'])
    
    burden = determine_burden(starting_integer, sequence_length)
   
    too_big = False
    
    max_burden = 2000
    
    if burden > max_burden:
        too_big = True

    if too_big:
        return render(request, 'math/too_big.html', locals())
    
    #Begin time measurement
    then = datetime.datetime.now()
    
    limit = starting_integer + sequence_length #This is the first number in the sequence that we don't want to consider - 11 in our example.
    
    #A list of our candidates - ie [8, 9, 10]
    candidates = range(starting_integer, limit)
    
    #Find out their lowest common multiple
    lowest_common_multiple = lcmm(*candidates)
    
    #Find out the LCM in reduced prime factors
    nice_lcm = nice_factor(lowest_common_multiple)
    
    #A list comp using sum to do 1/8 + 1/9 + 1/10
    harmonic_result = sum(Fraction(1, candidate_denominator) for candidate_denominator in candidates)



    denominator = harmonic_result.denominator
    numerator = harmonic_result.numerator

    reduced_denominator = nice_factor(denominator) #Reduce the denominator to a sum of powers of primes.
    reduced_numerator = nice_factor(numerator) #...and do the same for the numerator, although it will usually be prime anyway.

    reduced_result =  reduced_numerator, reduced_denominator
    
    as_decimal = float(numerator) / float(denominator)
    
    #End time measurement.
    now = datetime.datetime.now()
    
    how_long = now - then
    float_microseconds = float(how_long.microseconds) / 1000000
    how_long_seconds = float(how_long.seconds) + float_microseconds 
    burden_time = burden / how_long_seconds 
    
    
    return render(request, 'math/get_sigma.html', locals())

