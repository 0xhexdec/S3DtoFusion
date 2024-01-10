import numpy as np


def bezier_surface(x, y, z, uCELLS, wCELLS):
    # DEPENDANT VARIABLES
    # Total number of control points in U
    uPTS = np.size(x, 0)
    wPTS = np.size(x, 1)
    # Total number of subdivisions
    n = uPTS - 1
    m = wPTS - 1
    # Parametric variable
    u = np.linspace(0, 1, uCELLS)
    w = np.linspace(0, 1, wCELLS)
    # # Bernstein basis polynomial
    # b = []
    # d = []

    # Initialised empty matrix for X, Y and Z Bezier curve
    xBezier = np.zeros((uCELLS, wCELLS))
    yBezier = np.zeros((uCELLS, wCELLS))
    zBezier = np.zeros((uCELLS, wCELLS))

    # Binomial coefficients
    def Ni(n, i):
        return np.math.factorial(n) / (np.math.factorial(i) * np.math.factorial(n - i))

    def Mj(m, j):
        return np.math.factorial(m) / (np.math.factorial(j) * np.math.factorial(m - j))

    # Bernstein bases polynomial
    def J(n, i, u):
        return np.matrix(Ni(n, i) * (u ** i) * (1 - u) ** (n - i))

    def K(m, j, w):
        return np.matrix(Mj(m, j) * (w ** j) * (1 - w) ** (m - j))

    # Main loop
    for i in range(0, uPTS):
        for j in range(0, wPTS):
            # # Stores individual basis functions
            # b.append(J(n, i, u))
            # d.append(K(m, j, w))

            # Transpose J array
            Jt = J(n, i, u).transpose()

            # Bezier curve calculation
            xBezier = Jt * K(m, j, w) * x[i, j] + xBezier
            yBezier = Jt * K(m, j, w) * y[i, j] + yBezier
            zBezier = Jt * K(m, j, w) * z[i, j] + zBezier

    return xBezier, yBezier, zBezier


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # USER DEFINED VARIABLES:
    # Control points
    x = np.array([[-0.5, -2, 0], [1, 1, 1], [2, 2, 2]])
    y = np.array([[2, 1, 0], [2, 0, -1], [2, 1, 1]])
    z = np.array([[1, -1, 2], [0, -0.5, 2], [0.5, 1, 2]])

    # slice1 = ([0]*4, [0, 10.022967, 10.033, 0], [5.08, 5.08, 5.788078, 7.440261])
    # slice2 = ([30.467454]*4, [0, 19.916553, 19.936489, 0], [2.007365, 2.007365, 3.550370, 7.150714])
    # slice3 = ([92.985553]*4, [0, 24.975, 25, 0], [0, 0, 2.362212, 7.874037])
    # slice4 = ([169.430546]*4, [0, 17.505182, 17.522705, 0], [4.065244, 4.065244, 5.333662, 8.293304])
    # slice5 = ([199.898]*4, [0, 4.950495, 5, 0], [9.906000, 9.906000, 10.259271, 11.083571])
    # slices = [slice1, slice2, slice3, slice4, slice5]

    # outline = ([0, 30.48, 92.964, 169.418, 199.898], [10.033, 19.939, 25, 17.526, 5], [0]*5)

    # ctrl_points = slices #+ [outline]

    # x = np.array([p[0] for p in ctrl_points])
    # y = np.array([p[1] for p in ctrl_points])
    # z = np.array([p[2] for p in ctrl_points])
    # Number of cells for each direction
    uCELLS = 12
    wCELLS = 10

    # # Plotting Bernstein basis polynomials
    # plt.figure()
    # plt.subplot(121)
    # for line in b:
    #     plt.plot(u, line.transpose())
    # plt.subplot(122)
    # for line in d:
    #     plt.plot(w, line.transpose())
    # plt.show()

    xBezier, yBezier, zBezier = bezier_surface(x, y, z, uCELLS, wCELLS)

    # Bezier surface
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.plot_surface(xBezier, yBezier, zBezier)
    ax.scatter(x, y, z, edgecolors='face')
    ax.set_aspect('equal', 'box')
    fig.tight_layout()
    plt.show()