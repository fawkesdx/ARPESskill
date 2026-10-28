"""Typed tool handlers. Same functions as scripts/. SKILL.md stays the policy."""

import json
from pathlib import Path

from arpes_hotpath.convert_k import run_convert
from arpes_hotpath.fit_edc import extract_edc, fit_edc_curve
from arpes_hotpath.jsonutil import jsonable
from arpes_hotpath.load import load_spectrum
from arpes_hotpath.manifest import peek_file, write_manifest
from arpes_hotpath.overview import render_overview
from arpes_hotpath.policy import PolicyRefusal

from load_qc import run as load_qc_run


def _loads(text, default=None):
    if text in (None, ""):
        return default
    if isinstance(text, (dict, list)):
        return text
    return json.loads(text)


def state_axes(arguments):
    return load_qc_run(
        arguments["path"],
        arguments["backend"],
        bool(arguments.get("allow_inspect")),
        arguments.get("location"),
    )


def folder_manifest(arguments):
    return write_manifest(arguments["data_root"], arguments["analysis_dir"])


def folder_header_peek(arguments):
    path = Path(arguments["path"])
    if not path.is_file():
        raise PolicyRefusal(f"file not found: {path}")
    peeked = peek_file(path)
    peeked["path"] = str(path)
    peeked["values_read"] = False
    return jsonable(peeked)


def overview_plot(arguments):
    da, used, picked = load_spectrum(
        arguments["path"],
        backend=arguments["backend"],
        allow_inspect=bool(arguments.get("allow_inspect")),
        location=arguments.get("location"),
    )
    da.attrs["backend"] = used
    rendered = render_overview(
        da,
        stem=Path(arguments["path"]).stem,
        out_dir=arguments["out_dir"],
        notes=arguments.get("notes") or "",
    )
    return jsonable(
        {
            "backend": used,
            "picked_variable": picked,
            "kind": rendered["kind"],
            "plots": rendered["plots"],
            "angle_as_k": rendered["axes"]["angle_as_k"],
            "energy": rendered["axes"]["energy"],
            "report_momentum": False,
        }
    )


def extract_curve(arguments):
    da, used, picked = load_spectrum(
        arguments["path"],
        backend=arguments["backend"],
        allow_inspect=bool(arguments.get("allow_inspect")),
        location=arguments.get("location"),
    )
    extracted = extract_edc(da, at=_loads(arguments.get("at_json"), {}))
    return jsonable(
        {
            "backend": used,
            "picked_variable": picked,
            "energy_dim": extracted["energy_dim"],
            "n": extracted["n"],
            "min": extracted["min"],
            "max": extracted["max"],
            "mean": extracted["mean"],
            "curve_values_omitted": True,
        }
    )


def fit_peak(arguments):
    da, used, _picked = load_spectrum(
        arguments["path"],
        backend=arguments["backend"],
        allow_inspect=bool(arguments.get("allow_inspect")),
        location=arguments.get("location"),
    )
    extracted = extract_edc(da, at=_loads(arguments.get("at_json"), {}))
    fit = fit_edc_curve(
        extracted["curve"],
        lineshape=arguments["lineshape"],
        background=arguments.get("background") or "none",
        n_peaks=int(arguments.get("n_peaks") or 1),
    )
    return jsonable({"backend": used, "fit": fit, "n": extracted["n"]})


def convert_k(arguments):
    da, used, _picked = load_spectrum(
        arguments["path"],
        backend=arguments["backend"],
        allow_inspect=bool(arguments.get("allow_inspect")),
        location=arguments.get("location"),
    )
    if used != "pyarpes":
        raise PolicyRefusal("convert_k tool calls PyARPES only. No k formula in the MCP.")
    from arpes_hotpath.convert_k import package_apply_offsets, package_convert, package_shift_ef

    return jsonable(
        run_convert(
            da,
            source_path=arguments["path"],
            out_dir=arguments["out_dir"],
            stem=Path(arguments["path"]).stem,
            mode=arguments.get("mode") or "quick",
            gamma_method=arguments.get("gamma_method"),
            offsets=_loads(arguments.get("offsets_json")),
            energy_label=arguments.get("energy_axis"),
            ef_fit_eV=arguments.get("ef_fit_eV"),
            ef_fit_source="mcp",
            convert_fn=package_convert,
            apply_offsets_fn=package_apply_offsets,
            shift_fn=package_shift_ef,
        )
    )


