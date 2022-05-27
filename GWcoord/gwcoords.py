import numpy as np

def rotation_matrix(angle, direction):
    """Return the matrix effecting a rotation by angle, counterclockwise
    around the direction n (i.e. in the sense of the right-hand rule).
    """
    n = direction / np.linalg.norm(direction)
    costh, sinth = np.cos(angle), np.sin(angle)
    p = 1 - costh
    R = np.array([[costh + n[0]*n[0]*p,      n[0]*n[1]*p - n[2]*sinth, n[0]*n[2]*p + n[1]*sinth],
                [n[0]*n[1]*p + n[2]*sinth, costh + n[1]*n[1]*p,      n[1]*n[2]*p - n[0]*sinth],
                [n[0]*n[2]*p - n[1]*sinth, n[2]*n[1]*p + n[0]*sinth, costh + n[2]*n[2]*p]])
    return R
    
def get_location_vector(alpha, sindelta, *args):
    """Celestial coordinates are defined with alpha and delta as azimuthal 
    and (co)polar angles respectively, such that alpha = 0 corresponds to a
    source aligned with the March (vernal) equinox, which serves as X axis;
    delta = 0 corresponds to a source at the celestial equator, and so 
    sin(delta) is the Z coordinate along the celestial North
    """
    cosdelta = np.sqrt(1 - sindelta**2)
    x = cosdelta*np.cos(alpha)
    y = cosdelta*np.sin(alpha)
    z = sindelta
    return np.array([x, y, z])
    
def get_orientation_vector(alpha, sindelta, cosiota, psi, full_output=False):
    """iota is the polar angle between the line of sight and the orbital
    angular momentum, whereas psi is the in-sky angle between the angular
    momentum and the celestial East
    """
    # define celestial north
    north = np.array([0, 0, 1])
    # get wave-vector, which is Z in the waveframe
    n = get_location_vector(alpha, sindelta)
    k = -n
    # get local celestial West
    if abs(sindelta) == 1:
        # source at celestial North, need to disambiguate
        # waveframe orientation
        west = np.array([-np.cos(alpha+np.pi/2), -np.sin(alpha+np.pi/2), 0])
    else:
        west = np.cross(north, k)
        west /= np.linalg.norm(west)
    # the waveframe X is this vector rotated counterclockwise by psi around k,
    # as seen from Earth (i.e., following the right hand rule with thumb 
    # pointing towards k)
    wx = np.dot(rotation_matrix(psi, k), west)
    # finally rotate this vector, which lives in the plane of the sky,
    # such that it lies at an angle iota from z, i.e. rotate around Y
    wy = np.cross(k, wx)
    L = np.dot(rotation_matrix(np.arccos(cosiota), wy), k)
    if full_output:
        return L, west, wx/np.linalg.norm(wx), wy/np.linalg.norm(wy)
    else:
        return L

def plot_waveframe(alpha, sindelta, cosiota, psi):

    north = np.array([0, 0, 1])
    n = get_location_vector(alpha, sindelta)
    k = -n
    L, west, wx, wy = get_orientation_vector(alpha, sindelta, cosiota, psi, full_output=True)

alpha = 0#pi/4
sindelta = np.sin(np.pi/4)
cosiota = np.cos(np.pi/4)
psi = np.pi/4

L, west, wx, wy = get_orientation_vector(alpha, sindelta, cosiota, psi, full_output=True)
