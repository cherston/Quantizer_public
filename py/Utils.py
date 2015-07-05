import math
import numpy as np

#===========================================================
def deltaR(p1, p2):
    deltaeta = p1.Eta - p2.Eta
    deltaphi = p1.Phi - p2.Phi
    while (deltaphi >= math.pi): deltaphi -= 2*math.pi;
    while (deltaphi < -math.pi): deltaphi += 2*math.pi;
    return math.sqrt(deltaeta**2 + deltaphi**2)

def find_nearest(array,value):
	idx = (np.abs(array-value)).argmin()
	return idx
	

#coordinate conversion code below is taken from: https://searchcode.com/codesearch/view/45808784/

def cart_to_rap(cart_point):
    """
    cart_point is a 3-tuple representing a cartesian point (x, y, z).
    Converts from cartesian to ATLAS pseudo-rapidity coordinates (r, eta, phi),
    where r is the distance from the beam line, not the collision point.
    """

    x = cart_point[0]
    y = cart_point[1]
    z = cart_point[2]

    r     = math.sqrt(x**2 + y**2)
    phi   = math.atan2(y,x)
    theta = math.atan2(r,z)
    eta   = -math.log(math.tan(theta/2.0))

    return (r, eta, phi)



## --------------------------------------- ##
def rap_to_cart(rap_point):
    """
    rap_point is a 3-tuple representing an ATLAS pseudo-rapidity point (r, eta, phi).
    Converts from ATLAS cylindrical to cartesian coordinates (x, y, z),
    r is the distance from the beam line, not the collision point.
    """

    r   = rap_point[0]
    eta = rap_point[1]
    phi = rap_point[2]

    x = r*math.cos(phi)
    y = r*math.sin(phi)

    theta = 2*math.atan(math.exp(-eta))
    z = r/math.tan(theta)

    return (x, y, z)



## --------------------------------------- ##
def cart_to_cyl(cart_point):
    """
    cart_point is a 3-tuple representing a cartesian point (x, y, z).
    Converts from cartesian to ATLAS cylindrical coordinates (r, z, phi),
    where r is the distance from the beam line, not the collision point.
    """

    x = cart_point[0]
    y = cart_point[1]
    z = cart_point[2]

    r   = math.sqrt(x**2 + y**2)
    phi = math.atan2(y,x)

    return (r, z, phi)



## --------------------------------------- ##
def cyl_to_cart(cyl_point):
    """
    cyl_point is a 3-tuple representing an ATLAS cylindrical point (r, z, phi).
    Converts from ATLAS cylindrical to cartesian coordinates (x, y, z),
    r is the distance from the beam line, not the collision point.
    """

    r   = cyl_point[0]
    z   = cyl_point[1]
    phi = cyl_point[2]

    x = r*math.cos(phi)
    y = r*math.sin(phi)

    return (x, y, z)



## --------------------------------------- ##
def z_to_eta(cyl_point):
    """
    cyl_point is a 2-tuple containing radial (r) and longitudinal (z)
    coordinates, what you need to figure out the polar angle w.r.t.
    the transverse plane of the original coordinate system. The resulting
    angle is pseudorapidity.
    """

    r   = cyl_point[0]
    z   = cyl_point[1]

    theta = math.atan2(r,z)
    eta   = -math.log(math.tan(theta/2.0))

    return eta



## --------------------------------------- ##
def eta_to_z(rap_point):
    """
    rap_point is a 2-tuple containing radial (r) and pseudorapidity (eta)
    coordinates, what you need to figure out the longitudinal distance z.
    """

    r   = rap_point[0]
    eta = rap_point[1]

    theta = 2*math.atan(math.exp(-eta))
    z = r/math.tan(theta)

    return z

def eta_to_theta(eta): 
	return 2*math.atan(math.exp(-eta))
    