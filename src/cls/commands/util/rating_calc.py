import numpy as np

tau = 0.2 # Constant suggested by glicko2

def g(phi):
    return 1 / np.sqrt(1+3*phi**2 / np.pi**2)


def E(mu, mu_, phi_):
    return 1 / (1 + np.exp(-g(phi_)*(mu-mu_)))


def f(x, delta, phi, v, sigma):
    a = np.log(sigma**2)
    return np.exp(x) * (delta**2 - phi**2 - v - np.exp(x)) / 2 / (phi**2+v**2+np.exp(x)) - (x-a) / tau**2


def find_new_sigma(sigma, delta, phi, v):
    A = np.log(sigma**2)
    a = np.log(sigma**2)

    epsilon = 0.000001

    B = 0
    if delta**2 > phi**2+v:
        B=np.log(delta**2-phi**2-v)
    else:
        k=1
        while f(a - k*tau, delta, phi, v, sigma) < 0:
            k = k+1
            B = a - k*tau

    fA = f(A, delta, phi, v, sigma)
    fB = f(B, delta, phi, v, sigma)

    while np.abs(B-A) > epsilon:
        C = A + (A-B)*fA / (fB-fA)
        fC = f(C, delta, phi, v, sigma)

        if fC*fB <= 0:
            A = B
            fA = fB

        else:
            fA = fA / 2

        B = C
        fB = fC

    return np.exp(A/2)


def calculate_rating_changes(r1, RD1, sigma1, r2, RD2, sigma2, s): # Here s is the score of the first player against the second
    mu1 = (r1-1000) / 173.7178
    phi1 = RD1/173.7178

    mu2 = (r2-1000) / 173.7178
    phi2 = RD2/173.7178

    v1 = 1 / (g(phi2)**2 * E(mu1, mu2, phi2) * (1 - E(mu1, mu2, phi2)))
    v2 = 1 / (g(phi1)**2 * E(mu2, mu1, phi1) * (1 - E(mu2, mu1, phi1)))

    delta1 = v1*g(phi2)*(s - E(mu1, mu2, phi2))
    delta2 = v2*g(phi1)*((1-s) - E(mu2, mu1, phi1))

    phi1_ = np.sqrt(phi1**2+find_new_sigma(sigma1, delta1, phi1, v1)**2)
    phi2_ = np.sqrt(phi2**2+find_new_sigma(sigma2, delta2, phi2, v2)**2)

    phi1__ = 1/np.sqrt(1/phi1_**2+1/v1)
    phi2__ = 1/np.sqrt(1/phi2_**2+1/v2)

    mu1__ = mu1 + phi1__**2*g(phi2)*(s - E(mu1, mu2, phi2))
    mu2__ = mu2 + phi2__**2*g(phi1)*((1-s) - E(mu2, mu1, phi1))

    return (float(173.7178 * mu1__ + 1000), float(phi1__*173.7178), float(find_new_sigma(sigma1, delta1, phi1, v1)), float(173.7178 * mu2__ + 1000), float(phi2__*173.7178), float(find_new_sigma(sigma2, delta2, phi2, v2)))
