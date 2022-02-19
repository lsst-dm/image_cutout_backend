# This file is part of image_cutout_backend.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os.path
import tempfile
import unittest

import lsst.utils.tests
from lsst.image_cutout_backend import ImageCutoutBackend, RgbImageCutout, projection_finders, stencils


class TestRgbImageCutouts(lsst.utils.tests.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.data_dir = lsst.utils.getPackageDir("testdata_image_cutouts")
        except LookupError:
            raise unittest.SkipTest("testdata_image_cutouts not setup.")

    def setUp(self):
        collection = "2.2i/runs/test-med-1/w_2022_03/DM-33223/20220118T193330Z"
        self.butler = lsst.daf.butler.Butler(os.path.join(self.data_dir, "repo"), collections=collection)

        # Centered on a galaxy
        point = lsst.geom.SpherePoint(56.6400770 * lsst.geom.degrees, -36.4492250 * lsst.geom.degrees)
        radius = 10 * lsst.geom.arcseconds
        self.stencil = stencils.SkyCircle(point, radius)

        self.projectionFinder = projection_finders.ReadComponents()

        dataId = dict(patch=24, tract=3828, skymap="DC2")
        dataId['band'] = 'g'
        self.dataRefB = self.butler.registry.findDataset("deepCoadd_calexp", dataId=dataId)
        dataId['band'] = 'r'
        self.dataRefG = self.butler.registry.findDataset("deepCoadd_calexp", dataId=dataId)
        dataId['band'] = 'i'
        self.dataRefR = self.butler.registry.findDataset("deepCoadd_calexp", dataId=dataId)

    def test_extract_refs(self):
        """Extract images with g->B, r->G, i->R."""
        with tempfile.TemporaryDirectory() as tempdir:
            backend = ImageCutoutBackend(self.butler, self.projectionFinder, tempdir)
            cutoutBackend = RgbImageCutout(backend)
            result = cutoutBackend.extract_ref(self.stencil, self.dataRefR, self.dataRefG, self.dataRefB)

            box = result.r.cutout.getBBox()
            self.assertEqual(box, result.g.cutout.getBBox())
            self.assertEqual(box, result.b.cutout.getBBox())
            self.assertEqual(box.width, 101)
            self.assertEqual(box.height, 101)
            # The galaxy should be near the center of the image.
            self.assertFloatsAlmostEqual(result.r.cutout.image.array[50, 49], 2.5095553398132324)
            self.assertFloatsAlmostEqual(result.g.cutout.image.array[50, 49], 2.0735855102539062)
            self.assertFloatsAlmostEqual(result.b.cutout.image.array[50, 49], 1.2568331956863403)

    def test_process_refs_png(self):



if __name__ == "__main__":
    unittest.main()
