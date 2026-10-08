"""Hot-path scripts: axes, overview, manifest, fit gates, k gates."""

import json
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np
import pytest
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from arpes_hotpath.axes import axes_report
from arpes_hotpath.convert_k import prepare_k, run_convert
from arpes_hotpath.fit_edc import extract_edc, fit_edc_curve
from arpes_hotpath.manifest import write_manifest
from arpes_hotpath.overview import classify_kind, render_overview
from arpes_hotpath.policy import PolicyRefusal


def _cut(phi_name="phi", phi_units="deg", e_min=-1.2, e_max=0.1, n_e=16, n_phi=20):
    energy = np.linspace(e_min, e_max, n_e)
    phi = np.linspace(-12, 12, n_phi)
    intensity = np.exp(-((energy[:, None] + 0.3) ** 2) / 0.05) * np.exp(-(phi[None, :] ** 2) / 40.0)
    return xr.DataArray(
        intensity,
        coords={
            "eV": ("eV", energy, {"units": "eV"}),
            phi_name: (phi_name, phi, {"units": phi_units}),
        },
        dims=("eV", phi_name),
        name="spectrum",
    )


def _write_nc(path, da):
    da.to_dataset(name="spectrum").to_netcdf(path)


def test_energy_label_from_range_clue_not_from_large_positive():
    claimed = _cut()
    report = axes_report(claimed, source_path="cut.nc", backend="inspect-only")
    assert report["energy"]["label"] == "E-EF"
    assert report["energy"]["claimed"] is True
    assert report["report_momentum"] is False
    wide = _cut(e_min=90, e_max=95)
    wide_report = axes_report(wide, source_path="wide.nc", backend="inspect-only")
    assert wide_report["energy"]["label"] == "ambiguous"


def test_angle_named_as_k_is_not_momentum():
    da = _cut(phi_name="kx", phi_units="deg")
    report = axes_report(da, source_path="bad.nc", backend="inspect-only")
    assert report["angle_as_k"]
    assert report["angle_as_k"][0]["dim"] == "kx"
    assert report["report_momentum"] is False


def test_overview_cut_stays_angle_space(tmp_path):
    da = _cut()
    rendered = render_overview(da, stem="demo", out_dir=tmp_path)
    assert rendered["kind"] == "cut"
    assert rendered["assumptions"]["k_conversion"] == "off"
    assert rendered["assumptions"]["momentum_reported"] is False
    assert rendered["assumptions"]["gamma_claimed"] is False
    labels = " ".join(rendered["assumptions"]["axis_labels"].values())
    assert "Å" not in labels
    assert "angstrom" not in labels.casefold()
    assert Path(rendered["plots"][0]).is_file()


def test_overview_refuses_momentum_label_on_kx(tmp_path):
    da = _cut(phi_name="kx", phi_units="deg")
    rendered = render_overview(da, stem="bad", out_dir=tmp_path)
    label = rendered["assumptions"]["axis_labels"]["kx"]
    assert "not momentum" in label
    assert rendered["assumptions"]["momentum_reported"] is False


def test_fermi_trio_and_hv_not_kz(tmp_path):
    energy = np.linspace(-0.5, 0.1, 8)
    phi = np.linspace(-10, 10, 6)
    psi = np.linspace(-8, 8, 5)
    values = np.ones((8, 6, 5))
    fermi = xr.DataArray(
        values,
        coords={
            "eV": ("eV", energy, {"units": "eV"}),
            "phi": ("phi", phi, {"units": "deg"}),
            "psi": ("psi", psi, {"units": "deg"}),
        },
        dims=("eV", "phi", "psi"),
    )
    rendered = render_overview(fermi, stem="fs", out_dir=tmp_path)
    assert rendered["kind"] == "fermi"
    assert len(rendered["plots"]) == 3
    assert rendered["assumptions"]["absolute_kz"] is False
    hv = fermi.rename({"psi": "hv"})
    hv = hv.assign_coords(hv=("hv", np.linspace(90, 100, 5), {"units": "eV"}))
    hv_rendered = render_overview(hv, stem="eph", out_dir=tmp_path)
    assert hv_rendered["kind"] == "hv"
    assert len(hv_rendered["plots"]) == 3


def test_core_as_2d_from_span(tmp_path):
    da = _cut(e_min=-12, e_max=0.2, n_e=24)
    kind, _conf, clues = classify_kind(da)
    assert kind == "core_level_2d"
    assert clues
    rendered = render_overview(da, stem="core", out_dir=tmp_path)
    assert len(rendered["plots"]) == 2


