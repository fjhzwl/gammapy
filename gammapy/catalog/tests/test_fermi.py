# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_allclose
from astropy import units as u
from astropy.time import Time
from astropy.utils.data import get_pkg_data_filename
from gammapy.catalog import (
    SourceCatalog1FHL,
    SourceCatalog2FHL,
    SourceCatalog3FGL,
    SourceCatalog3FHL,
    SourceCatalog4FGL,
)
from gammapy.modeling.models import (
    ExpCutoffPowerLaw3FGLSpectralModel,
    LogParabolaSpectralModel,
    PowerLawSpectralModel,
    SuperExpCutoffPowerLaw3FGLSpectralModel,
    SuperExpCutoffPowerLaw4FGLSpectralModel,
)
from gammapy.utils.testing import (
    assert_quantity_allclose,
    assert_time_allclose,
    requires_data,
    requires_dependency,
)

SOURCES_4FGL = [
    dict(
        idx=0,
        name="4FGL J0000.3-7355",
        spec_type=PowerLawSpectralModel,
        dnde=u.Quantity(2.9476e-11, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(5.3318e-12, "cm-2 s-1 GeV-1"),
    ),
    dict(
        idx=3,
        name="4FGL J0001.5+2113",
        spec_type=LogParabolaSpectralModel,
        dnde=u.Quantity(2.8545e-8, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(1.3324e-9, "cm-2 s-1 GeV-1"),
    ),
    dict(
        idx=7,
        name="4FGL J0002.8+6217",
        spec_type=SuperExpCutoffPowerLaw4FGLSpectralModel,
        dnde=u.Quantity(2.084e-09, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(1.0885e-10, "cm-2 s-1 GeV-1"),
    ),
]

SOURCES_3FGL = [
    dict(
        idx=0,
        name="3FGL J0000.1+6545",
        str_ref_file="data/3fgl_J0000.1+6545.txt",
        spec_type=PowerLawSpectralModel,
        dnde=u.Quantity(1.4351261e-9, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(2.1356270e-10, "cm-2 s-1 GeV-1"),
    ),
    dict(
        idx=4,
        name="3FGL J0001.4+2120",
        str_ref_file="data/3fgl_J0001.4+2120.txt",
        spec_type=LogParabolaSpectralModel,
        dnde=u.Quantity(8.3828599e-10, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(2.6713238e-10, "cm-2 s-1 GeV-1"),
    ),
    dict(
        idx=55,
        name="3FGL J0023.4+0923",
        str_ref_file="data/3fgl_J0023.4+0923.txt",
        spec_type=ExpCutoffPowerLaw3FGLSpectralModel,
        dnde=u.Quantity(1.8666925e-09, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(2.2068837e-10, "cm-2 s-1 GeV-1"),
    ),
    dict(
        idx=960,
        name="3FGL J0835.3-4510",
        str_ref_file="data/3fgl_J0835.3-4510.txt",
        spec_type=SuperExpCutoffPowerLaw3FGLSpectralModel,
        dnde=u.Quantity(1.6547128794756733e-06, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(1.6621504e-11, "cm-2 s-1 MeV-1"),
    ),
]

SOURCES_3FHL = [
    dict(
        idx=352,
        name="3FHL J0534.5+2201",
        spec_type=PowerLawSpectralModel,
        dnde=u.Quantity(6.3848912826152664e-12, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(2.679593524691324e-13, "cm-2 s-1 GeV-1"),
    ),
    dict(
        idx=1442,
        name="3FHL J2158.8-3013",
        spec_type=LogParabolaSpectralModel,
        dnde=u.Quantity(2.056998292908196e-12, "cm-2 s-1 GeV-1"),
        dnde_err=u.Quantity(4.219030630302381e-13, "cm-2 s-1 GeV-1"),
    ),
]


@requires_data()
class TestFermi4FGLObject:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog4FGL()

    @requires_dependency("uncertainties")
    @pytest.mark.parametrize("ref", SOURCES_4FGL, ids=lambda _: _["name"])
    def test_spectral_model(self, ref):
        model = self.cat[ref["idx"]].spectral_model

        e_ref = model.reference.quantity
        dnde, dnde_err = model.evaluate_error(e_ref)
        assert isinstance(model, ref["spec_type"])
        assert_quantity_allclose(dnde, ref["dnde"], rtol=1e-4)
        assert_quantity_allclose(dnde_err, ref["dnde_err"], rtol=1e-4)


@requires_data()
class TestFermi3FGLObject:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog3FGL()
        # Use 3FGL J0534.5+2201 (Crab) as a test source
        cls.source_name = "3FGL J0534.5+2201"
        cls.source = cls.cat[cls.source_name]

    def test_name(self):
        assert self.source.name == self.source_name

    def test_index(self):
        assert self.source.index == 621

    def test_data(self):
        assert_allclose(self.source.data["Signif_Avg"], 30.669872283935547)

    def test_position(self):
        position = self.source.position
        assert_allclose(position.ra.deg, 83.637199, atol=1e-3)
        assert_allclose(position.dec.deg, 22.024099, atol=1e-3)

    @pytest.mark.parametrize("ref", SOURCES_3FGL, ids=lambda _: _["name"])
    def test_str(self, ref):
        actual = str(self.cat[ref["idx"]])
        expected = open(get_pkg_data_filename(ref["str_ref_file"])).read()
        assert actual == expected

    def test_data_python_dict(self):
        data = self.source._data_python_dict
        assert isinstance(data["RAJ2000"], float)
        assert data["RAJ2000"] == 83.63719940185547
        assert isinstance(data["Unc_Flux100_300"], list)
        assert isinstance(data["Unc_Flux100_300"][0], float)
        assert_allclose(data["Unc_Flux100_300"][0], -1.44535601265261e-08)

    @requires_dependency("uncertainties")
    @pytest.mark.parametrize("ref", SOURCES_3FGL, ids=lambda _: _["name"])
    def test_spectral_model(self, ref):
        model = self.cat[ref["idx"]].spectral_model

        dnde, dnde_err = model.evaluate_error(1 * u.GeV)

        assert isinstance(model, ref["spec_type"])
        assert_quantity_allclose(dnde, ref["dnde"])
        assert_quantity_allclose(dnde_err, ref["dnde_err"])

    def test_spatial_model(self):
        # TODO: check spatial parameter errors as soon as they are filled
        model = self.cat[0].spatial_model
        assert model.tag == "PointSpatialModel"
        assert model.frame == "galactic"
        p = model.parameters
        assert_allclose(p["lon_0"].value, 117.693878)
        assert_allclose(p["lat_0"].value, 3.402958)

        model = self.cat[122].spatial_model
        assert model.tag == "GaussianSpatialModel"
        assert model.frame == "galactic"
        p = model.parameters
        assert_allclose(p["lon_0"].value, 302.145142)
        assert_allclose(p["lat_0"].value, -44.41674)
        assert_allclose(p["sigma"].value, 1.35)

        model = self.cat[955].spatial_model
        assert model.tag == "DiskSpatialModel"
        assert model.frame == "galactic"
        p = model.parameters
        assert_allclose(p["lon_0"].value, 263.33252)
        assert_allclose(p["lat_0"].value, -3.105928)
        assert_allclose(p["r_0"].value, 0.91)

        model = self.cat[602].spatial_model
        assert model.tag == "TemplateSpatialModel"
        assert model.frame == "fk5"
        assert model.normalize is True

    @pytest.mark.parametrize("ref", SOURCES_3FGL, ids=lambda _: _["name"])
    def test_sky_model(self, ref):
        self.cat[ref["idx"]].sky_model

    def test_flux_points(self):
        flux_points = self.source.flux_points

        assert len(flux_points.table) == 5
        assert "flux_ul" in flux_points.table.colnames
        assert flux_points.sed_type == "flux"

        desired = [1.645888e-06, 5.445407e-07, 1.255338e-07, 2.545524e-08, 2.263189e-09]
        assert_allclose(flux_points.table["flux"].data, desired, rtol=1e-5)

    def test_flux_points_ul(self):
        source = self.cat["3FGL J0000.2-3738"]
        flux_points = source.flux_points

        desired = [4.096391e-09, 6.680059e-10, np.nan, np.nan, np.nan]
        assert_allclose(flux_points.table["flux_ul"].data, desired, rtol=1e-5)

    def test_lightcurve(self):
        lc = self.source.lightcurve
        table = lc.table

        assert len(table) == 48
        assert table.colnames == [
            "time_min",
            "time_max",
            "flux",
            "flux_errp",
            "flux_errn",
        ]

        expected = Time(54680.02313657408, format="mjd", scale="utc")
        assert_time_allclose(lc.time_min[0], expected)

        expected = Time(54710.43824797454, format="mjd", scale="utc")
        assert_time_allclose(lc.time_max[0], expected)

        assert table["flux"].unit == "cm-2 s-1"
        assert_allclose(table["flux"][0], 2.384e-06, rtol=1e-3)

        assert table["flux_errp"].unit == "cm-2 s-1"
        assert_allclose(table["flux_errp"][0], 8.071e-08, rtol=1e-3)

        assert table["flux_errn"].unit == "cm-2 s-1"
        assert_allclose(table["flux_errn"][0], 8.071e-08, rtol=1e-3)

    def test_crab_alias(self):
        for name in [
            "Crab",
            "3FGL J0534.5+2201",
            "1FHL J0534.5+2201",
            "PSR J0534+2200",
        ]:
            assert self.cat[name].index == 621


@requires_data()
class TestFermi1FHLObject:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog1FHL()
        # Use 1FHL J0534.5+2201 (Crab) as a test source
        cls.source_name = "1FHL J0534.5+2201"
        cls.source = cls.cat[cls.source_name]

    def test_name(self):
        assert self.source.name == self.source_name

    def test_position(self):
        position = self.source.position
        assert_allclose(position.ra.deg, 83.628098, atol=1e-3)
        assert_allclose(position.dec.deg, 22.0191, atol=1e-3)

    def test_spectral_model(self):
        model = self.source.spectral_model
        energy = u.Quantity(100, "GeV")
        desired = u.Quantity(4.7717464131e-12, "cm-2 GeV-1 s-1")
        assert_quantity_allclose(model(energy), desired)

    def test_flux_points(self):
        # test flux point on  PKS 2155-304
        src = self.cat["1FHL J0153.1+7515"]
        flux_points = src.flux_points
        actual = flux_points.table["flux"]
        desired = [5.523017e-11, 0, 0] * u.Unit("cm-2 s-1")
        assert_quantity_allclose(actual, desired)

        actual = flux_points.table["flux_ul"]
        desired = [np.nan, 4.163177e-11, 2.599397e-11] * u.Unit("cm-2 s-1")
        assert_quantity_allclose(actual, desired, rtol=1e-5)


@requires_data()
class TestFermi2FHLObject:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog2FHL()
        # Use 2FHL J0534.5+2201 (Crab) as a test source
        cls.source_name = "2FHL J0534.5+2201"
        cls.source = cls.cat[cls.source_name]

    def test_name(self):
        assert self.source.name == self.source_name

    def test_position(self):
        position = self.source.position
        assert_allclose(position.ra.deg, 83.634102, atol=1e-3)
        assert_allclose(position.dec.deg, 22.0215, atol=1e-3)

    def test_spectral_model(self):
        model = self.source.spectral_model
        energy = u.Quantity(100, "GeV")
        desired = u.Quantity(6.8700477298e-12, "cm-2 GeV-1 s-1")
        assert_quantity_allclose(model(energy), desired)

    def test_flux_points(self):
        # test flux point on  PKS 2155-304
        src = self.cat["PKS 2155-304"]
        flux_points = src.flux_points
        actual = flux_points.table["flux"]
        desired = [2.866363e-10, 6.118736e-11, 3.257970e-16] * u.Unit("cm-2 s-1")
        assert_quantity_allclose(actual, desired)

        actual = flux_points.table["flux_ul"]
        desired = [np.nan, np.nan, 1.294092e-11] * u.Unit("cm-2 s-1")
        assert_quantity_allclose(actual, desired, rtol=1e-3)


@requires_data()
class TestFermi3FHLObject:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog3FHL()
        # Use 3FHL J0534.5+2201 (Crab) as a test source
        cls.source_name = "3FHL J0534.5+2201"
        cls.source = cls.cat[cls.source_name]

    def test_name(self):
        assert self.source.name == self.source_name

    def test_index(self):
        assert self.source.index == 352

    def test_data(self):
        assert_allclose(self.source.data["Signif_Avg"], 168.64082)

    def test_str(self):
        actual = str(self.cat["3FHL J2301.9+5855e"])  # an extended source
        expected = open(get_pkg_data_filename("data/3fhl_j2301.9+5855e.txt")).read()
        assert actual == expected

    def test_data_python_dict(self):
        data = self.source._data_python_dict
        assert isinstance(data["RAJ2000"], float)
        assert data["RAJ2000"] == 83.63483428955078
        assert isinstance(data["Flux_Band"], list)
        assert isinstance(data["Flux_Band"][0], float)
        assert_allclose(data["Flux_Band"][0], 5.1698894054652555e-09)

    def test_position(self):
        position = self.source.position
        assert_allclose(position.ra.deg, 83.634834, atol=1e-3)
        assert_allclose(position.dec.deg, 22.019203, atol=1e-3)

    @requires_dependency("uncertainties")
    @pytest.mark.parametrize("ref", SOURCES_3FHL, ids=lambda _: _["name"])
    def test_spectral_model(self, ref):
        model = self.cat[ref["idx"]].spectral_model

        dnde, dnde_err = model.evaluate_error(100 * u.GeV)

        assert isinstance(model, ref["spec_type"])
        assert_quantity_allclose(dnde, ref["dnde"])
        assert_quantity_allclose(dnde_err, ref["dnde_err"])

    @pytest.mark.parametrize("ref", SOURCES_3FHL, ids=lambda _: _["name"])
    def test_spatial_model(self, ref):
        model = self.cat[ref["idx"]].spatial_model
        assert model.frame == "galactic"

    @pytest.mark.parametrize("ref", SOURCES_3FHL, ids=lambda _: _["name"])
    def test_sky_model(self, ref):
        self.cat[ref["idx"]].sky_model

    def test_flux_points(self):
        flux_points = self.source.flux_points

        assert len(flux_points.table) == 5
        assert "flux_ul" in flux_points.table.colnames

        desired = [5.169889e-09, 2.245024e-09, 9.243175e-10, 2.758956e-10, 6.684021e-11]
        assert_allclose(flux_points.table["flux"].data, desired, rtol=1e-3)

    def test_crab_alias(self):
        for name in ["Crab Nebula", "3FHL J0534.5+2201", "3FGL J0534.5+2201i"]:
            assert self.cat[name].index == 352


@requires_data()
class TestSourceCatalog3FGL:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog3FGL()

    def test_main_table(self):
        assert len(self.cat.table) == 3034

    def test_extended_sources(self):
        table = self.cat.extended_sources_table
        assert len(table) == 25

    def test_select_source_classes(self):
        selection = self.cat.select_source_class("galactic")
        assert len(selection.table) == 101

        selection = self.cat.select_source_class("extra-galactic")
        assert len(selection.table) == 1684

        selection = self.cat.select_source_class("unassociated")
        assert len(selection.table) == 1010

        selection = self.cat.select_source_class("ALL")
        assert len(selection.table) == 239

        selection = self.cat.select_source_class("PSR")
        assert len(selection.table) == 143


@requires_data()
class TestSourceCatalog1FHL:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog1FHL()

    def test_main_table(self):
        assert len(self.cat.table) == 514

    def test_extended_sources(self):
        table = self.cat.extended_sources_table
        assert len(table) == 18

    def test_crab_alias(self):
        for name in [
            "Crab",
            "1FHL J0534.5+2201",
            "2FGL J0534.5+2201",
            "PSR J0534+2200",
        ]:
            assert self.cat[name].index == 116


@requires_data()
class TestSourceCatalog2FHL:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog2FHL()

    def test_main_table(self):
        assert len(self.cat.table) == 360

    def test_extended_sources(self):
        table = self.cat.extended_sources_table
        assert len(table) == 25

    def test_crab_alias(self):
        for name in [
            "Crab",
            "3FGL J0534.5+2201i",
            "1FHL J0534.5+2201",
            "TeV J0534+2200",
        ]:
            assert self.cat[name].index == 85


@requires_data()
class TestSourceCatalog3FHL:
    @classmethod
    def setup_class(cls):
        cls.cat = SourceCatalog3FHL()

    def test_main_table(self):
        assert len(self.cat.table) == 1556

    def test_extended_sources(self):
        table = self.cat.extended_sources_table
        assert len(table) == 55

    def test_select_source_classes(self):
        selection = self.cat.select_source_class("galactic")
        assert len(selection.table) == 44

        selection = self.cat.select_source_class("extra-galactic")
        assert len(selection.table) == 1177

        selection = self.cat.select_source_class("unassociated")
        assert len(selection.table) == 177

        selection = self.cat.select_source_class("ALL")
        assert len(selection.table) == 135

        selection = self.cat.select_source_class("PSR")
        assert len(selection.table) == 53