def shift_energy(arguments):
    """Package shift only. Caller supplies EF_fit from a package edge fit."""
    ef = arguments.get("ef_fit_eV")
    if ef is None:
        raise PolicyRefusal("ef_fit_eV required; this tool does not fit or guess an edge")
    da, used, _picked = load_spectrum(
        arguments["path"],
        backend=arguments["backend"],
        allow_inspect=bool(arguments.get("allow_inspect")),
        location=arguments.get("location"),
    )
    if used != "pyarpes":
        raise PolicyRefusal("shift_energy needs PyARPES S.shift_by. No numeric coord rewrite.")
    from arpes_hotpath.axes import ENERGY_NAMES, find_dim
    from arpes_hotpath.convert_k import package_shift_ef

    energy = find_dim(da, ENERGY_NAMES)
    if energy is None:
        raise PolicyRefusal("no energy dim")
    package_shift_ef(da, energy, float(ef))
    return {
        "ok": True,
        "backend": used,
        "energy_dim": energy,
        "ef_fit_eV": float(ef),
        "shift": {energy: -float(ef)},
        "note": "package S.shift_by only; result not written (pass convert_k to persist)",
    }


TOOL_SPECS = [
    {
        "name": "state_axes",
        "capability_id": "state_axes",
        "description": "Load one spectrum and report dims, units, energy label. Does not call angles momentum.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string", "enum": ["pyarpes", "arpes_viewer", "inspect-only"]},
                "allow_inspect": {"type": "boolean"},
                "location": {"type": "string"},
            },
            "required": ["path", "backend"],
        },
        "handler": state_axes,
    },
    {
        "name": "load_spectrum",
        "capability_id": "load_spectrum",
        "description": "Same QC payload as state_axes. Intensity values are not returned.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string"},
                "allow_inspect": {"type": "boolean"},
                "location": {"type": "string"},
            },
            "required": ["path", "backend"],
        },
        "handler": state_axes,
    },
    {
        "name": "folder_manifest",
        "capability_id": "folder_manifest",
        "description": "Pass B header peek to analysis/manifest.json. Returns counts, not every row.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data_root": {"type": "string"},
                "analysis_dir": {"type": "string"},
            },
            "required": ["data_root", "analysis_dir"],
        },
        "handler": folder_manifest,
    },
    {
        "name": "folder_header_peek",
        "capability_id": "folder_header_peek",
        "description": "Header or shape peek for one file. Does not read a spectrum cube.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
        "handler": folder_header_peek,
    },
    {
        "name": "overview_plot",
        "capability_id": "overview_plot",
        "description": "Default angle-space overview PNGs. Does not convert to k.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string"},
                "out_dir": {"type": "string"},
                "allow_inspect": {"type": "boolean"},
                "location": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["path", "backend", "out_dir"],
        },
        "handler": overview_plot,
    },
    {
        "name": "extract_edc_mdc",
        "capability_id": "extract_edc_mdc",
        "description": "EDC stats at optional fixed coords. Curve values stay out of the reply.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string"},
                "at_json": {"type": "string"},
                "allow_inspect": {"type": "boolean"},
            },
            "required": ["path", "backend"],
        },
        "handler": extract_curve,
    },
    {
        "name": "fit_peak",
        "capability_id": "fit_peak",
        "description": "One package lineshape (gaussian, lorentzian, voigt) on one EDC. N=1 only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string"},
                "lineshape": {"type": "string"},
                "background": {"type": "string"},
                "at_json": {"type": "string"},
                "n_peaks": {"type": "integer"},
                "allow_inspect": {"type": "boolean"},
            },
            "required": ["path", "backend", "lineshape"],
        },
        "handler": fit_peak,
    },
    {
        "name": "convert_k",
        "capability_id": "convert_k",
        "description": "PyARPES convert_to_kspace in analysis mode. Requires gamma method and EF_fit. No k formula.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string"},
                "out_dir": {"type": "string"},
                "mode": {"type": "string"},
                "gamma_method": {"type": "string"},
                "offsets_json": {"type": "string"},
                "energy_axis": {"type": "string"},
                "ef_fit_eV": {"type": "number"},
                "allow_inspect": {"type": "boolean"},
            },
            "required": ["path", "backend", "out_dir"],
        },
        "handler": convert_k,
    },
    {
        "name": "shift_energy",
        "capability_id": "shift_energy",
        "description": "PyARPES S.shift_by by -EF_fit. Does not fit the edge and does not invent the shift.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string"},
                "ef_fit_eV": {"type": "number"},
                "allow_inspect": {"type": "boolean"},
            },
            "required": ["path", "backend", "ef_fit_eV"],
        },
        "handler": shift_energy,
    },
]