def test_manifest_ignores_measurement_type(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    with h5py.File(data / "scan.h5", "w") as handle:
        handle.attrs["Measurement Type"] = "Fermi Map"
        handle.attrs["photon_energy"] = 91.5
        handle.create_dataset("eV", data=np.linspace(-1, 0, 4))
        handle.create_dataset("phi", data=np.linspace(-5, 5, 5))
        handle.create_dataset("spectrum", data=np.zeros((4, 5)))
    summary = write_manifest(data, data / "analysis")
    manifest = json.loads((data / "analysis" / "manifest.json").read_text())
    row = manifest["files"][0]
    assert row["kind"] == "cut"
    assert row["kind"] != "fermi"
    assert row["hv_eV"] == 91.5
    assert row["backend"] is None
    assert summary["n_files"] == 1
    assert "Fermi Map" not in json.dumps(row["kind_clues"])


def test_manifest_mh1_backend_and_fits_preferred(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    with h5py.File(data / "pair.h5", "w") as handle:
        handle.create_group("Headers")
        handle.attrs["Beamline Energy"] = 80
    (data / "pair.fits").write_bytes(b"not a real fits")
    write_manifest(data, tmp_path / "analysis")
    manifest = json.loads((tmp_path / "analysis" / "manifest.json").read_text())
    assert len(manifest["files"]) == 1
    row = manifest["files"][0]
    assert row["ext"] == ".fits"
    assert row["path"].endswith("pair.fits")
    assert row["path_alt"].endswith("pair.h5")
    assert row["backend"] == "pyarpes"
    assert "MAESTRO" in (row["preferred_loader"] or "")
    assert row["kind"] == "unknown"


def test_fit_refuses_multi_and_unknown_lineshape():
    da = _cut()
    extracted = extract_edc(da)
    with pytest.raises(PolicyRefusal):
        fit_edc_curve(extracted["curve"], lineshape="doniach", n_peaks=1, guess_fit=lambda *a, **k: None, models=object())
    with pytest.raises(PolicyRefusal):
        fit_edc_curve(extracted["curve"], lineshape="gaussian", n_peaks=2, guess_fit=lambda *a, **k: None, models=object())


def test_fit_uses_injected_package_model():
    da = _cut()
    extracted = extract_edc(da)

    class Param:
        def __init__(self, value):
            self.value = value
            self.stderr = 0.01

    class Result:
        params = {"center": Param(-0.3), "sigma": Param(0.05)}

    class Models:
        GaussianModel = object

    def guess_fit(model, curve):
        assert model is Models.GaussianModel
        assert curve.ndim == 1
        return Result()

    fit = fit_edc_curve(
        extracted["curve"],
        lineshape="gaussian",
        guess_fit=guess_fit,
        models=Models,
    )
    assert fit["lineshape"] == "gaussian"
    assert fit["engine"] == "arpes.fits"
    assert fit["params"]["center"]["value"] == pytest.approx(-0.3)


def test_convert_refuses_quick_report_and_missing_gamma():
    da = _cut()
    with pytest.raises(PolicyRefusal, match="angle-space"):
        prepare_k(da, mode="quick", gamma_method="user", offsets={"phi": 0.1}, energy_label="E-EF")
    with pytest.raises(PolicyRefusal, match="gamma"):
        prepare_k(da, mode="analysis", gamma_method=None, offsets=None, energy_label="E-EF")


def test_convert_refuses_angle_stored_as_kx():
    da = _cut(phi_name="kx", phi_units="deg")
    with pytest.raises(PolicyRefusal, match="momentum"):
        prepare_k(da, mode="analysis", gamma_method="user", offsets={"kx": 0}, energy_label="E-EF")


def test_convert_provisional_cut_writes_provenance(tmp_path):
    da = _cut()

    def convert_fn(data):
        return data.rename({"phi": "kp"})

    result = run_convert(
        da,
        source_path="demo.nc",
        out_dir=tmp_path,
        stem="demo",
        mode="analysis",
        gamma_method="provisional:nearest-0",
        offsets=None,
        energy_label="E-EF",
        ef_fit_eV=0.0,
        ef_fit_source="test",
        convert_fn=convert_fn,
        apply_offsets_fn=lambda data, offsets: data,
        shift_fn=lambda data, energy, ef: data,
    )
    assert result["kspace_provenance"] == "convert_to_kspace"
    assert result["gamma_method"] == "provisional:nearest-0"
    with np.load(result["npz"], allow_pickle=False) as saved:
        assert str(saved["kspace_provenance"]) == "convert_to_kspace"
        assert "intensity" in saved
        assert "gamma_method" in saved


def test_convert_fermi_needs_user_offsets():
    energy = np.linspace(-0.4, 0.05, 6)
    phi = np.linspace(-5, 5, 4)
    psi = np.linspace(-3, 3, 3)
    da = xr.DataArray(
        np.ones((6, 4, 3)),
        coords={"eV": energy, "phi": phi, "psi": psi},
        dims=("eV", "phi", "psi"),
    )
    with pytest.raises(PolicyRefusal, match="Fermi"):
        prepare_k(
            da,
            mode="analysis",
            gamma_method="provisional:nearest-0",
            offsets=None,
            energy_label="E-EF",
        )


def test_convert_source_has_no_k_formula():
    text = (ROOT / "scripts" / "arpes_hotpath" / "convert_k.py").read_text(encoding="utf-8")
    for banned in ("np.sin", "hbar", "0.5124", "sqrt(2"):
        assert banned not in text


def test_load_qc_cli_on_nc(tmp_path):
    path = tmp_path / "cut.nc"
    _write_nc(path, _cut())
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "load_qc.py"),
            str(path),
            "--backend",
            "inspect-only",
            "--allow-inspect",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["energy"]["label"] == "E-EF"
    assert payload["report_momentum"] is False
    assert payload["dims"] == ["eV", "phi"]


def test_load_qc_refuses_silent_inspect(tmp_path):
    path = tmp_path / "cut.nc"
    _write_nc(path, _cut())
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "load_qc.py"),
            str(path),
            "--backend",
            "inspect-only",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["ok"] is False
