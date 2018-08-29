import numpy as np
import numpy.testing as npt
from freud import box, density, parallel
import unittest
from freud.errors import FreudDeprecationWarning
import warnings
import os


class TestCorrelationFunction(unittest.TestCase):
    def test_type_check(self):
        boxlen = 10
        N = 500
        rmax, dr = 3, 0.1
        bx = box.Box.cube(boxlen)
        np.random.seed(0)
        points = np.asarray(np.random.uniform(-boxlen/2, boxlen/2, (N, 3)),
                            dtype=np.float32)
        values = np.ones(N)
        corrfun = density.FloatCF(rmax, dr)
        corrfun.compute(bx, points, values, points, values.conj())
        assert True


class TestR(unittest.TestCase):
    def test_generateR(self):
        rmax = 51.23
        dr = 0.1
        nbins = int(rmax / dr)

        # make sure the radius for each bin is generated correctly
        r_list = np.zeros(nbins, dtype=np.float32)
        for i in range(nbins):
            r1 = i * dr
            r2 = r1 + dr
            r_list[i] = 2.0/3.0 * (r2**3.0 - r1**3.0) / (r2**2.0 - r1**2.0)

        ocf = density.FloatCF(rmax, dr)

        npt.assert_almost_equal(ocf.R, r_list, decimal=3)


class TestOCF(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=FreudDeprecationWarning)

    def test_random_points(self):
        rmax = 10.0
        dr = 1.0
        num_points = 1000
        box_size = rmax*3.1
        np.random.seed(0)
        points = np.random.random_sample((num_points, 3)).astype(np.float32) \
            * box_size - box_size/2
        ang = np.random.random_sample((num_points)).astype(np.float64) - 0.5
        ocf = density.FloatCF(rmax, dr)
        correct = np.zeros(int(rmax/dr), dtype=np.float64)
        absolute_tolerance = 0.1
        # first bin is bad
        ocf.accumulate(box.Box.square(box_size), points, ang)
        npt.assert_allclose(ocf.RDF, correct, atol=absolute_tolerance)
        ocf.compute(box.Box.square(box_size), points, ang, points, ang)
        npt.assert_allclose(ocf.getRDF(), correct, atol=absolute_tolerance)
        ocf.reset()
        ocf.accumulate(box.Box.square(box_size), points, ang, points, ang)
        npt.assert_allclose(ocf.RDF, correct, atol=absolute_tolerance)
        ocf.compute(box.Box.square(box_size), points, ang)
        npt.assert_allclose(ocf.getRDF(), correct, atol=absolute_tolerance)
        self.assertEqual(box.Box.square(box_size), ocf.box)
        self.assertEqual(box.Box.square(box_size), ocf.getBox())

    def test_zero_points(self):
        rmax = 10.0
        dr = 1.0
        num_points = 1000
        box_size = rmax*3.1
        np.random.seed(0)
        points = np.random.random_sample((num_points, 3)).astype(np.float32) \
            * box_size - box_size/2
        ang = np.zeros(int(num_points), dtype=np.float64)
        ocf = density.FloatCF(rmax, dr)
        ocf.accumulate(box.Box.square(box_size), points, ang)

        correct = np.zeros(int(rmax/dr), dtype=np.float32)
        absolute_tolerance = 0.1
        npt.assert_allclose(ocf.RDF, correct, atol=absolute_tolerance)

    def test_counts(self):
        rmax = 10.0
        dr = 1.0
        num_points = 10
        box_size = rmax*2
        np.random.seed(0)
        points = np.random.random_sample((num_points, 3)).astype(np.float32) \
            * box_size - box_size/2
        ang = np.zeros(int(num_points), dtype=np.float64)

        vectors = points[np.newaxis, :, :] - points[:, np.newaxis, :]
        correct = np.sum(np.linalg.norm(vectors, axis=-1) < np.sqrt(2*rmax**2))

        ocf = density.FloatCF(rmax, dr)
        ocf.compute(box.Box.square(box_size), points, ang)
        self.assertEqual(np.sum(ocf.getCounts()), correct)
        self.assertEqual(np.sum(ocf.counts), correct)


if __name__ == '__main__':
    unittest.main()
