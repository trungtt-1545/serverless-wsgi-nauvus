#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import pytest
import serve
import sys
from werkzeug import serving


class ObjectStub:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


@pytest.fixture
def mock_werkzeug(monkeypatch):
    stub = ObjectStub(lastcall=None)

    def mock_serving(host, port, app, **kwargs):
        stub.lastcall = ObjectStub(host=host, port=port, app=app, kwargs=kwargs)

    monkeypatch.setattr(serving, "run_simple", mock_serving)

    return stub


@pytest.fixture
def mock_importlib(monkeypatch):
    app = ObjectStub()
    app.app = ObjectStub()

    def mock_import_module(module):
        if app.app:
            app.app.module = module
        return app

    monkeypatch.setattr(importlib, "import_module", mock_import_module)

    return app


@pytest.fixture
def mock_path(monkeypatch):
    path = []
    monkeypatch.setattr(sys, "path", path)
    return path


def test_serve(mock_path, mock_importlib, mock_werkzeug):
    serve.serve("/tmp1", "app.app", "5000")
    assert len(mock_path) == 1
    assert mock_path[0] == "/tmp1"
    assert mock_werkzeug.lastcall.host == "localhost"
    assert mock_werkzeug.lastcall.port == 5000
    assert mock_werkzeug.lastcall.app.module == "app"
    assert mock_werkzeug.lastcall.app.debug
    assert mock_werkzeug.lastcall.kwargs == {
        "use_reloader": True,
        "use_debugger": True,
        "use_evalex": True,
        "threaded": True,
        "processes": 1,
        "ssl_context": None,
    }


def test_serve_alternative_hostname(mock_path, mock_importlib, mock_werkzeug):
    serve.serve("/tmp1", "app.app", "5000", "0.0.0.0")
    assert len(mock_path) == 1
    assert mock_path[0] == "/tmp1"
    assert mock_werkzeug.lastcall.host == "0.0.0.0"
    assert mock_werkzeug.lastcall.port == 5000
    assert mock_werkzeug.lastcall.app.module == "app"
    assert mock_werkzeug.lastcall.app.debug
    assert mock_werkzeug.lastcall.kwargs == {
        "use_reloader": True,
        "use_debugger": True,
        "use_evalex": True,
        "threaded": True,
        "processes": 1,
        "ssl_context": None,
    }


def test_serve_disable_threading(mock_path, mock_importlib, mock_werkzeug):
    serve.serve("/tmp1", "app.app", "5000", "0.0.0.0", threaded=False)
    assert len(mock_path) == 1
    assert mock_path[0] == "/tmp1"
    assert mock_werkzeug.lastcall.host == "0.0.0.0"
    assert mock_werkzeug.lastcall.port == 5000
    assert mock_werkzeug.lastcall.app.module == "app"
    assert mock_werkzeug.lastcall.app.debug
    assert mock_werkzeug.lastcall.kwargs == {
        "use_reloader": True,
        "use_debugger": True,
        "use_evalex": True,
        "threaded": False,
        "processes": 1,
        "ssl_context": None,
    }


def test_serve_multiple_processes(mock_path, mock_importlib, mock_werkzeug):
    serve.serve("/tmp1", "app.app", "5000", "0.0.0.0", processes=10)
    assert len(mock_path) == 1
    assert mock_path[0] == "/tmp1"
    assert mock_werkzeug.lastcall.host == "0.0.0.0"
    assert mock_werkzeug.lastcall.port == 5000
    assert mock_werkzeug.lastcall.app.module == "app"
    assert mock_werkzeug.lastcall.app.debug
    assert mock_werkzeug.lastcall.kwargs == {
        "use_reloader": True,
        "use_debugger": True,
        "use_evalex": True,
        "threaded": True,
        "processes": 10,
        "ssl_context": None,
    }


def test_serve_ssl(mock_path, mock_importlib, mock_werkzeug):
    serve.serve("/tmp1", "app.app", "5000", "0.0.0.0", threaded=False, ssl=True)
    assert len(mock_path) == 1
    assert mock_path[0] == "/tmp1"
    assert mock_werkzeug.lastcall.host == "0.0.0.0"
    assert mock_werkzeug.lastcall.port == 5000
    assert mock_werkzeug.lastcall.app.module == "app"
    assert mock_werkzeug.lastcall.app.debug
    assert mock_werkzeug.lastcall.kwargs == {
        "use_reloader": True,
        "use_debugger": True,
        "use_evalex": True,
        "threaded": False,
        "processes": 1,
        "ssl_context": "adhoc",
    }


def test_serve_from_subdir(mock_path, mock_importlib, mock_werkzeug):
    serve.serve("/tmp2", "subdir/app.app", "5000")
    assert len(mock_path) == 2
    assert mock_path[0] == "/tmp2/subdir"
    assert mock_path[1] == "/tmp2"
    assert mock_werkzeug.lastcall.host == "localhost"
    assert mock_werkzeug.lastcall.port == 5000
    assert mock_werkzeug.lastcall.app.module == "app"
    assert mock_werkzeug.lastcall.app.debug
    assert mock_werkzeug.lastcall.kwargs == {
        "use_reloader": True,
        "use_debugger": True,
        "use_evalex": True,
        "threaded": True,
        "processes": 1,
        "ssl_context": None,
    }


def test_serve_non_debuggable_app(mock_path, mock_importlib, mock_werkzeug):
    mock_importlib.app = None

    serve.serve("/tmp1", "app.app", "5000")
    assert mock_werkzeug.lastcall.app is None
